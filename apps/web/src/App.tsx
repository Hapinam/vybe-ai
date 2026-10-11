import { useEffect, useMemo, useRef, useState } from "react";
import { Activity, ArrowRight, AudioLines, BarChart3, CheckCircle2, CircleHelp, Heart, Pause, Play, RotateCcw, ShieldCheck, Sparkles, Volume2, VolumeX } from "lucide-react";
import { demoMatch, formatClock, postJson, type Explanation, type MatchState, type Persona } from "./match";
import { eventCaption, languageNames, matchRecap, spokenMatchIntro, spokenMatchOutro, type FanLanguage } from "./localization";

type PlaybackSpeed = 1 | 2 | 4;

const personaInfo: Record<Persona, { label: string; subtitle: string }> = {
  young: { label: "Young Fan", subtitle: "Every moment, made simple." },
  accessible: { label: "Accessible", subtitle: "Clear commentary, at your pace." },
  analyst: { label: "Analyst", subtitle: "Facts, context, and evidence." }
};

export default function App() {
  const [step, setStep] = useState(1);
  const [persona, setPersona] = useState<Persona>(() => { const v=localStorage.getItem("vybe.persona"); return v==="young"||v==="accessible"||v==="analyst"?v:"young"; });
  const [language, setLanguage] = useState<FanLanguage>(() => { const v=localStorage.getItem("vybe.language"); return v==="ar"||v==="cs"?v:"en"; });
  const [captionsEnabled, setCaptionsEnabled] = useState(() => localStorage.getItem("vybe.captions")!=="false");
  const [demoMode, setDemoMode] = useState(false);
  const demoModeRef = useRef(false);
  const [selectedWindow, setSelectedWindow] = useState<number|null>(null);
  const [playing, setPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(2);
  const [state, setState] = useState<MatchState | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [error, setError] = useState("");
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [highContrast, setHighContrast] = useState(() => localStorage.getItem("vybe.contrast")==="true");
  const [largeText, setLargeText] = useState(() => localStorage.getItem("vybe.largeText")==="true");
  const [expandedAudio, setExpandedAudio] = useState(() => localStorage.getItem("vybe.expandedAudio")==="true");
  const [quizAnswer, setQuizAnswer] = useState<string | null>(null);
  const [timelineFilter, setTimelineFilter] = useState<"all" | "highlights">(() => localStorage.getItem("vybe.timeline")==="all"?"all":"highlights");
  const [showEventDetails, setShowEventDetails] = useState(() => localStorage.getItem("vybe.details")!=="false");
  const [speechRate, setSpeechRate] = useState(() => { const n=Number(localStorage.getItem("vybe.speechRate")); return [0.5,1,1.5,2].includes(n)?n:1; });
  const [audioPaused, setAudioPaused] = useState(false);
  const [narrating, setNarrating] = useState(false);
  const speechQueue = useRef<string[]>([]);
  const speechActive = useRef(false);
  const speechRateRef = useRef(speechRate);
  const spokenGoalIds = useRef<Set<string>>(new Set());
  const spokenEventIds = useRef<Set<string>>(new Set());
  const previewSpeech = useRef<SpeechSynthesisUtterance | null>(null);
  const introStarted = useRef(false);
  const outroStarted = useRef(false);
  speechRateRef.current = speechRate;

  const speakNext = () => {
    if (speechActive.current || speechQueue.current.length === 0 || !("speechSynthesis" in window)) return;
    const narrative = speechQueue.current.shift();
    if (!narrative) return;
    speechActive.current = true;
    setNarrating(true);
    // A single utterance avoids dropped words at sentence boundaries.
    // Browser speech engines apply rate when an utterance starts.
    const utterance = new SpeechSynthesisUtterance(narrative);
    utterance.rate = speechRateRef.current;
    utterance.lang = language==="ar"?"ar":language==="cs"?"cs-CZ":"en-US";
    const finish = () => {
      if (!speechActive.current) return;
      speechActive.current = false;
      setNarrating(false);
      speakNext();
    };
    utterance.onend = finish;
    utterance.onerror = finish;
    window.speechSynthesis.speak(utterance);
  };
  useEffect(() => { localStorage.setItem("vybe.persona",persona); },[persona]);
  useEffect(() => { localStorage.setItem("vybe.language",language); },[language]);
  useEffect(() => { localStorage.setItem("vybe.contrast",String(highContrast)); },[highContrast]);
  useEffect(() => { localStorage.setItem("vybe.largeText",String(largeText)); },[largeText]);
  useEffect(() => { localStorage.setItem("vybe.captions",String(captionsEnabled)); },[captionsEnabled]);
  useEffect(() => { localStorage.setItem("vybe.timeline",timelineFilter); },[timelineFilter]);
  useEffect(() => { localStorage.setItem("vybe.details",String(showEventDetails)); },[showEventDetails]);
  useEffect(() => { localStorage.setItem("vybe.speechRate",String(speechRate)); },[speechRate]);
  useEffect(() => { localStorage.setItem("vybe.expandedAudio",String(expandedAudio)); },[expandedAudio]);
  useEffect(() => {
    demoModeRef.current=demoMode;
    if(!demoMode) return;
    setPlaying(false);
    const stages:[Persona,number][]=[["young",4],["accessible",18],["analyst",29]];
    let index=0;
    const show=()=>{if(!demoModeRef.current)return;const [p,s]=stages[index];setPersona(p);setStep(s);index++;};
    show();
    const timer=window.setInterval(()=>{if(index<stages.length)show();else {window.clearInterval(timer);setDemoMode(false);}},7000);
    return ()=>{demoModeRef.current=false;window.clearInterval(timer);};
  },[demoMode]);
  useEffect(() => {
    if (!demoMode || persona !== "accessible" || !("speechSynthesis" in window)) return;
    const utterance = new SpeechSynthesisUtterance(
      language === "cs" ? "Vítejte ve VYBE. Aurora FC hraje proti Harbor United." :
      language === "ar" ? "أهلًا بكم في فايب. أورورا إف سي يواجه هاربور يونايتد." :
      "Welcome to VYBE. Aurora FC faces Harbor United."
    );
    utterance.lang = language === "cs" ? "cs-CZ" : language === "ar" ? "ar-EG" : "en-US";
    utterance.rate = speechRateRef.current;
    window.speechSynthesis.speak(utterance);
    return () => window.speechSynthesis.cancel();
  }, [demoMode, persona, language]);
  const visibleEvents = useMemo(() => demoMatch.events.slice(0, step), [step]);
  const lastEvent = visibleEvents[visibleEvents.length - 1];
  const latestGoal = [...visibleEvents].reverse().find((event) => event.type === "goal");
  const timelineEvents = (timelineFilter === "highlights" ? visibleEvents.filter(event => event.type !== "pass_completed") : visibleEvents).filter(event=>selectedWindow===null || (event.minute>=selectedWindow*15 && event.minute<(selectedWindow+1)*15));
  useEffect(() => { setQuizAnswer(null); }, [latestGoal?.id]);
  const celebratingGoal = persona === "young" && lastEvent.type === "goal" ? lastEvent : null;
  const currentCaption=eventCaption(lastEvent,language,persona);
  const recap=matchRecap(visibleEvents,language,persona);
  const glossary: Record<string,string> = {goal:"A goal means the ball went into the net!",shot:"A shot is an attempt to score.",pass_completed:"A completed pass reaches a teammate.",kickoff:"Kickoff begins the match.",halftime:"Half-time is the break.",fulltime:"Full-time ends the match."};
  const statsForHalf = (start:number,end:number) => {
    const events=visibleEvents.filter(e=>e.minute>=start&&e.minute<end);
    const count=(type:string,team:string)=>events.filter(e=>e.type===type&&e.team===team).length;
    return {goals:[count("goal",demoMatch.home_team),count("goal",demoMatch.away_team)],shots:[count("shot",demoMatch.home_team)+count("goal",demoMatch.home_team),count("shot",demoMatch.away_team)+count("goal",demoMatch.away_team)],passes:[count("pass_completed",demoMatch.home_team),count("pass_completed",demoMatch.away_team)]};
  };
  const firstHalf=statsForHalf(0,45), secondHalf=statsForHalf(45,91);
  const momentum=Array.from({length:6},(_,i)=>{
    const events=visibleEvents.filter(e=>e.minute>=i*15&&e.minute<(i+1)*15);
    const points=(team:string)=>events.filter(e=>e.team===team).reduce((sum,e)=>sum+(e.type==="goal"?3:e.type==="shot"?2:e.type==="pass_completed"?1:0),0);
    return {label:String(i*15)+"–"+String((i+1)*15),home:points(demoMatch.home_team),away:points(demoMatch.away_team)};
  });
  const turningPoints=visibleEvents.filter(e=>e.type==="goal" && (selectedWindow===null || (e.minute>=selectedWindow*15 && e.minute<(selectedWindow+1)*15))).map(e=>{ const prior=visibleEvents.filter(x=>x.type==="goal" && (x.minute<e.minute || (x.minute===e.minute && (x.second??0)<(e.second??0)))); const home=prior.filter(x=>x.team===demoMatch.home_team).length; const away=prior.filter(x=>x.team===demoMatch.away_team).length; const nextHome=home+(e.team===demoMatch.home_team?1:0); const nextAway=away+(e.team===demoMatch.away_team?1:0); const change=nextHome===nextAway?"Equalizer":(home===away?"Took the lead":(Math.sign(home-away)!==Math.sign(nextHome-nextAway)?"Lead changed":"Extended the lead")); return {event:e,change,score:String(nextHome)+"–"+String(nextAway)}; });

  useEffect(() => {
    if (!playing || !audioEnabled || persona !== "accessible" || step !== 1 || introStarted.current || !("speechSynthesis" in window)) return;
    introStarted.current = true;
    speechQueue.current.push(spokenMatchIntro(language));
    speakNext();
  }, [playing, audioEnabled, persona, step, language]);

  useEffect(() => {
    if (!playing || !audioEnabled || persona !== "accessible" || lastEvent.type !== "fulltime" || outroStarted.current || !("speechSynthesis" in window)) return;
    outroStarted.current = true;
    const goals = visibleEvents.filter(event => event.type === "goal");
    const home = goals.filter(event => event.team === demoMatch.home_team).length;
    const away = goals.filter(event => event.team === demoMatch.away_team).length;
    speechQueue.current.push(spokenMatchOutro(language, home, away));
    speakNext();
    setPlaying(false);
  }, [playing, audioEnabled, persona, step, language]);

  useEffect(() => {
    if (!playing || (audioEnabled && persona === "accessible" && (narrating || audioPaused || (step === 1 && !introStarted.current) || (lastEvent.type === "goal" && !spokenGoalIds.current.has(lastEvent.id))))) return;
    const timer = window.setInterval(() => {
      setStep((current) => {
        if (current >= demoMatch.events.length) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, (1900 * 9) / (demoMatch.events.length * playbackSpeed));
    return () => window.clearInterval(timer);
  }, [playing, playbackSpeed, audioEnabled, persona, narrating, audioPaused, step]);

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
    if (!audioEnabled || !playing || persona !== "accessible" || !explanation || !latestGoal || lastEvent.type !== "goal" || lastEvent.id !== latestGoal.id || !("speechSynthesis" in window)) return;
    if (!explanation.evidence_event_ids.includes(latestGoal.id)) return;
    if (spokenGoalIds.current.has(latestGoal.id)) return;
    spokenGoalIds.current.add(latestGoal.id);
    speechQueue.current.push(language==="en"?explanation.narrative:eventCaption(latestGoal,language,persona));
    speakNext();
  }, [audioEnabled, playing, persona, explanation, latestGoal?.id, step, language]);

  useEffect(() => {
    if (!expandedAudio || !audioEnabled || !playing || persona !== "accessible" || !("speechSynthesis" in window)) return;
    if (lastEvent.type !== "shot" && lastEvent.type !== "pass_completed") return;
    if (spokenEventIds.current.has(lastEvent.id)) return;
    spokenEventIds.current.add(lastEvent.id);
    speechQueue.current.push(eventCaption(lastEvent,language,persona));
    speakNext();
  }, [expandedAudio,audioEnabled,playing,persona,step,language]);
  useEffect(() => {
    const onKey=(event:KeyboardEvent)=>{
      if(persona!=="accessible"||event.altKey||event.ctrlKey||event.metaKey)return;
      const target=event.target as HTMLElement|null;
      if(target?.closest("button,input,select,textarea,a,[contenteditable]"))return;
      if(event.code==="Space"){event.preventDefault();if(audioEnabled && "speechSynthesis" in window){if(playing){window.speechSynthesis.pause();setAudioPaused(true);}else if(audioPaused){window.speechSynthesis.resume();setAudioPaused(false);}}setPlaying(v=>!v);}
      if(event.code==="ArrowRight"){event.preventDefault();setPlaying(false);if(audioEnabled && "speechSynthesis" in window){window.speechSynthesis.cancel();speechQueue.current=[];speechActive.current=false;setNarrating(false);setAudioPaused(false);}setStep(v=>Math.min(demoMatch.events.length,v+1));}
      if(event.code==="ArrowLeft"){event.preventDefault();setPlaying(false);if(audioEnabled && "speechSynthesis" in window){window.speechSynthesis.cancel();speechQueue.current=[];speechActive.current=false;setNarrating(false);setAudioPaused(false);}setStep(v=>Math.max(1,v-1));}
    };
    window.addEventListener("keydown",onKey);
    return ()=>window.removeEventListener("keydown",onKey);
  },[persona,playing,audioEnabled,audioPaused]);
  const stopAudio = () => {
    setAudioEnabled(false);
    setAudioPaused(false);
    speechQueue.current = [];
    speechActive.current = false;
    setNarrating(false);
    spokenGoalIds.current.clear();
    spokenEventIds.current.clear();
    introStarted.current = false;
    outroStarted.current = false;
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    previewSpeech.current = null;
  };

  return (
    <div className={"shell"+(highContrast&&persona==="accessible"?" high-contrast":"")+(largeText&&persona==="accessible"?" large-text":"")}>
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
            <div className="fan-settings" role="group" aria-label="Fan preferences">
              <label htmlFor="fan-language">Commentary language</label>
              <select id="fan-language" value={language} onChange={e=>{stopAudio();setLanguage(e.target.value as FanLanguage);}}>
                {(Object.keys(languageNames) as FanLanguage[]).map(key=><option key={key} value={key}>{languageNames[key]}</option>)}
              </select>
              <label className="access-choice"><input type="checkbox" checked={captionsEnabled} onChange={e=>setCaptionsEnabled(e.target.checked)}/> Live captions</label>
              <button type="button" className="secondary" onClick={()=>{stopAudio();setDemoMode(v=>!v);}}>{demoMode?"Stop demo":"Guided demo · 21 sec"}</button>
            </div>
            {captionsEnabled && <div className="live-caption" role="status" aria-live="polite" dir={language==="ar"?"rtl":"ltr"}><strong>LIVE CAPTIONS · {languageNames[language]}</strong><p>{currentCaption}</p></div>}
            <div className="controls">
              <button className="primary" onClick={() => { if (playing) { setPlaying(false); if (audioEnabled && persona === "accessible" && "speechSynthesis" in window && window.speechSynthesis.speaking) { window.speechSynthesis.pause(); setAudioPaused(true); } else { setAudioPaused(false); } } else { if (step === demoMatch.events.length) { stopAudio(); setStep(1); } else if (audioPaused && "speechSynthesis" in window) { if (window.speechSynthesis.speaking && window.speechSynthesis.paused) { window.speechSynthesis.resume(); } else { window.speechSynthesis.cancel(); speechActive.current = false; setNarrating(false); } setAudioPaused(false); } setPlaying(true); } }}><span>{playing ? <Pause size={16} /> : <Play size={16} />}</span>{playing ? "Pause" : step === demoMatch.events.length ? "Replay" : "Play match"}</button>
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
            <input id="event-progress" className="progress" type="range" min="1" max={demoMatch.events.length} value={step} onChange={(e) => { setPlaying(false); if(audioEnabled)stopAudio(); setStep(Number(e.target.value)); }} />
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
            {celebratingGoal && (
              <div role="status" aria-live="polite" aria-label="Goal celebration" style={{ margin: "1rem 0", padding: "1.25rem", borderRadius: "1rem", border: "2px solid #fbbf24", background: "linear-gradient(135deg, #403068, #2a2348)", textAlign: "center" }}>
                <div aria-hidden="true" style={{ fontSize: "2rem" }}>⚽ 🎉 ⭐</div>
                <strong style={{ display: "block", fontSize: "1.65rem", margin: "0.4rem 0" }}>GOOOAL!</strong>
                <p style={{ margin: "0.25rem 0" }}>{celebratingGoal.player ?? "A player"} scores for {celebratingGoal.team ?? "their team"}!</p>
                <span style={{ fontWeight: 700 }}>Minute {formatClock(celebratingGoal)} · What a moment!</span>
              </div>
            )}
            {persona==="young" && <div className="persona-extra">
              <strong>Football words explained</strong><p>{glossary[lastEvent.type]}</p>
              {latestGoal && <div className="young-quiz" aria-label="Football mini quiz">
                <h3>Mini football quiz</h3>
                <p>Which team scored the goal at {formatClock(latestGoal)}?</p>
                <div className="quiz-options">{[demoMatch.home_team, demoMatch.away_team].map(team => <button type="button" className="secondary" key={team} disabled={quizAnswer !== null} onClick={() => setQuizAnswer(team)}>{team}</button>)}</div>
                {quizAnswer !== null && <p role="status">{quizAnswer === latestGoal.team ? "Correct! Great football knowledge!" : "Good try! It was " + latestGoal.team + "."}</p>}
              </div>}
            </div>}
            {persona==="analyst" && <div className="persona-extra">
              <h3>First half vs second half</h3><p className="muted">Home–Away counts; recorded shots include goals.</p>
              <table className="analysis-table"><thead><tr><th>Recorded events</th><th>First</th><th>Second</th></tr></thead><tbody>
                {(["goals","shots","passes"] as const).map(key=><tr key={key}><th>{key}</th><td>{firstHalf[key].join("–")}</td><td>{secondHalf[key].join("–")}</td></tr>)}
              </tbody></table>
              <h3>Match momentum</h3><p className="muted">Weighted event activity: goal 3, shot 2, pass 1. Not possession or xG.</p>
              <p className="muted">Select a 15-minute window to filter the timeline.</p>
              {momentum.map((p,i)=><button type="button" className={"momentum-row momentum-select"+(selectedWindow===i?" selected":"")} key={p.label} aria-pressed={selectedWindow===i} onClick={()=>{setSelectedWindow(v=>v===i?null:i);setTimelineFilter("all");}}><span>{p.label}</span><div className="momentum-bars" aria-label={"Aurora "+p.home+", Harbor "+p.away}><div style={{width:(p.home*100/Math.max(1,p.home+p.away))+"%",background:"#65d5ff"}}/><div style={{width:(p.away*100/Math.max(1,p.home+p.away))+"%",background:"#ffb86b"}}/></div><span>{p.home}:{p.away}</span></button>)}
              <p className="muted"><strong style={{color:"#65d5ff"}}>● Aurora FC (blue)</strong> · <strong style={{color:"#ffb86b"}}>● Harbor United (orange)</strong></p><p className="muted">{selectedWindow===null ? "Showing all match events." : `Timeline filtered to minutes ${selectedWindow*15}–${(selectedWindow+1)*15}. Select the same window again to clear.`}</p>
              <h3>Key turning points</h3>{turningPoints.length?<ul>{turningPoints.map(({event:e,change,score})=><li key={e.id}>{formatClock(e)} — {change}: {e.player} scored for {e.team}. Score {score}.</li>)}</ul>:<p>No goals recorded yet.</p>}
            </div>}
            <div className="persona-extra" aria-label="Match story recap"><h3>Match story recap</h3><p dir={language==="ar"?"rtl":"ltr"}>{recap}</p><p className="muted">Based on played synthetic events.</p></div>
            <div className="insight-card" aria-live="polite" aria-atomic="true">
              <div className="insight-heading"><span><Sparkles size={16} /> VYBE INSIGHT</span><span className="grounded"><ShieldCheck size={14} /> EVIDENCE-BASED</span></div>
              {explanation && <div className="evidence">{explanation.generation_mode === "azure_ai" ? "Azure AI-selected style · verified factual template" : "Evidence-based commentary · deterministic fallback"}</div>}
              <p className="insight-text">{explanation?.narrative ?? (latestGoal ? "Preparing the latest goal insight…" : "Press play to experience the match. Insights appear when a goal is scored.")}</p>
              {explanation && <div className="evidence"><CheckCircle2 size={15} /> Verified from synthetic event <code>{explanation.evidence_event_ids.join(", ")}</code></div>}
            </div>
            {persona==="accessible" && <div className="persona-extra" role="group" aria-label="Accessibility preferences"><strong>Accessibility preferences</strong><label className="access-choice"><input type="checkbox" checked={highContrast} onChange={e=>setHighContrast(e.target.checked)}/> High contrast</label><label className="access-choice"><input type="checkbox" checked={largeText} onChange={e=>setLargeText(e.target.checked)}/> Large text</label><label className="access-choice"><input type="checkbox" checked={expandedAudio} onChange={e=>setExpandedAudio(e.target.checked)}/> Describe shots and passes too</label><p className="muted">Keyboard: Space play/pause, arrows move events when focus is outside controls; Tab navigates controls.</p></div>}
            {persona === "accessible" && <div role="group" aria-label="Spoken commentary controls">
              <button type="button" className="audio-toggle" onClick={() => audioEnabled ? stopAudio() : (spokenGoalIds.current.clear(), setAudioEnabled(true))} aria-pressed={audioEnabled}>{audioEnabled ? <VolumeX size={18} /> : <Volume2 size={18} />}{audioEnabled ? "Stop spoken commentary" : "Enable spoken commentary"}</button>
              {audioEnabled && <button type="button" className="audio-toggle" onClick={() => { if (!("speechSynthesis" in window)) return; if (audioPaused) { window.speechSynthesis.resume(); setAudioPaused(false); } else { window.speechSynthesis.pause(); setAudioPaused(true); } }} aria-pressed={audioPaused}>{audioPaused ? <Play size={18} /> : <Pause size={18} />}{audioPaused ? "Resume commentary" : "Pause commentary"}</button>}
              <label htmlFor="speech-rate" className="progress-label">Commentary voice speed</label>
              <select id="speech-rate" value={speechRate} onChange={(event) => setSpeechRate(Number(event.target.value))} style={{ color: "inherit", background: "#25243e", border: "1px solid #8171bc", borderRadius: "0.5rem", padding: "0.45rem 0.65rem", margin: "0.5rem", font: "inherit" }}>
                <option value={0.5}>0.5× · Very slow</option>
                <option value={1}>1× · Normal</option>
                <option value={1.5}>1.5× · Fast</option>
                <option value={2}>2× · Very fast</option>
              </select>
              <button type="button" className="audio-toggle" onClick={() => {
                if (!("speechSynthesis" in window)) return;
                // Keep the match commentary intact: do not cancel an active narration.
                if (speechActive.current || window.speechSynthesis.speaking || window.speechSynthesis.pending) return;
                const preview = new SpeechSynthesisUtterance("Welcome to VYBE. This is a preview of your selected commentary speed.");
                preview.rate = speechRateRef.current;
                previewSpeech.current = preview;
                preview.onend = () => { previewSpeech.current = null; };
                preview.onerror = () => { previewSpeech.current = null; };
                window.speechSynthesis.speak(preview);
              }} disabled={narrating} title="Preview is available when commentary is not speaking">Test voice speed</button>
              <span className="progress-label">Speed changes apply to the next commentary.</span>
            </div>}
            <div className="trust-note"><CircleHelp size={16} /><span>AI commentary is optional and experimental; automated fact checks are limited. Synthetic match scores come from the deterministic engine.</span></div>
          </div>
        </section>

        <section className="timeline-section">
          <div className="timeline-title"><div><span className="section-label">THE STORY SO FAR</span><h2>Match timeline</h2></div><span className="muted">Only simulated events</span></div>
          <div className="timeline-filter" role="group" aria-label="Filter match timeline">
            <button type="button" className={timelineFilter === "highlights" ? "primary" : "secondary"} aria-pressed={timelineFilter === "highlights"} onClick={() => setTimelineFilter("highlights")}>Highlights</button>
            <button type="button" className={timelineFilter === "all" ? "primary" : "secondary"} aria-pressed={timelineFilter === "all"} onClick={() => setTimelineFilter("all")}>All events ({visibleEvents.length})</button>
          </div>
          {selectedWindow!==null && <button type="button" className="secondary" onClick={()=>setSelectedWindow(null)}>Clear time filter</button>}
          <label className="access-choice"><input type="checkbox" checked={showEventDetails} onChange={e=>setShowEventDetails(e.target.checked)} /> Show event details</label>
          <ol className="timeline">
            {[...timelineEvents].reverse().map((event) => <li key={event.id}><span className="event-time">{formatClock(event)}</span><span className={event.type === "goal" ? "event-icon goal-icon" : "event-icon"}>{event.type === "goal" ? "⚽" : event.type === "shot" ? "↗" : event.type === "pass_completed" ? "→" : "•"}</span><div><strong>{event.type === "goal" ? "GOAL!" : event.type.replace("_", " ").toUpperCase()}</strong>{showEventDetails && <p>{event.team ?? "Match official"}{event.player ? ` · ${event.player}` : ""}</p>}</div>{event.type === "goal" && <span className="goal-label">KEY MOMENT</span>}</li>)}
          </ol>
        </section>
        {error && <div className="error" role="alert">Backend connection issue: {error}. Start the FastAPI server on port 8000.</div>}
      </main>
      <footer><div className="brand small"><Activity size={17} /> VYBE.</div><span>Built for every kind of fan. Synthetic match data only.</span><span>POWERED BY HUMAN CONNECTION <ArrowRight size={15} /></span></footer>
    </div>
  );
}
