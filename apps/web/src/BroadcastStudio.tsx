import { useEffect, useMemo, useState } from "react";
import { demoMatch, formatClock, postJson, type Persona } from "./match";

type Insight = {
  event_id: string;
  headline: string;
  explanation: string;
  impact: string;
  evidence_event_ids: string[];
  score_after: { home: number; away: number };
};
type InsightsResponse = {
  persona: Persona;
  recap: string;
  recap_evidence_event_ids: string[];
  insights: Insight[];
  score: { home: number; away: number };
  generation_mode: "deterministic";
  synthetic: true;
};

const modes: { id: Persona; title: string; subtitle: string }[] = [
  { id: "young", title: "Young Fan", subtitle: "Simple and exciting" },
  { id: "accessible", title: "Accessible", subtitle: "Clear and descriptive" },
  { id: "analyst", title: "Analyst", subtitle: "Scoreboard impact and evidence" },
];

export default function BroadcastStudio({
  persona, onPersonaChange, playedEventIds, onJumpToEvent, retryCount
}: {
  persona: Persona;
  onPersonaChange: (persona: Persona) => void;
  playedEventIds: string[];
  onJumpToEvent: (eventId: string) => void;
  retryCount: number;
}) {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const played = useMemo(() => new Set(playedEventIds), [playedEventIds]);
  useEffect(() => {
    const controller = new AbortController();
    // postJson handles its own timeout; the active flag guards stale persona responses.
    let active = true;
    setLoading(true);
    setError(false);
    setData(null);
    postJson<InsightsResponse>(`/v1/matches/insights?persona=${persona}`, demoMatch)
      .then(result => {
        if (!active || controller.signal.aborted) return;
        const valid = new Set(demoMatch.events.map(event => event.id));
        if (result.persona !== persona || !result.synthetic ||
            result.generation_mode !== "deterministic" ||
            result.insights.some(item => !valid.has(item.event_id) ||
              item.evidence_event_ids.some(id => !valid.has(id)))) {
          throw new Error("Unexpected insight response");
        }
        setData(result);
      })
      .catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; controller.abort(); };
  }, [persona, retryCount]);

  const fulltimePlayed = demoMatch.events.some(event => event.type === "fulltime" && played.has(event.id));
  const available = data?.insights.filter(item => played.has(item.event_id)) ?? [];
  const current = available.find(item => item.event_id === selectedEventId) ?? available[available.length - 1];
  const evidence = current?.evidence_event_ids.map(id => demoMatch.events.find(event => event.id === id)).filter(
    (event): event is (typeof demoMatch.events)[number] => Boolean(event)
  ) ?? [];
  return (
    <section className="studio" aria-labelledby="studio-title">
      <div className="studio-header">
        <div>
          <span className="section-label">BROADCAST STUDIO · SYNTHETIC MATCH</span>
          <h2 id="studio-title">AI Match Director <span className="studio-muted">Studio</span></h2>
          <p className="studio-muted">One match. Three fan experiences. Every claim traceable to an event.</p>
        </div>
        <span className="studio-pill">Evidence-grounded · deterministic</span>
      </div>
      <div className="studio-modes" role="group" aria-label="Studio audience">
        {modes.map(mode => <button type="button" key={mode.id}
          aria-pressed={persona === mode.id} className={persona === mode.id ? "studio-mode active" : "studio-mode"}
          onClick={() => onPersonaChange(mode.id)}>
          <strong>{mode.title}</strong><span>{mode.subtitle}</span>
        </button>)}
      </div>
      {loading && <p role="status" className="studio-muted">Preparing verified match insights…</p>}
      {error && <p role="alert">Studio insights are temporarily unavailable. The original match replay still works.</p>}
      {data && <div className="studio-layout">
        <div className="studio-main">
          <div className="studio-score" aria-label="Recorded match score">
            <span>{demoMatch.home_team}</span><strong>{current ? current.score_after.home : 0} : {current ? current.score_after.away : 0}</strong><span>{demoMatch.away_team}</span>
          </div>
          <p className="studio-muted">Score at the selected recorded moment · not a live football feed</p>
          {current ? <>
            <span className="section-label">DIRECTOR'S MOMENT</span>
            <h3>{current.headline}</h3>
            <p className="studio-explanation">{current.explanation}</p>
            <div className="studio-evidence">
              <strong>Verified evidence</strong>
              {evidence.map(event => <button type="button" className="studio-evidence-link" key={event.id}
                onClick={() => onJumpToEvent(event.id)}>
                {event.id} · {formatClock(event)} · {event.team ?? "Match event"}
              </button>)}
            </div>
          </> : <p>No recorded goals have played yet. Press Play to reveal verified moments.</p>}
        </div>
        <aside className="studio-side" aria-label="Director's moments">
          <h3>Match director's picks</h3>
          <p className="studio-muted">Recorded goals only · choose a moment</p>
          {available.map(item => <button type="button" key={item.event_id}
            className={current?.event_id === item.event_id ? "studio-pick selected" : "studio-pick"}
            aria-pressed={current?.event_id === item.event_id}
            onClick={() => setSelectedEventId(item.event_id)}>
            <span>{item.headline}</span><small>{item.impact.replaceAll("_", " ")} · {item.event_id}</small>
          </button>)}
          {!available.length && <p className="studio-muted">No goal moments available yet.</p>}
          <h3>Match recap</h3>
          {fulltimePlayed ? <>
            <p>{data.recap}</p>
            <small className="studio-muted">Full-fixture recap · Event evidence: {data.recap_evidence_event_ids.join(", ") || "none"}</small>
          </> : <p className="studio-muted" role="status">Full match recap unlocks after the final whistle. Keep watching for verified moments.</p>}
        </aside>
      </div>}
      <p className="studio-disclaimer">Studio insights are deterministic, not AI-generated commentary. Model-based tool selection is optional in Ask the Match and is only active when configured on the server.</p>
    </section>
  );
}
