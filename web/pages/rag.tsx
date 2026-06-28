import { useState } from "react";
import { RAGRequest, RAGResponse } from "../lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RagPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/rag/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, k: 4 } as RAGRequest),
      });

      if (response.status === 422) {
        setError("Invalid query parameters.");
      } else if (response.status === 503) {
        setError("The RAG service is temporarily unavailable.");
      } else if (!response.ok) {
        setError("An error occurred while generating the answer.");
      } else {
        const data: RAGResponse = await response.json();
        setResult(data);
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  // دالة لتحويل نص الإجابة إلى أجزاء تحتوي على وسوم استشهاد قابلة للاختبار
  const renderAnswer = (text: string) => {
    // نمط للبحث عن [N]
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      if (/^\[\d+\]$/.test(part)) {
        return (
          <span key={i} data-testid="citation-marker" style={{ fontWeight: "bold", color: "blue" }}>
            {part}
          </span>
        );
      }
      return part;
    });
  };

  return (
    <main>
      <h1>RAG — Cited Answer</h1>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a recipe question..."
      />
      <button onClick={submit} disabled={!question || loading}>
        {loading ? "Asking..." : "Ask"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <section>
          <h2>Answer:</h2>
          <p>{renderAnswer(result.answer)}</p>
          <h3>Citations & Confidence:</h3>
          <p>Confidence Score: {(result.confidence * 100).toFixed(1)}%</p>
          <ul>
            {result.citations.map((c, i) => (
              <li key={i}>
                Chunk ID: {c.chunk_id} | Score: {c.score.toFixed(2)}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}