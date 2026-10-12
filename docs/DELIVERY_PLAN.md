# Delivery Plan — October 2026

**Hackathon deadline:** October 27, 2026 at 11:59 PM Pacific (verify final submission timezone on event portal).

## Current status (October 12, 2026)

- Feature PR #15 has been squash-merged into `main`; automated backend tests (43), frontend build, and GitHub API/Web/Container CI checks passed.
- Local Arabic Accessible narration and Guided Demo playback were verified in Chrome after installing the Windows `ar-EG` speech capability.
- The complete manual acceptance pass, mobile and accessibility checks, demo video, submission and live Azure integration/deployment remain outstanding.
- **Execution priority:** documentation and acceptance review → UI/mobile/accessibility → demo/submission materials → optional Azure AI integration and Azure deployment **last**, after the local experience is stable.
- Dates below are planning targets, not proof that each milestone was completed. Verify the official deadline/timezone in the event portal.

## Phase 1 — Foundation (Oct 10–12)
- Product vision, architecture, repository conventions
- Synthetic event schema and a reproducible match fixture
- API skeleton with health check and automated tests

## Phase 2 — Working match experience (Oct 13–17)
- Deterministic match state and event playback
- Evidence-backed insights and fallback narratives
- React live dashboard with persona switching

## Phase 3 — Acceptance and submission preparation (Oct 18–22)
- Complete cross-persona desktop/mobile/accessibility manual acceptance and resolve defects
- Prepare demo story, recording, submission copy and reproducibility notes
- Confirm basic telemetry/error handling and disclose deterministic vs optional Azure narration

## Phase 4 — Azure last, then submission quality (Oct 23–27)
- Integrate and validate Microsoft Foundry narration only if time and hackathon requirements permit; preserve deterministic fallback
- Deploy to Azure Container Apps only after local acceptance; verify availability, costs, configuration and access
- Rehearse demo: same 87th-minute goal, three human experiences
- Finalize setup instructions, architecture and evaluation evidence
- English project description and public video under 2 minutes
- Verify judges can access the app without payment through judging

## Definition of done
A judge can open the demo, replay a synthetic match, switch personas, inspect why an insight was generated, and experience an accessible interface.
