# VYBE — Judges' Testing Guide

**Feel the Game. Your Way.**

VYBE presents one fictional football match through three personalized experiences. This guide takes approximately **3–5 minutes**.

- **Demo video (53 seconds):** https://youtu.be/c717qul116M
- **Source code:** https://github.com/Hapinam/vybe-ai
- **Live application:** To be provided after successful Azure deployment and verification. No live URL is claimed yet.

## 1. Young Fan (about 45 seconds)

1. Select **Young Fan**.
2. Start replay or the **Guided Demo**.
3. Watch a goal celebration and read the simple, event-grounded commentary.
4. Try the football glossary and goal quiz.

**Look for:** understandable explanations, approachable learning, and interactive feedback.

## 2. Accessible Fan (about 60 seconds)

1. Switch to **Accessible**.
2. Select English, Arabic, or Czech commentary/captions.
3. Enable captions, high contrast, and larger text.
4. Optionally turn on browser speech and change the voice speed.
5. Enable **Step-by-step playback (screen reader friendly)** and use **Previous event** / **Next event**.

**Look for:** user-controlled presentation, multilingual event text, and keyboard-friendly navigation.

**Important:** Spoken commentary uses installed browser/OS voices. Arabic/Czech voices may not be available; captions remain usable. Captions are synchronized to events, not word-level speech transcription. This prototype has not undergone a full WCAG audit.

## 3. Analyst Fan (about 60 seconds)

1. Switch to **Analyst**.
2. Compare recorded shots and passes across match halves.
3. Inspect the **15-minute momentum** chart.
4. Select an interval to focus the event timeline, then clear the selection.
5. Compare **Highlights**, **Goals**, and **All events** timeline filters.

**Look for:** interactive, traceable insights grounded in the recorded match events.

**Important:** Momentum is a custom event-activity indicator (goal = 3, shot = 2, completed pass = 1), **not** possession, expected goals (xG), or tactical causation.

## 4. Ask the Match (about 30 seconds)

1. Scroll to **Ask the Match** and select **Who scored?** or **What was the final score?**
2. Inspect the returned **evidence event IDs**.
3. Select **Why did momentum change?** to see the explicit limits of the recorded evidence.

**Look for:** a useful, interactive question-and-answer panel that declines unsupported claims. The code can use a Foundry-hosted Azure OpenAI-compatible model to select one of three allowlisted read-only tools; without verified live configuration it uses deterministic event queries. A managed Foundry Agent Service agent is **not** implemented. It asks about the complete synthetic fixture, independent of playback position.

## 5. Technical approach (about 30 seconds)

The challenge pipeline is **Ingest → Interpret → Explain → Render → Personalize**.

- A deterministic Python replay engine processes ordered synthetic events and computes match facts.
- FastAPI exposes match state and event-grounded narratives.
- React/TypeScript presents the same match to three audiences.
- Preferences persist in the current browser when storage is permitted; blocked storage does not prevent use.
- Docker and Azure Container Apps deployment infrastructure are prepared.

**Microsoft Foundry is required for the final live demo.** The repository has bounded model adapters for narration and tool selection, but live Foundry operation remains unverified until deployed and tested. Deterministic fallback remains the source of safe answers during model failure. Do not assume the live Azure deployment or Azure AI endpoint is active unless separately verified.

## 6. Foundry live proof (required before submission)

1. In the deployed app, ask a supported factual question and verify the backend reports `generation_mode=foundry_model_tool_call`, an allowlisted `selected_tool`, and event evidence IDs.
2. Trigger a supported goal narration and verify `generation_mode=azure_ai` with validated facts.
3. Confirm no API keys or credentials are exposed in the browser.
4. Test the fallback separately; it must not be represented as live Foundry.
5. **Pending:** publish the verified public HTTPS app URL and record this evidence after owner-approved Azure deployment.

See [Final Demo Storyboard](FINAL_DEMO_STORYBOARD.md).

## 7. Validation evidence

The repository's [README](../README.md) and [Final Acceptance Checklist](FINAL_ACCEPTANCE_CHECKLIST.md) document the tested scope:

- GitHub Actions runs backend, Playwright, frontend/container and dependency checks; see the latest workflow results for current status.
- **24/24** manual end-to-end acceptance checks were previously recorded; these do not cover subsequent changes.
- Azure runtime and post-deployment smoke tests remain to be verified.

These checks are not a production security certification or a full accessibility audit.

## Responsible data

Aurora FC, Harbor United, and the match events are fictional. VYBE does not use official Premier League match feeds or provide real-time match coverage.

**One synthetic match. Three experiences. One consistent source of truth.**

**Every Fan Belongs. Every Moment Matters.**
