# VYBE — Final Acceptance Checklist

This checklist tracks verified targeted checks and the remaining **manual acceptance pass** after feature integration through PR #18. The full manual acceptance pass is still outstanding. Do not interpret the merged PR or passing CI as full acceptance.

## Verified progress (October 12, 2026)

- [x] PR #15 merged into `main` (squash merge commit `3d13cedbee1c732737039bfd47d72922132e9803`).
- [x] Backend automated tests: **43 passed** in the local test run before merge.
- [x] Frontend TypeScript/Vite production build succeeded before merge.
- [x] GitHub CI: API tests, Web build and Container build succeeded for PR #15.
- [x] Local FastAPI server started successfully on `127.0.0.1:8000` and Vite started on `localhost:5173`.
- [x] Windows Arabic (`ar-EG`) text-to-speech capability installed; Chrome exposed Microsoft Hoda and successfully spoke Arabic test text.
- [x] User confirmed the Arabic Accessible/Guided Demo narration and Play/Pause worked in the locally running VYBE app.

**Scope:** These are targeted checks, not evidence that every item below passed. Voice availability and accent depend on the user's OS/browser; the installed `ar-EG` voice did not sound distinctly Egyptian to the tester. The complete cross-persona and cross-language manual pass remains open, although targeted mobile, keyboard and screen-reader checks have now been performed.

## Additional verified accessibility checks (October 12, 2026)\n\n- [x] PR #17 mobile accessibility controls merged; mobile Chrome iPhone-sized viewport (393×852) checked for horizontal overflow and responsive layout.\n- [x] Keyboard smoke checks (9/9): skip link, language selector, live captions toggle, play/pause, arrow event navigation, and native select arrow behavior. Skip-link landing/scroll positioning remains a minor improvement note.\n- [x] Windows Narrator controls (5/5 targeted): skip link, language selector, live captions state, play/pause, and match progress value were announced.\n- [x] Narrator dynamic captions were announced, but timed playback could finish before speech finished; treated as a timing limitation, not a full pass.\n- [x] PR #18 Step-by-step playback merged and locally built successfully; user confirmed Narrator reads each newly selected event and the event does not advance automatically.\n- [x] Arabic Narrator reading tested with Microsoft Hoda (ar-EG). Pronunciation and punctuation behavior were accepted as OS voice limitations, not a guarantee of natural Arabic speech.\n- [x] PR #18 Web and Container CI checks passed on merged `main` commit `d0a6695`; local `git status -sb` was clean and synchronized.\n\n## Prerequisites

- [ ] Fetch the latest `main` without overwriting uncommitted local changes (`git status --short` first).
- [ ] Install backend dependencies, run `python -m pytest tests -q` from `apps/api`.
- [ ] Install frontend dependencies, run `npm run build` from `apps/web`.
- [ ] Start FastAPI on 8000 and Vite on its printed local port.
- [ ] Confirm `GET /health` responds successfully and the browser has no blocking errors.

## Replay and event integrity

- [ ] Start from kickoff; play, pause, resume, change 1×/2×/4× playback speed, scrub and restart.
- [ ] Scores advance only when goals occur; final score is **Aurora FC 2 – 2 Harbor United**.
- [ ] Event count reaches **31**, completed passes reach **12 – 11**; compare backend state and UI.
- [ ] Recorded shots and goal timeline remain consistent with synthetic events.
- [ ] Full-time jump and replay from full time work without stale narration or counters.

## Young Fan

- [ ] Goal celebration appears at each goal and shows correct player, team and minute.
- [ ] Celebration does not appear on non-goal events or in other personas.
- [ ] Glossary explains kickoff, passes, shots, goals, halftime and full time.
- [ ] Celebration and glossary remain legible on a narrow mobile viewport.
- [ ] Mini quiz asks about the latest goal, gives correct feedback, and resets on the next goal.
- [ ] Timeline filter switches between highlights and all events without altering match statistics.

## Accessible

- [ ] High contrast toggles correctly; text, controls and focus rings remain readable.
- [ ] Large text does not clip labels or controls on desktop/mobile.
- [x] Targeted Tab/skip-link/keyboard navigation smoke checks passed; full Shift+Tab and focus/scroll audit remains open.
- [ ] Space pauses/resumes replay; Left/Right arrows step events outside interactive controls.
- [ ] Enable/stop spoken commentary, pause/resume, and preview 0.5×/1×/1.5×/2× speeds.
- [ ] Kickoff, goal and full-time narration work; no clipped sentences or overlapping voices.
- [ ] Expanded audio narrates shots and passes without interrupting goal commentary.
- [ ] Switching personas, scrubbing, restarting and full-time jump do not leave stale speech.
- [ ] Reduced-motion preference disables unnecessary movement.
- [x] Windows Narrator smoke checks completed; manual step-by-step playback addresses caption timing, not automatic screen-reader voice synchronization.

## Analyst

- [ ] Half-by-half goals, recorded shots and passes match synthetic event counts.
- [ ] Momentum shows 15-minute windows and clearly identifies **weighted event activity**, not possession or xG.
- [ ] Turning points correctly identify goals, equalizers and leads with accurate scores.
- [ ] All analyst values update when scrubbing and reset when restarting.

## Additional features — final acceptance

- [ ] Switch between English, Arabic and Czech; verify captions and recap reflect the selected language and Arabic text reads right-to-left.
- [ ] In Accessible mode, test speech in all three languages where voices exist; document unavailable OS/browser voices.
- [ ] Verify event-based captions update at kickoff, goal, pass, shot, halftime and fulltime; toggle captions off/on.
- [ ] Verify recap never reveals goals that have not been played; check 2–2 at fulltime.
- [ ] Select and clear all six Analyst momentum windows; timeline must filter without changing score or totals.
- [ ] Reload the page; persona, language, contrast, font-size, captions, timeline view, event details and voice settings should persist in the same browser.
- [ ] Start Guided demo; confirm persona transitions and stopping behavior; verify no stale audio.
- [ ] Confirm translated templates are not represented as live Azure AI translation or word-level speech captions.

## Quality, documentation and release gate

- [ ] Check browser console and network requests for errors during a full replay.
- [ ] Check desktop and mobile layouts, color contrast, and responsive controls.
- [ ] Confirm root, API and web READMEs match the implemented code and commands.
- [ ] Verify synthetic-data disclosure and no secrets or Azure keys are committed.
- [ ] Verify optional Azure integration is described accurately; do not claim a live Azure service unless actually deployed and verified.
- [ ] Review the final release diff and complete remaining acceptance checks before declaring the demo submission-ready. (PR #15 has already been merged.)

**Status: PARTIALLY VERIFIED THROUGH PR #18 — FULL MANUAL ACCEPTANCE PENDING.** The verified progress above records targeted tests only. Unchecked items remain unverified.
