# VYBE — Final Acceptance Checklist

> **Document status (October 25, 2026):** This document preserves historical checks and planning. Earlier references to future deployment or unverified production tests are historical, not current release status. The current deployment is in [Architecture](ARCHITECTURE.md); owner-observed production responses are in [the evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). The final video was uploaded to https://youtu.be/-pfgaeGjSN8. No CI check alone certifies Azure inference, cost, WCAG, or all devices.


This checklist records historical targeted checks plus the **completed 24/24 manual E2E acceptance run** and later local validation. The older unchecked item-level template below remains a reference for regression coverage, **not a claim that those items failed or were individually re-run on this audit date**. Passing CI and manual acceptance do not establish WCAG compliance or production security.

## Verified progress (October 12, 2026)

- [x] PR #15 merged into `main` (squash merge commit `3d13cedbee1c732737039bfd47d72922132e9803`).
- [x] Backend automated tests: **43 passed** in the local test run before merge.
- [x] Frontend TypeScript/Vite production build succeeded before merge.
- [x] GitHub CI: API tests, Web build and Container build succeeded for PR #15.
- [x] Local FastAPI server started successfully on `127.0.0.1:8000` and Vite started on `localhost:5173`.
- [x] Windows Arabic (`ar-EG`) text-to-speech capability installed; Chrome exposed Microsoft Hoda and successfully spoke Arabic test text.
- [x] User confirmed the Arabic Accessible/Guided Demo narration and Play/Pause worked in the locally running VYBE app.

**Scope:** These are targeted checks, not evidence that every item below passed. Voice availability and accent depend on the user's OS/browser; the installed `ar-EG` voice did not sound distinctly Egyptian to the tester. This paragraph describes the October 12 snapshot; the later 24/24 manual acceptance run is documented below.

## Additional verified accessibility checks (October 12, 2026)

- [x] PR #17 mobile accessibility controls merged; mobile Chrome iPhone-sized viewport (393×852) checked for horizontal overflow and responsive layout.
- [x] Keyboard smoke checks (9/9): skip link, language selector, live captions toggle, play/pause, arrow event navigation, and native select arrow behavior. Skip-link landing/scroll positioning remains a minor improvement note.
- [x] Windows Narrator controls (5/5 targeted): skip link, language selector, live captions state, play/pause, and match progress value were announced.
- [x] Narrator dynamic captions were announced, but timed playback could finish before speech finished; treated as a timing limitation, not a full pass.
- [x] PR #18 Step-by-step playback merged and locally built successfully; user confirmed Narrator reads each newly selected event and the event does not advance automatically.
- [x] Arabic Narrator reading tested with Microsoft Hoda (ar-EG). Pronunciation and punctuation behavior were accepted as OS voice limitations, not a guarantee of natural Arabic speech.
- [x] PR #18 Web and Container CI checks passed on merged `main` commit `d0a6695`; local `git status -sb` was clean and synchronized.

## Final release readiness evidence (October 2026)

- [x] Manual E2E acceptance: **24/24 passed** (Young Fan 8/8, Accessible 6/6, Analyst 5/5, General 4/4, Final Smoke 1/1).
- [x] Goals-only timeline filter manually verified: four synthetic goals displayed; PR #21 merged by project owner.
- [x] Backend unit tests rerun locally using Python 3.13.14: **43 passed, 1 Starlette/httpx deprecation warning**.
- [x] Frontend TypeScript/Vite production build passed locally.
- [x] `npm audit --omit=dev` and full `npm audit`: **0 known vulnerabilities**.
- [x] `pip-audit`: **no known vulnerabilities** in installed external Python packages; local editable `vybe-api` is not on PyPI and was skipped.
- [x] Local `git status -sb`: `## main...origin/main`, no local changes reported.
- [ ] Final source-code security/secrets review, browser regression after release changes, and live Azure deployment validation are separate gates.

## Prerequisites

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
- [ ] Verify **mandatory** Microsoft Foundry model integration is accurately described; do not claim a live model call or managed Agent Service unless actually deployed and verified.
- [ ] Review the final release diff and complete remaining acceptance checks before declaring the demo submission-ready. (PR #15 has already been merged.)

**Status: 24/24 MANUAL E2E ACCEPTANCE PASSED; LOCAL BACKEND/FRONTEND BUILDS AND DEPENDENCY AUDITS PASSED.** The older unchecked template above is retained for future targeted regression testing. No full WCAG certification, comprehensive source-code security audit, or live Azure validation is claimed.

## Pre-Azure validation (October 18, 2026)

- [x] PR #39 merged into `main`; all six GitHub Actions checks passed before merge.

- [x] Backend automated tests: 54 passed locally.
- [x] Playwright browser tests: 4 passed, including replay API failure and retry recovery.
- [x] Frontend TypeScript and Vite production build passed after final error-handling changes.
- [x] Docker image built successfully; container health endpoint returned status `ok`.
- [x] Frontend production dependency audit: 0 known vulnerabilities.
- [x] Python dependency audit: no known vulnerabilities in audited external packages; local unpublished package skipped.
- [x] Frontend API requests use a 10-second timeout and provide retry controls for replay and commentary failures.
- [x] Azure Container Apps deployment health passed October 24; owner-supplied October 25 API responses reported Foundry tool selection and Azure AI narration. Independent Azure inference logs remain unverified.
- [ ] Final source-code security review, cross-browser accessibility audit, and production readiness sign-off remain pending.

These checks establish local pre-deployment readiness only. They do not establish WCAG certification, a comprehensive security audit, or successful live Azure operation.

## Mandatory Foundry and final-demo acceptance (added October 18, 2026)

- [ ] Confirm Foundry deployment and supported model tool-calling capability; capture actual model, region and deployment name without exposing secrets.
- [ ] Confirm explicit owner approval and combined Azure forecast remain within 500 CZK **total** through judging.
- [ ] Confirm private GHCR package, server-side secret references and public HTTPS Container Apps endpoint.
- [x] Owner-observed production response returned `generation_mode=foundry_model_tool_call`, `selected_tool=get_key_moments` and valid evidence IDs (October 25).
- [ ] Verify a real goal narration request returns `generation_mode=azure_ai` with only validated fact IDs.
- [ ] Verify deliberate Foundry outage produces deterministic fallback; do not mislabel it as live AI.
- [ ] Re-run continuous spoken narration: persona/language switch must finish current utterance before the next event.
- [x] Final 75-second narrated demo produced and uploaded to https://youtu.be/-pfgaeGjSN8 (owner-reported; public playback not independently checked).
- [ ] Verify judge access without sign-in, and link the actual tested URL in README and judges' guide.
- [ ] Confirm submission deadline/timezone from the official portal and capture successful submission confirmation.

See [required Foundry gates](FOUNDRY_REQUIRED_LAUNCH.md) and [final demo storyboard](FINAL_DEMO_STORYBOARD.md).
