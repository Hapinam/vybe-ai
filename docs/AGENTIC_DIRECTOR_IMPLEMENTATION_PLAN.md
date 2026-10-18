# VYBE AI Match Director — implementation plan

**Status:** Approved scope; implementation in progress. No cloud resources are provisioned by this document or PR. Target submission: October 27, 2026.

## Codebase review (October 18)

- FastAPI accepts caller-supplied, validated synthetic `MatchDefinition` (max 500 events); deterministic replay is the source of truth.
- `/v1/matches/ask` is deterministic question answering, **not** an agent.
- `/v1/matches/narrate/{event_id}` optionally calls Azure OpenAI for **selection of exact verified facts**, with deterministic fallback; it is **not** a Foundry agent.
- React already implements Young, Accessible and Analyst modes, local replay snapshots and a question UI.
- Azure Container Apps deployment is prepared but unexecuted. Azure OpenAI / Microsoft Foundry are not deployed or verified.

## Workstreams and merge gates

| Phase | Deliverable | Acceptance gate |
| --- | --- | --- |
| PR 1 — foundation | Read-only `get_match_state`, `get_key_moments`, `get_match_statistics` tools, evidence IDs, tests and plan | Unit tests pass; existing API unchanged; no network or Azure writes |
| PR 2 — Foundry adapter | Server-side Microsoft Foundry agent integration and constrained tool-call dispatch; explicit configuration; deterministic fallback | Mocked tool-call tests, invalid-call refusal, timeouts, secrets never in frontend/logs; verified real Foundry call **only after owner approval** |
| PR 3 — insights and Ask | Evidence-grounded recap, “why it matters” and agentic Ask the Match; show unsupported claims as unsupported | Every displayed claim traces to event IDs; agent cannot invent tactics; deterministic mode remains usable |
| PR 4 — presentation | Broadcast Studio Mode and persona-specific AI outputs, visible generation mode and evidence viewer | Playwright E2E for all three personas, keyboard/accessibility regression, mobile layout |
| PR 5 — launch | Deployment/configuration docs, budget guardrails, smoke tests, updated demo and judges guide | Explicit owner approval before Azure writes; verified public HTTPS demo and actual AI mode before claiming live integration |

## Design constraints

1. One orchestrating agent with three **read-only allowlisted tools**; do not imply multi-agent architecture.
2. Match events and tool results are **untrusted data**, not instructions. Never execute model-supplied code, arbitrary URLs or unregistered tool names.
3. Evidence IDs must exist in the validated match; score, scorer and chronology come only from deterministic engine outputs. Do not imply tactical causality, xG or possession.
4. Separate **generated language** from **verified facts**. Reject unsupported model claims and fall back safely.
5. Limit agent rounds, tool calls, token output, request body size and latency. Per-process rate limits do **not** enforce a spend cap.
6. Azure credentials stay server-side. Keep `min-replicas=0`, `max-replicas=1` as a starting point; review logging, ACR/GHCR, model quota and pricing before deployment.
7. Budget target: **500 CZK for the planned live window**, not a guaranteed cap. No paid resources, deployments, or deletion without explicit owner approval.
8. Do not merge PRs automatically; the repository owner reviews and merges.

## Demo narrative

1. A fictional match event occurs.
2. AI Match Director selects an allowlisted tool and reads deterministic evidence.
3. The interface shows a supported insight, linked evidence IDs, and the selected persona's explanation.
4. Ask the Match answers a follow-up using tool results or explicitly declines unsupported tactical claims.
5. Broadcast Studio displays the same event for Young, Accessible and Analyst audiences.
6. Clearly disclose synthetic data, deterministic fallback and whether a **real** Foundry deployment is active.

## Schedule and stop conditions

- Oct 18–19: foundation + adapter with mocks.
- Oct 20–22: grounded insights, agentic Q&A, UI integration and (if approved) cloud validation.
- Oct 23–24: E2E, accessibility checks, cost/latency tests and stabilization.
- Oct 25–26: updated video, public demo verification, submission checklist.
- Oct 27: final submission buffer.

**Stop adding features** if integration cannot pass tests or public demo reliability is at risk. Prioritize working, verifiable functionality over agent count.
