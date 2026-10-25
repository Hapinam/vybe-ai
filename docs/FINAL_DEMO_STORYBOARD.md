# VYBE — Final hackathon demo storyboard (working plan)

**Final produced demo:** 75-second narrated MP4 uploaded by the owner to https://youtu.be/-pfgaeGjSN8. The storyboard below is the earlier 110-second planning script, **not** the running order of the final video. The 53-second preview at https://youtu.be/c717qul116M is historical.

## Historical 110-second planning storyboard (superseded)

| Time | Screen | Suggested voice-over |
| --- | --- | --- |
| 0–10s | VYBE identity + synthetic match banner | “Football brings us together, but not every fan experiences a match the same way.” |
| 10–30s | Young Fan goal and quiz | “VYBE turns the same fictional match into an exciting, understandable story for younger fans.” |
| 30–50s | Accessible mode: Arabic/Czech/English, captions, contrast and step-by-step | “Fans can choose language, readable captions, contrast and control over match narration.” |
| 50–70s | Analyst: weighted event activity and evidence | “Analysts explore recorded actions and trace each insight back to match evidence, without inventing tactics or xG.” |
| 70–95s | Ask the Match with real Foundry-enabled tool selection and verified evidence IDs | “Microsoft Foundry powers a bounded AI decision: it selects a read-only match tool, while our deterministic engine verifies the facts.” |
| 95–105s | Grounded goal narration + server-side verified generation mode | “AI-assisted narration only uses approved, verified match facts. If the model fails, VYBE falls back safely.” |
| 105–110s | Brand outro | “VYBE. Every fan belongs.” |

## Recording and proof requirements

1. Open the deployed public HTTPS URL without login. Check `/health` and real UI; the October 24 main deployment CI passed.
2. Show one supported Ask the Match question (e.g. “Who scored?”) and independently capture the **actual** backend response with `generation_mode=foundry_model_tool_call`, `selected_tool`, and `evidence_event_ids`. The UI may show a user-friendly model label; do not paste developer tokens or API keys.
3. Verify one grounded goal narration response has `generation_mode=azure_ai`; display it only if genuinely returned from the live model.
4. Capture a separate fallback test for evidence; **do not** portray deterministic mode as live Foundry.
5. Record the browser screen with real UI, English voice-over and readable captions. Browser SpeechSynthesis does not necessarily appear in Playwright's silent WebM recording; record voice-over separately.
6. Keep the synthetic match disclaimer visible. Do not suggest official Premier League data, live match feeds, real-world tactical inference, managed Foundry Agent Service, or production WCAG certification.
7. Confirm English audio clarity, text contrast, 16:9, duration below two minutes, licensed audio/media, final URL and submission requirements.
8. Replace/update video links in README, judges guide and project portal **only after** the new upload is verified. Keep the previous URL until then.

## Current status

- [x] Script/storyboard written.
- [x] Azure Container Apps deployment health passed; owner supplied October 25 production API responses reporting Foundry tool calling and Azure AI narration. See [evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). Independent Azure inference logs remain pending.
- [x] New browser capture and English narration assets prepared by the owner; final synchronization/export still needs acceptance.
- [x] Final video exported and uploaded: https://youtu.be/-pfgaeGjSN8 (owner-reported; public playback not independently tested).
- [ ] README, judges guide and hackathon project page updated with verified live URL and video.
- [ ] Full judging and submission acceptance pass completed.

This document creates no Azure resources and does not imply any paid inference has occurred.
