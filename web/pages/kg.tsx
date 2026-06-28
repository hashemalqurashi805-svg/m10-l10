import { useState } from "react";
import { KGRequest, KGResponse } from "../lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function KgPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<KGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [supportedPatterns, setSupportedPatterns] = useState<string[]>([]);

  async function submit() {
    setError(null);
    setResult(null);
    setSupportedPatterns([]);

    try {
      const response = await fetch(`${API_URL}/kg/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question } as KGRequest),
      });

      const data = await response.json();

      if (response.status === 422) {
        setError("Unsupported question format.");
        setSupportedPatterns(data.detail.supported_patterns || []);
      } else if (!response.ok) {
        setError("An error occurred while querying the knowledge graph.");
      } else {
        setResult(data as KGResponse);
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    }
  }

  return (
    <main>
      <h1>Knowledge Graph — Recipe Query</h1>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="e.g. Find Sichuan recipes"
      />
      <button onClick={submit} disabled={!question}>Ask</button>

      {error && (
        <section style={{ color: "red" }}>
          <p>{error}</p>
          {supportedPatterns.length > 0 && (
            <ul>
              {supportedPatterns.map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          )}
        </section>
      )}

      {result && (
        <section>
          <h3>Cypher Query:</h3>
          <pre>{result.cypher}</pre>
          <h3>Results:</h3>
          <table border={1}>
            <tbody>
              {result.rows.map((row, i) => (
                <tr key={i} data-testid="kg-row">
                  {Object.values(row).map((val: any, j) => (
                    <td key={j}>{JSON.stringify(val)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  );
}