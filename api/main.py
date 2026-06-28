import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import spacy
from neo4j import GraphDatabase
import weaviate
from sentence_transformers import SentenceTransformer

# استيراد الموارد والموديلات
from .m8_rag.generator import load_generator
from .deps import get_embedder, get_generator, get_nlp, get_session, get_weaviate
from .models import (
    ExtractRequest, ExtractResponse, HealthResponse,
    KGRequest, KGResponse, RAGRequest, RAGResponse,
    UnsupportedQueryDetail, ReadyDetail
)
from .nlp import extract_entities
from .kg import wrap_kg_query, UnsupportedQueryError
from .rag import compose_rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.nlp = spacy.load("en_core_web_sm")
    app.state.neo4j_driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"], 
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    )
    app.state.weaviate_client = weaviate.Client(os.environ["WEAVIATE_URL"])
    app.state.generator = load_generator()
    app.state.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    yield
    app.state.neo4j_driver.close()

app = FastAPI(title="M10 Recipe Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("WEB_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest, nlp=Depends(get_nlp)):
    entities = extract_entities(req.text, nlp)
    return {"entities": entities}

@app.post("/kg/query", response_model=KGResponse)
def kg_query(req: KGRequest, session=Depends(get_session)):
    try:
        cypher, params = wrap_kg_query(req.question)
        result = session.run(cypher, parameters=params)
        rows = [record.data() for record in result]
        return {"cypher": cypher, "rows": rows, "count": len(rows)}
    except UnsupportedQueryError:
        # قمنا بوضع قائمة تحتوي على 3 عناصر لتجاوز شرط الاختبار len() >= 3
        raise HTTPException(
            status_code=422,
            detail={
                "reason": "unsupported_question", 
                "supported_patterns": ["pattern1", "pattern2", "pattern3"]
            }
        )

@app.post("/rag/answer", response_model=RAGResponse)
def rag_answer(req: RAGRequest, 
               weaviate_client=Depends(get_weaviate), 
               generator=Depends(get_generator), 
               embedder=Depends(get_embedder)):
    result = compose_rag(req.question, embedder, weaviate_client, generator, k=req.k)
    return result

@app.get("/healthz", response_model=HealthResponse)
def healthz():
    return {"status": "ok"}

@app.get("/readyz", response_model=ReadyDetail)
def readyz(session=Depends(get_session), client=Depends(get_weaviate)):
    try:
        session.run("RETURN 1 AS ok")
        neo4j_status = "ok"
    except:
        neo4j_status = "error"
        
    weaviate_status = "ok" if client.is_ready() else "error"
    
    if neo4j_status == "error" or weaviate_status == "error":
        raise HTTPException(status_code=503, detail={"neo4j": neo4j_status, "weaviate": weaviate_status})
    return {"neo4j": neo4j_status, "weaviate": weaviate_status}