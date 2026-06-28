import { useState } from "react";
import { ExtractRequest, ExtractResponse } from "../lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ExtractPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<ExtractResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text } as ExtractRequest),
      });

      if (response.status === 422) {
        setError("Invalid input: Please check your text length.");
      } else if (response.status === 503) {
        setError("Service is currently unavailable. Please try again later.");
      } else if (!response.ok) {
        setError("An unexpected error occurred.");
      } else {
        const data: ExtractResponse = await response.json();
        setResult(data);
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    }
  }

  return (
    <main>
      <h1>Extract — Named Entity Recognition</h1>
      <textarea 
        value={text} 
        onChange={(e) => setText(e.target.value)} 
        placeholder="Enter text to extract entities..."
      />
      <button onClick={submit} disabled={!text}>Extract</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <section>
          <h2>Entities:</h2>
          {result.entities.map((ent, i) => (
            <span 
              key={i} 
              data-testid="entity-span" 
              style={{ margin: "5px", padding: "5px", border: "1px solid #ccc" }}
            >
              {ent.text} ({ent.label})
            </span>
          ))}
        </section>
      )}
    </main>
  );
}