# VYBE — Delivery Plan (updated 18 October 2026)

> **Document status (October 25, 2026):** This document preserves historical checks and planning. Earlier references to future deployment or unverified production tests are historical, not current release status. The current deployment is in [Architecture](ARCHITECTURE.md); owner-observed production responses are in [the evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). The final video was uploaded to https://youtu.be/-pfgaeGjSN8. No CI check alone certifies Azure inference, cost, WCAG, or all devices.


**Project:** VYBE — Every Fan Belongs · *Feel the Game. Your Way.*  
**Challenge:** Microsoft × Premier League Inside the Game — Synthetic Match Insights Engine.  
**Official submission target:** 27 October 2026 (portal lists 11:59 PM Pacific in the earlier plan; reverify on the event portal).  
**Internal completion:** 26 October 2026. **Azure target:** 22 October 2026.  
**Budget:** approximately **500 CZK TOTAL** through judging, not per month. Existing EUR 10/month Azure alerts are not a hard cap. **No billable Azure writes or paid inference without separate explicit owner approval after a cost review.**  
**Registry:** private GHCR image only. **Region:** germanywestcentral. **Resource group:** rg-vybe-hackathon.

## Non-negotiable scope
- Synthetic match Aurora FC vs Harbor United; deterministic event timeline, verified match state and evidence-backed insights.
- Three distinct fan experiences: Young Fan, Accessible and Analyst.
- English, Czech and Arabic commentary, browser speech and accessibility; changing persona/language must not interrupt an active utterance or skip the current event.
- Broadcast Studio, grounded Ask the Match and clear indication of AI-generated versus deterministic output.
- **Live Microsoft Foundry-hosted model integration is REQUIRED**, not optional. Deterministic fallback is a safety mechanism and does not satisfy the live demonstration requirement.
- Azure Container Apps hosts the public judge-accessible application; GHCR package stays private. Do not imply managed Microsoft Foundry Agent Service is implemented: current code uses Azure OpenAI-compatible model APIs for bounded tool selection and grounded narration.
- Public English demo video under two minutes, reproducibility notes, source repository and working judge-accessible link.

## Current evidence (as of 18 October)
- Main includes PR #72: continuous event narration and persona/language handoff; automated CI passed and user confirmed local experience.
- Main includes PR #73: required Foundry launch gate and acceptance checklist.
- Historical October 18 status: deployment not yet verified. October 24 CI subsequently deployed to Azure; October 25 owner-observed Foundry-related production responses are preserved in the evidence pack.
- Existing `apps/api/vybe/director_agent.py` selects one read-only tool via Azure OpenAI-compatible chat completions; `apps/api/vybe/ai.py` selects verified narration facts. Both require a compatible endpoint, deployment and secret; neither is proof of managed Agent Service.
- The historical 53-second preview was superseded by the 75-second narrated demo, uploaded to https://youtu.be/-pfgaeGjSN8.
- Previously completed local QA does not substitute for a full live end-to-end acceptance pass.

## Milestones
| Date | Work | Exit gate |
| --- | --- | --- |
| Oct 18–20 | Freeze core replay/voice fixes; review security, responsive UI and accessibility; prepare Azure/Foundry config without creating paid resources | Green CI, verified private image, no regressions |
| Oct 19–21 | Confirm available Foundry model and endpoint compatibility; add secure Container Apps model configuration; prepare live test procedure | Model supports required tool calling; secrets server-side; forecast prepared |
| Oct 21 | Read-only Azure preflight, inspect subscription/quota/region, calculate full-through-judging forecast for Foundry, Container Apps, logs, egress and tax | Owner reviews cost and explicitly approves any paid action |
| Oct 22 | Target: approved Foundry model deployment and Container Apps release | Public HTTPS /health and UI; real model call shows `foundry_model_tool_call` and narration shows `azure_ai` |
| Oct 23 | Deployment contingency and live security, accessibility and budget checks | Judge path works; synthetic facts grounded; deterministic fallback also tested |
| Oct 24–25 | Rehearse same 87th-minute goal across Young/Accessible/Analyst, languages and Ask the Match; finalize evidence | End-to-end browser and backend pass; capture proof of real Foundry usage |
| Oct 26 | Internal freeze: final public video, English description, architecture, setup and screenshots | Submission package complete and link verified from a fresh browser |
| Oct 27 | Submit through official hackathon portal before verified cutoff | Confirmation recorded; no further feature changes |
| Through judging (review around Nov 21) | Check spending and uptime; seek separate approval before resource cleanup | Spend within agreed total; judge link stays available as required |

## Priority and change control
1. P0: working live Foundry model integration and accurate proof, with grounded outputs.
2. P0: safe affordable Azure deployment and judge-accessible HTTPS URL.
3. P0: final submission/video and tested accessible three-persona experience.
4. P1: visual polish only if P0 gates are green. **No new features after Oct 23** unless required to fix a submission-blocking defect.
5. If a model is unavailable, choose another compatible pay-as-you-go model after cost/quality review; do not quietly downgrade the Foundry requirement or claim a deterministic response is a live model call.

## Cost/security rules
- Prefer small compatible pay-as-you-go chat model (e.g. gpt-4.1-mini **only if available and priced appropriately**); avoid provisioned capacity and expensive managed agent sessions.
- Container Apps scale 0–1; minimize logging/retention; no extra Azure Container Registry.
- Keep GHCR read token and Foundry key only in server-side secrets, never frontend or git.
- Monitor Azure spend; the existing EUR 10 monthly alert is not a hard limit. Budget forecasts are estimates, not guarantees.
- Deployment requires a fresh explicit authorization; approval to merge PRs is **not** authorization to spend.

## Definition of done
A judge can access VYBE without payment, replay a fictional match, switch fan personas and languages without losing spoken events, inspect evidence-backed insights, ask a grounded question, and **see proof of a real Microsoft Foundry-hosted model call**. The team can demonstrate the safe fallback and show the architecture, costs and final submission assets.

See [Foundry required launch gate](FOUNDRY_REQUIRED_LAUNCH.md) and [private GHCR deployment](GHCR_DEPLOYMENT.md).
