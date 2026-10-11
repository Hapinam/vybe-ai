# VYBE — Final Acceptance Checklist

This is the **single consolidated manual test pass** to run after all feature work and documentation is complete. Keep PR #15 in draft until this checklist has been executed and any failures resolved.

## Prerequisites

- [ ] Fetch the PR branch without overwriting uncommitted local changes (`git status --short` first).
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

## Accessible

- [ ] High contrast toggles correctly; text, controls and focus rings remain readable.
- [ ] Large text does not clip labels or controls on desktop/mobile.
- [ ] Tab/Shift+Tab and skip link work; focused controls retain native keyboard behavior.
- [ ] Space pauses/resumes replay; Left/Right arrows step events outside interactive controls.
- [ ] Enable/stop spoken commentary, pause/resume, and preview 0.5×/1×/1.5×/2× speeds.
- [ ] Kickoff, goal and full-time narration work; no clipped sentences or overlapping voices.
- [ ] Expanded audio narrates shots and passes without interrupting goal commentary.
- [ ] Switching personas, scrubbing, restarting and full-time jump do not leave stale speech.
- [ ] Reduced-motion preference disables unnecessary movement.
- [ ] Run at least one screen-reader smoke check if a screen reader is available.

## Analyst

- [ ] Half-by-half goals, recorded shots and passes match synthetic event counts.
- [ ] Momentum shows 15-minute windows and clearly identifies **weighted event activity**, not possession or xG.
- [ ] Turning points correctly identify goals, equalizers and leads with accurate scores.
- [ ] All analyst values update when scrubbing and reset when restarting.

## Quality, documentation and release gate

- [ ] Check browser console and network requests for errors during a full replay.
- [ ] Check desktop and mobile layouts, color contrast, and responsive controls.
- [ ] Confirm root, API and web READMEs match the implemented code and commands.
- [ ] Verify synthetic-data disclosure and no secrets or Azure keys are committed.
- [ ] Verify optional Azure integration is described accurately; do not claim a live Azure service unless actually deployed and verified.
- [ ] Only after all checks pass: mark PR ready for review, review diff, then merge.

**Status: NOT YET EXECUTED.** This document is a plan, not evidence of passing tests.
