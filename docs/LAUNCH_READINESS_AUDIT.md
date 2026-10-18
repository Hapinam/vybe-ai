# PR 61 — Launch readiness audit and no-cost deployment preflight

**Review date:** October 18, 2026. **No Azure resources created.**

## Verified by reading current `main`

- Backend routes: `/health`, `/v1/matches/replay/states`, `/v1/matches/narrate/{event_id}`, `/v1/matches/insights`, `/v1/matches/director/ask`.
- Studio fetches deterministic persona-specific insights; only played goal moments appear in its pick list, while the full-fixture recap is clearly marked as a spoiler.
- Ask the Match sends the selected persona to the Director endpoint and displays model-tool-selection vs deterministic fallback.
- `director_agent.py` uses Azure OpenAI-compatible chat completions for **model tool selection**, not Microsoft Foundry managed Agent Service. No real model invocation is evidenced by the repository.
- Existing deployment script provisions a Basic ACR, uses an ACR build, creates/reuses Container Apps environment and managed identity, and creates a public Container App with min 0 / max 1 replicas. It is guarded by `CONFIRM_AZURE_DEPLOY=YES`.
- `/v1/matches/` rate limiting is per-process, not a spending cap; an exposed configured model endpoint can generate charges.
- Web E2E currently uses a mocked API, not a running FastAPI backend. A passing Playwright suite alone does **not** establish an integrated deployment.

## Risks and release decisions

| Priority | Risk | Gate |
| --- | --- | --- |
| P0 | Foundry model tool selection has never been validated live | Do not claim real cloud integration until owner-approved live test succeeds |
| P0 | 500 CZK is a planning budget, not a billing hard stop | Itemize registry, build, logs, model tokens, container usage, egress, tax; obtain owner approval |
| P0 | Public API can cause token spending if Foundry configured | Prefer separate bounded demo validation; set model quotas and monitor usage before public exposure |
| P1 | Studio has lacked dedicated E2E regression coverage | Add mocked studio playback/persona/evidence/failure tests in this PR |
| P1 | Playwright mocks do not verify the Python server | Run local full-stack smoke test and later HTTPS smoke test with real API |
| P1 | Studio recap reveals full-fixture score before replay completes | Current UI discloses spoiler explicitly; decide whether to hide recap during judging demo |
| P1 | Studio narrative remains deterministic across personas | Describe it as persona-aware evidence-grounded content, not generated AI |
| P2 | Public app's speech voices vary by browser and OS | Verify accessible narration and caption fallback on target devices |

## Read-only Azure inspection — optional, owner-run

```bash
az account show --query '{name:name,id:id}' -o json
az group show --name rg-vybe-hackathon --query '{name:name,location:location}' -o json
az resource list --resource-group rg-vybe-hackathon --query '[].{name:name,type:type,location:location}' -o table
az acr list --resource-group rg-vybe-hackathon --query '[].{name:name,sku:sku.name}' -o table
az containerapp list --resource-group rg-vybe-hackathon --query '[].{name:name,location:location}' -o table
```

No subscription identifiers, credentials or access tokens should be posted in a public PR.

## Owner approval gate

**Do not** run `CONFIRM_AZURE_DEPLOY=YES` or configure paid Foundry credentials without a separate explicit approval, an itemized estimate for the full hosting window, and a cleanup plan. A dry-run of the script also needs `AZURE_SUBSCRIPTION_ID` and `REGISTRY_NAME` environment variables.

## Required before calling VYBE launch-ready

1. GitHub Actions green on the **latest** PR commit.
2. Full-stack local smoke test with FastAPI and Vite, not mocks only.
3. Accessibility/mobile and demo-script manual review.
4. Live Foundry call (only if owner approves cost); document actual model/deployment, output and fallback.
5. Owner-approved Azure cost estimate and deployment; public HTTPS URL tested from incognito.
6. Update README, judges guide, submission and video using only verified live details.

No merges or cloud writes are performed by this PR.
