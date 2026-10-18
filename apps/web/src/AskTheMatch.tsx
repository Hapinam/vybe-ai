import { useRef, useState } from "react";
import { demoMatch, postJson, type Persona } from "./match";

type MatchAnswer = {
  answer: string;
  supported: boolean;
  synthetic: true;
  generation_mode: "deterministic" | "foundry_model_tool_call";
  selected_tool?: string | null;
  evidence_event_ids: string[];
};

const suggestions = [
  "Who scored?",
  "What was the halftime score?",
  "What was the final score?",
  "What happened in the last 15 minutes?",
  "Why did momentum change?",
];

export default function AskTheMatch({ persona }: { persona: Persona }) {
  const [question, setQuestion] = useState(suggestions[0]);
  const [answer, setAnswer] = useState<MatchAnswer | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestId = useRef(0);

  const ask = async (text: string) => {
    const normalized = text.trim();
    if (!normalized || normalized.length > 300) return;
    const id = ++requestId.current;
    setQuestion(normalized);
    setAnswer(null);
    setError("");
    setLoading(true);
    try {
      // Ask about the complete fictional fixture, not the current replay position.
      const response = await postJson<MatchAnswer>("/v1/matches/director/ask", {
        match: demoMatch,
        question: normalized,
        persona,
      });
      if (id === requestId.current) setAnswer(response);
    } catch {
      if (id === requestId.current) setError("Unable to answer right now. Please retry.");
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  };

  return (
    <section className="timeline-section" aria-labelledby="ask-match-title">
      <div className="timeline-title">
        <div>
          <span className="section-label">EVIDENCE-GROUNDED QUESTIONS</span>
          <h2 id="ask-match-title">Ask the Match</h2>
        </div>
        <span className="muted">Synthetic events only</span>
      </div>
      <p className="muted">
        Explore the complete fictional match. Answers use verified events; an optional server-configured model can select a read-only tool.
        Unsupported questions are declined rather than guessed.
      </p>
      <div role="group" aria-label="Suggested match questions" style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", margin: "1rem 0" }}>
        {suggestions.map((suggestion) => (
          <button key={suggestion} type="button" className="secondary"
            disabled={loading} onClick={() => void ask(suggestion)}>{suggestion}</button>
        ))}
      </div>
      <form onSubmit={(event) => { event.preventDefault(); void ask(question); }}
        style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem", alignItems: "center" }}>
        <label htmlFor="ask-match-question">Your question (English)</label>
        <input id="ask-match-question" value={question} maxLength={300}
          onChange={(event) => setQuestion(event.target.value)}
          style={{ flex: "1 1 18rem", minWidth: 0, padding: "0.7rem", borderRadius: "0.5rem" }} />
        <button type="submit" className="primary" disabled={loading || !question.trim()}>
          {loading ? "Checking events…" : "Ask"}
        </button>
      </form>
      <div role="status" aria-live="polite" aria-atomic="true" style={{ marginTop: "1rem" }}>
        {error && <p role="alert">{error}</p>}
        {answer && (
          <div className="insight-card">
            <strong>{answer.supported ? "Verified match answer" : "Not established by the events"}</strong>
            <p>{answer.answer}</p>
            <p className="muted">Source: synthetic event data · {answer.generation_mode === "foundry_model_tool_call" ? "Model-selected tool, deterministic answer" : "Deterministic fallback; no model tool call"}</p>
            {answer.selected_tool && <p className="muted">Selected tool: <code>{answer.selected_tool}</code></p>}
            {answer.evidence_event_ids.length > 0 && (
              <p className="evidence">Evidence event IDs: <code>{answer.evidence_event_ids.join(", ")}</code></p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
