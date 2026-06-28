import re
import numpy as np
from typing import Tuple
from .models import RAGResponse, Citation

PROMPT_TEMPLATE = """\
You are answering a recipe question. Use ONLY the numbered sources below.
Cite each claim with the source number in square brackets, e.g. [1].
If the sources do not contain the answer, say: I cannot answer this from the available sources.

Sources:
{sources}

Question: {question}
Answer:"""

SENTINEL = "I cannot answer this from the available sources"
CITATION_PATTERN = re.compile(r"\[(\d+)\]")

def assemble_prompt(question: str, chunks: list[dict]) -> Tuple[str, dict[int, dict]]:
    sources_text = ""
    numbered = {}
    for i, chunk in enumerate(chunks, 1):
        sources_text += f"[{i}] {chunk['text']}\n"
        numbered[i] = chunk
    prompt = PROMPT_TEMPLATE.format(sources=sources_text, question=question)
    return prompt, numbered

def extract_citations(answer: str, numbered: dict[int, dict]) -> list[dict]:
    found_indices = {int(m.group(1)) for m in CITATION_PATTERN.finditer(answer)}
    citations = []
    for idx in found_indices:
        if idx in numbered:
            chunk = numbered[idx]
            # Score = 1.0 - distance (distance is in _additional field)
            score = 1.0 - chunk.get("_additional", {}).get("distance", 0.0)
            citations.append({"chunk_id": chunk["chunk_id"], "score": max(0.0, min(1.0, score))})
    return citations

def compose_rag(question: str, embedder, weaviate_client, generator, k: int = 4) -> dict:
    # 1. الاسترجاع (Retrieval)
    vector = embedder.encode(question).tolist()
    result = weaviate_client.query.get("Chunk", ["text", "chunk_id"]).with_near_vector(
        {"vector": vector}
    ).with_additional(["distance"]).with_limit(k).do()
    
    chunks = result.get("data", {}).get("Get", {}).get("Chunk", [])
    
    if not chunks:
        return {"answer": SENTINEL, "citations": [], "confidence": 0.0}
    
    # 2. التجميع والتوليد
    prompt, numbered = assemble_prompt(question, chunks)
    
    # التعديل: استدعاء الـ pipeline مباشرة واستخراج النص
    # المولد يعيد قائمة قواميس، نأخذ النص من المفتاح 'generated_text'
    model_output = generator(prompt, do_sample=False, max_new_tokens=256)
    raw_answer = model_output[0]["generated_text"]
    
    # 3. الاستشهاد والتحقق (Grounding)
    citations = extract_citations(raw_answer, numbered)
    
    if not citations:
        return {"answer": SENTINEL, "citations": [], "confidence": 0.0}
    
    # 4. حساب الثقة
    confidence = np.mean([c["score"] for c in citations])
    
    return {
        "answer": raw_answer,
        "citations": citations,
        "confidence": float(confidence)
    }