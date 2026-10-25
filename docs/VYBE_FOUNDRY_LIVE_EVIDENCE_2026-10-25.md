# VYBE — Microsoft Foundry Live Evidence Pack

**Evidence observation date:** 2026-10-25 (historical snapshot; not continuously updated)  
**Document review:** 2026-10-25  
**Environment:** Production, user-observed browser Network responses  
**Application:** https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io  
**Repository:** https://github.com/Hapinam/vybe-ai  
**Production code revision referenced:** `bf3ad1b` (PR #106); the live image SHA was not independently established from these browser responses

> **Evidence provenance:** The two JSON responses below were copied by the application owner from browser DevTools during manual production testing and supplied in the conversation. This pack preserves those observations; it is not an independent Azure trace, audit log, or billing record. No secrets are included.

## Test 1 — Ask the Match: Foundry tool selection

**Action:** Ask a supported question about the match's key scoring moments using the production Ask the Match interface.  
**Observed response:**

```json
{
  "answer": "Recorded key moments: Aurora FC scored at 12:10 (took lead); Harbor United scored at 24:35 (equalizer); Harbor United scored at 55:08 (took lead); Aurora FC scored at 87:24 (equalizer). No tactical cause is inferred.",
  "evidence_event_ids": ["e2", "e3", "e5", "e8"],
  "supported": true,
  "generation_mode": "foundry_model_tool_call",
  "selected_tool": "get_key_moments",
  "persona": "accessible",
  "synthetic": true
}
```

**Acceptance:** PASS for the observable API contract: model-tool-call mode, an expected read-only tool, evidence event references, supported answer, and explicit synthetic-data disclosure. This response alone does not independently verify an upstream Azure model request in Azure logs.

## Test 2 — Goal narration: Azure AI mode

**Action:** Request narration for the first goal, event `e2`, in production.  
**Observed response:**

```json
{
  "event_id": "e2",
  "persona": "accessible",
  "narrative": "Match update. This is a fictional match reconstructed from synthetic events. Goal for Aurora FC at minute 12, 10 seconds. The score is Aurora FC 1, Harbor United 0. End of update.",
  "evidence_event_ids": ["e2"],
  "score": {"home": 1, "away": 0},
  "synthetic": true,
  "generation_mode": "azure_ai",
  "selected_fact_ids": ["context", "goal", "score"]
}
```

**Acceptance:** PASS for the observable API contract: Azure AI mode reported, selected facts identified, single-event evidence, score 1–0, and synthetic-data disclosure. The narration contains no unsupported tactical explanation. This response alone does not independently verify upstream model execution.

## Claims supported by these observations

- The deployed API returned the intended Foundry-related mode and grounded evidence fields for two distinct paths.
- A supported match question selected `get_key_moments`.
- Goal `e2` narration used `context`, `goal`, and `score` fact IDs.
- Both paths clearly identified the fixture as synthetic.

## Claims NOT established by this pack

- No independent Azure Foundry model inference trace, token usage, or resource identity was inspected.
- Fallback behavior under a real Foundry outage was not live-tested.
- All questions, all match events, all personas, and all browsers were not exhaustively tested.
- iPhone Safari/Chrome audio acceptance, WCAG conformance, and Azure spend/quota have not been verified here.
- This project does not claim to implement a managed Foundry Agent Service agent.

## Recommended demo evidence capture (no application changes)

1. In the production app, show the fictional match and the **Synthetic** label.
2. Open **Ask the Match**, ask for key moments, and show the visible answer.
3. In browser DevTools → Network, capture the response fields `generation_mode`, `selected_tool`, `evidence_event_ids`, and `synthetic` (hide tokens or sensitive headers).
4. Trigger goal `e2` narration; show the `generation_mode`, `selected_fact_ids`, `evidence_event_ids`, and score.
5. Show the approved Evelyn Arabic speech briefly, with captions.
6. Capture a dated screenshot or short screen recording of each response for judges. Optionally correlate with Azure resource logs for stronger independent proof.

## Status scope and later developments

This document is an **evidence snapshot**, not the authoritative current release checklist. The responses below are preserved as observed on October 25 and should not be overwritten by subsequent tests; newer observations belong in a new dated evidence section/file. For current setup, see [the main README](../README.md), [judges' guide](JUDGES_TESTING_GUIDE.md) and [release plan](DELIVERY_PLAN.md).

The demo video has since been exported and uploaded to YouTube (https://youtu.be/-pfgaeGjSN8), but YouTube playback is not independently checked by this evidence pack. Documentation updates are proposed in draft PR #107; they are not yet merged into `main`.

## Checklist at the time of the October 25 observation (historical)

- [x] Owner-supplied production Ask the Match response shows `foundry_model_tool_call`.
- [x] Owner-supplied production narration response shows `azure_ai`.
- [x] Owner reports Evelyn Arabic speech accepted in production.
- [ ] Independently corroborate model calls in Azure logs, if available.
- [ ] Review Azure Speech tier, spend, and budget alerts.
- [ ] Confirm iPhone audio if required for judging.
- [x] Final demo video was produced and uploaded to YouTube; processing/playback verification was still pending when last reported.
- [x] Documentation updates proposed in draft PR #107 (not yet merged to `main`).
- [ ] Freeze judge-facing production after final approval.

**Release control:** Originally prepared as a local observation pack, this document is now committed on a documentation-only branch in draft PR #107. It has not been merged into `main` and does not itself prove a new production deployment.