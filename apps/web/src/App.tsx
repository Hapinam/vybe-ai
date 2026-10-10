import { useEffect, useMemo, useState } from "react";
import { Activity, ArrowRight, AudioLines, BarChart3, CheckCircle2, CircleHelp, Heart, Pause, Play, RotateCcw, ShieldCheck, Sparkles, Volume2, VolumeX } from "lucide-react";
import { demoMatch, formatClock, postJson, type Explanation, type MatchState, type Persona } from "./match";

const personaInfo: Record<Persona, { label: string; subtitle: string }> = {
  young: { label: "Young Fan", subtitle: "Every moment, made simple." },
  accessible: { label: "Accessible", subtitle: "Clear commentary, at your pace." },
  analyst: { label: "Analyst", subtitle: "Facts, context, and evidence." }
};

export default function App() {
  const [step, setStep] = useState(1);
  const [persona, setPersona] = useState<Persona>("young");
  const [playing, setPlaying] = useState(false);
  const [state, setState] = useState<MatchState | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [error, setError] = useState("");
  const [audioEnabled, setAudioEnabled] = useState(false);
  const visibleEvents = useMemo(() => demoMatch.events.slice(0, step), [step]);
  const lastEvent = visibleEvents[visibleEvents.length - 1];
  const latestGoal = [...visibleEvents].reverse().find((event) => event.type === "goal");

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setStep((current) => {
        if (current >= demoMatch.events.length) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, 1900);
    return () => window.clearInterval(timer);
  }, [playing]);

  useEffect(() => {
    let active = true;
    setError("");
    postJson<{ state: MatchState }>("/v1/matches/replay?through_event=" + step, demoMatch)
      .then((result) => { if (active) setState(result.state); })
      .catch((err: unknown) => { if (active) { setState(null); setError(String(err)); } });
    return () => { active = false; };
  }, [step]);

  useEffect(() => {
    let active = true;
    setExplanation(null);
    if (!latestGoal) return;
    postJson<Explanation>(`/v1/matches/narrate/${latestGoal.id}?persona=${persona}`, demoMatch)
      .then((result) => { if (active) setExplanation(result); })
      .catch((err: unknown) => { if (active) setError(String(err)); });
    return () => { active = false; };
  }, [latestGoal?.id, persona]);

  useEffect(() => {
    if (!audioEnabled || persona !== "accessible" || !explanation || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const speech = new SpeechSynthesisUtterance(explanation.narrative);
    speech.rate = 0.9;
    window.speechSynthesis.speak(speech);
    return () => window.speechSynthesis.cancel();
  }, [audioEnabled, persona, explanation]);

  const stopAudio = () => {
    setAudioEnabled(false);
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  };

  return (
    <div className="shell">
      <a href="#main" className="skip-link">Skip to match content</a>
      <header className="topbar">
        <div className="brand"><span className="brand-mark"><Activity size={21} /></span><span>VYBE<span className="brand-dot">.</span></span></div>
        <span className="top-tag">FEEL THE GAME. YOUR WAY.</span>
        <div className="demo-tag"><span className="live-dot" /> SYNTHETIC DEMO</div>
      </header>

      <main id="main">
        <section className="hero">
          <div className="eyebrow"><Sparkles size={15} /> HUMAN-CENTERED FOOTBALL INTELLIGENCE</div>
          <h1>Every fan belongs.<br /><span>Every moment matters.</span></h1>
          <p>One match. Different perspectives. A football experience that adapts to you, not the other way around.</p>
        </section>

        <section className="dashboard" aria-label="Synthetic match dashboard">
          <div className="score-panel">
            <div className="panel-heading"><span className="section-label">MATCH CENTER</span><span className="match-pill">SIMULATED · {formatClock(lastEvent)}</span></div>
            <div className="scoreline">
              <div className="club"><div className="crest aurora">A</div><strong>Aurora FC</strong><span>HOME</span></div>
              <div className="score"><div className="numbers">{state ? `${state.home_score} : ${state.away_score}` : "— : —"}</div><span className="match-status">{lastEvent.type === "fulltime" ? "FULL TIME" : lastEvent.type === "halftime" ? "HALF TIME" : "MATCH PLAYBACK"}</span></div>
              <div className="club"><div className="crest harbor">H</div><strong>Harbor United</strong><span>AWAY</span></div>
            </div>
            <div className="controls">
              <button className="primary" onClick={() => { if (step === demoMatch.events.length) setStep(1); setPlaying((v) => !v); }}><span>{playing ? <Pause size={16} /> : <Play size={16} />}</span>{playing ? "Pause" : step === demoMatch.events.length ? "Replay" : "Play match"}</button>
              <button className="secondary" onClick={() => { setPlaying(false); setStep(1); }}><RotateCcw size={15} /> Restart</button>
              <span className="playback-info">Event {step} of {demoMatch.events.length}</span>
            </div>
            <label className="progress-label" htmlFor="event-progress">Match progress</label>
            <input id="event-progress" className="progress" type="range" min="1" max={demoMatch.events.length} value={step} onChange={(e) => { setPlaying(false); setStep(Number(e.target.value)); }} />
            <div className="stats">
              <div><span>Recorded shots</span><strong>{state ? `${state.shots_home} — ${state.shots_away}` : "—"}</strong></div>
              <div><span>Completed passes</span><strong>{state ? `${state.passes_home} — ${state.passes_away}` : "—"}</strong></div>
              <div><span>Events processed</span><strong>{state?.events_processed ?? "—"}</strong></div>
            </div>
          </div>

          <div className="insight-panel">
            <div className="panel-heading"><span className="section-label">YOUR EXPERIENCE</span><Heart size={18} className="heart" /></div>
            <h2>The game, <em>your way.</em></h2>
            <p className="muted">Choose how you'd like to experience each moment.</p>
            <div className="persona-tabs" role="group" aria-label="Choose commentary experience">
              {(["young", "accessible", "analyst"] as const).map((option) => (
                <button key={option} aria-pressed={persona === option} className={persona === option ? "persona active" : "persona"} onClick={() => { setPersona(option); stopAudio(); }}>
                  {option === "young" ? <Sparkles size={17} /> : option === "accessible" ? <AudioLines size={17} /> : <BarChart3 size={17} />}
                  {personaInfo[option].label}
                </button>
              ))}
            </div>
            <div className="insight-card" aria-live="polite" aria-atomic="true">
              <div className="insight-heading"><span><Sparkles size={16} /> VYBE INSIGHT</span><span className="grounded"><ShieldCheck size={14} /> EVIDENCE-BASED</span></div>
              {explanation && <div className="evidence">{explanation.generation_mode === "azure_ai" ? "Azure AI-selected style · verified factual template" : "Evidence-based commentary · deterministic fallback"}</div>}
              <p className="insight-text">{explanation?.narrative ?? (latestGoal ? "Preparing the latest goal insight…" : "Press play to experience the match. Insights appear when a goal is scored.")}</p>
              {explanation && <div className="evidence"><CheckCircle2 size={15} /> Verified from synthetic event <code>{explanation.evidence_event_ids.join(", ")}</code></div>}
            </div>
            {persona === "accessible" && <button className="audio-toggle" onClick={() => audioEnabled ? stopAudio() : setAudioEnabled(true)} aria-pressed={audioEnabled}>{audioEnabled ? <VolumeX size={18} /> : <Volume2 size={18} />}{audioEnabled ? "Stop spoken commentary" : "Enable spoken commentary"}</button>}
            <div className="trust-note"><CircleHelp size={16} /><span>AI commentary is optional and experimental; automated fact checks are limited. Synthetic match scores come from the deterministic engine.</span></div>
          </div>
        </section>

        <section className="timeline-section">
          <div className="timeline-title"><div><span className="section-label">THE STORY SO FAR</span><h2>Match timeline</h2></div><span className="muted">Only simulated events</span></div>
          <ol className="timeline">
            {[...visibleEvents].reverse().map((event) => <li key={event.id}><span className="event-time">{formatClock(event)}</span><span className={event.type === "goal" ? "event-icon goal-icon" : "event-icon"}>{event.type === "goal" ? "⚽" : event.type === "shot" ? "↗" : event.type === "pass_completed" ? "→" : "•"}</span><div><strong>{event.type === "goal" ? "GOAL!" : event.type.replace("_", " ").toUpperCase()}</strong><p>{event.team ?? "Match official"}{event.player ? ` · ${event.player}` : ""}</p></div>{event.type === "goal" && <span className="goal-label">KEY MOMENT</span>}</li>)}
          </ol>
        </section>
        {error && <div className="error" role="alert">Backend connection issue: {error}. Start the FastAPI server on port 8000.</div>}
      </main>
      <footer><div className="brand small"><Activity size={17} /> VYBE.</div><span>Built for every kind of fan. Synthetic match data only.</span><span>POWERED BY HUMAN CONNECTION <ArrowRight size={15} /></span></footer>
    </div>
  );
}
