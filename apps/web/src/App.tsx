import { useEffect, useMemo, useRef, useState } from "react";
import { Activity, ArrowRight, AudioLines, BarChart3, CheckCircle2, CircleHelp, Heart, Pause, Play, RotateCcw, ShieldCheck, Sparkles, Volume2, VolumeX } from "lucide-react";
import { demoMatch, formatClock, postJson, type Explanation, type MatchState, type Persona } from "./match";

type PlaybackSpeed = 1 | 2 | 4;

const personaInfo: Record<Persona, { label: string; subtitle: string }> = {
  young: { label: "Young Fan", subtitle: "Every moment, made simple." },
  accessible: { label: "Accessible", subtitle: "Clear commentary, at your pace." },
  analyst: { label: "Analyst", subtitle: "Facts, context, and evidence." }
};

export default function App() {
  const [step, setStep] = useState(1);
  const [persona, setPersona] = useState<Persona>("young");
  const [playing, setPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(2);
  const [state, setState] = useState<MatchState | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [error, setError] = useState("");
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [speechRate, setSpeechRate] = useState(0.9);
  const [audioPaused, setAudioPaused] = useState(false);
  const [narrating, setNarrating] = useState(false);
  const speechQueue = useRef<string[]>([]);
  const speechActive = useRef(false);
  const speechRateRef = useRef(speechRate);
  const spokenGoalIds = useRef<Set<string>>(new Set());
  speechRateRef.current = speechRate;

  const speakNext = () => {
    if (speechActive.current || speechQueue.current.length === 0 || !("speechSynthesis" in window)) return;
    const narrative = speechQueue.current.shift();
    if (!narrative) return;
    speechActive.current = true;
    setNarrating(true);
    const utterance = new SpeechSynthesisUtterance(narrative);
    utterance.rate = speechRateRef.current;
    const finish = () => { speechActive.current = false; setNarrating(false); speakNext(); };
    utterance.onend = finish;
    utterance.onerror = finish;
    window.speechSynthesis.speak(utterance);
  };
  const visibleEvents = useMemo(() => demoMatch.events.slice(0, step), [step]);
  const lastEvent = visibleEvents[visibleEvents.length - 1];
  const latestGoal = [...visibleEvents].reverse().find((event) => event.type === "goal");

  useEffect(() => {
    if (!playing || (audioEnabled && persona === "accessible" && (narrating || (lastEvent.type === "goal" && !spokenGoalIds.current.has(lastEvent.id))))) return;
    const timer = window.setInterval(() => {
      setStep((current) => {
        if (current >= demoMatch.events.length) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, 1900 / playbackSpeed);
    return () => window.clearInterval(timer);
  }, [playing, playbackSpeed, audioEnabled, persona, narrating, step]);

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
    if (!audioEnabled || persona !== "accessible" || !explanation || !latestGoal || !("speechSynthesis" in window)) return;
    if (spokenGoalIds.current.has(latestGoal.id)) return;
    spokenGoalIds.current.add(latestGoal.id);
    speechQueue.current.push(explanation.narrative);
    speakNext();
  }, [audioEnabled, persona, explanation, latestGoal?.id]);

  const stopAudio = () => {
    setAudioEnabled(false);
    setAudioPaused(false);
    speechQueue.current = [];
    speechActive.current = false;
    setNarrating(false);
    spokenGoalIds.current.clear();
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
              <button className="primary" onClick={() => { if (playing) { setPlaying(false); if (audioEnabled && persona === "accessible" && "speechSynthesis" in window) { window.speechSynthesis.pause(); setAudioPaused(true); } } else { if (step === demoMatch.events.length) { stopAudio(); setStep(1); } else if (audioPaused && "speechSynthesis" in window) { window.speechSynthesis.resume(); setAudioPaused(false); } setPlaying(true); } }}><span>{playing ? <Pause size={16} /> : <Play size={16} />}</span>{playing ? "Pause" : step === demoMatch.events.length ? "Replay" : "Play match"}</button>
              <button className="secondary" onClick={() => { setPlaying(false); stopAudio(); setStep(1); }}><RotateCcw size={15} /> Restart</button>
              <span className="playback-info">Event {step} of {demoMatch.events.length}</span>
            </div>
            <div className="playback-speed" style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap", margin: "0.9rem 0" }}>
              <label htmlFor="playback-speed" className="progress-label">Playback speed</label>
              <select id="playback-speed" value={playbackSpeed} onChange={(event) => setPlaybackSpeed(Number(event.target.value) as PlaybackSpeed)} style={{ color: "inherit", background: "#25243e", border: "1px solid #8171bc", borderRadius: "0.5rem", padding: "0.45rem 0.65rem", font: "inherit" }}>
                <option value={1}>1× · Relaxed</option>
                <option value={2}>2× · Default</option>
                <option value={4}>4× · Fast</option>
              </select>
              <button type="button" className="secondary" onClick={() => { setPlaying(false); stopAudio(); setStep(demoMatch.events.length); }} aria-label="Jump instantly to full time">Instant · Full time</button>
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
            {persona === "accessible" && <div role="group" aria-label="Spoken commentary controls">
              <button type="button" className="audio-toggle" onClick={() => audioEnabled ? stopAudio() : (spokenGoalIds.current.clear(), setAudioEnabled(true))} aria-pressed={audioEnabled}>{audioEnabled ? <VolumeX size={18} /> : <Volume2 size={18} />}{audioEnabled ? "Stop spoken commentary" : "Enable spoken commentary"}</button>
              {audioEnabled && <button type="button" className="audio-toggle" onClick={() => { if (!("speechSynthesis" in window)) return; if (audioPaused) { window.speechSynthesis.resume(); setAudioPaused(false); } else { window.speechSynthesis.pause(); setAudioPaused(true); } }} aria-pressed={audioPaused}>{audioPaused ? <Play size={18} /> : <Pause size={18} />}{audioPaused ? "Resume commentary" : "Pause commentary"}</button>}
              <label htmlFor="speech-rate" className="progress-label">Commentary voice speed</label>
              <select id="speech-rate" value={speechRate} onChange={(event) => setSpeechRate(Number(event.target.value))} style={{ color: "inherit", background: "#25243e", border: "1px solid #8171bc", borderRadius: "0.5rem", padding: "0.45rem 0.65rem", margin: "0.5rem", font: "inherit" }}>
                <option value={0.75}>0.75× · Slower</option>
                <option value={0.9}>0.9× · Default</option>
                <option value={1}>1× · Normal</option>
                <option value={1.25}>1.25× · Faster</option>
              </select>
            </div>}
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
