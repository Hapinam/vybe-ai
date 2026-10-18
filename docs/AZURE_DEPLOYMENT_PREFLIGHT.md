# Azure deployment preflight — cost, security and judging

**Status:** Review-only preparation. This document does not authorize provisioning. Deployment requires the project owner's explicit approval on the agreed deployment date.

## Target and spend

- Subscription: owner-approved Pay-As-You-Go subscription (verify the exact subscription ID at execution time).
- Existing resource group: `rg-vybe-hackathon`; expected region: `germanywestcentral`.
- **Planning budget: 500 CZK total**, not a guaranteed cap. Verify the Azure billing currency, current spend, and any pre-existing resources before deployment.
- Intended public availability: October 21 through November 21, 2026, subject to actual judging requirements and explicit owner approval for deletion.
- Azure Cost Management budgets and alert emails **do not stop billing**. Do not proceed merely because an alert exists.

## Cost risks found in `infra/azure/deploy.sh`

| Resource | Why it matters | Preflight decision |
| --- | --- | --- |
| Azure Container Registry, Basic | May incur recurring charges even when the application has zero replicas | Confirm estimated cost for the entire retention period; prefer reusing an existing approved registry if suitable |
| Container Apps environment | Environment can provision associated observability resources | Inspect workspace creation and ingestion/retention costs before confirming |
| Azure Container App | Configured for 0–1 replicas, 0.5 vCPU and 1 GiB; scale-to-zero does not cap total usage | Review request volume, free allowances and ingress exposure |
| ACR build | Build may be billed and can fail after resources have already been created | Estimate build charges; check permissions and image size |
| Log Analytics | Potential ingestion/retention costs | Choose an explicitly approved minimal logging configuration; do not assume free logs |
| Managed identity / RBAC | No key in code; permissions still need review | Confirm AcrPull scope is limited to the intended registry |

**Go/no-go:** Do not run with `CONFIRM_AZURE_DEPLOY=YES` until the owner has reviewed an itemized estimate for the full planned lifetime, including registry and logging. If the estimate cannot fit the budget with reasonable headroom, revise the architecture or shorten the deployment duration **with approval**.

## Deployment security checks

1. Confirm Azure account, subscription ID, and the existing resource group/region before any write.
2. Confirm the globally unique ACR name is the intended owner-controlled registry; avoid unexpected registry creation.
3. Confirm no API keys, connection strings or secrets are in Git, container build arguments, or public logs.
4. Use the existing non-root Docker runtime user (`appuser`), and verify the container still starts.
5. Confirm the registry uses `--admin-enabled false` and the app identity receives only `AcrPull` on the target ACR.
6. Confirm the public endpoint is HTTPS; the application is intentionally public for judging.
7. Confirm the request-body guard and per-process rate limiting are **defense in depth**, not a distributed quota or spending cap. Public requests can still cause costs.
8. Do not configure Azure OpenAI credentials unless the owner separately approves the service, its pricing, and the live integration test.
9. Confirm the API and static UI are served from the same origin; no private credentials should be exposed in frontend assets.
10. Review provider registration and RBAC permissions before execution. The script can create multiple billable resources after the confirmation flag is set.

## Day-of-deployment gates

- [ ] Owner explicitly authorizes provisioning and confirms maximum acceptable spend.
- [ ] Azure cost estimate and billing-currency conversion reviewed.
- [ ] Existing resource group and registry inventory reviewed.
- [ ] Logging/workspace charges understood and approved.
- [ ] Registry name, application name, and subscription ID confirmed.
- [ ] Verify that no Azure resources were unexpectedly created during preparation.
- [ ] Execute deployment only after approval; capture actual resource IDs and FQDN.
- [ ] Test `/health`, the root UI, all three fan modes, and a full replay on the public HTTPS endpoint.
- [ ] Verify no auth is needed for judges; update README and Judges' Testing Guide with the **verified** public URL.
- [ ] Check actual cost and logs after deployment; adjust only with approval.

## Post-judging cleanup

- Inventory **all** resources created or reused by the deployment: Container App, Container Apps environment, registry/images, Log Analytics workspace if created, user-assigned identity, role assignments and any incidental resources.
- Do not assume deleting only the Container App stops all charges.
- On the agreed review date, request explicit approval before deleting resources. Keep the existing resource group if requested.
- Recheck Azure Cost Management after cleanup; charges may post with a delay.

## Judging and submission boundaries

- Current prototype has deterministic synthetic-match facts and optional Azure AI-assisted narration. The deployment script does **not** provision Azure OpenAI/Microsoft Foundry.
- No production WCAG/security certification or live Azure success is claimed before verification.
- The demo video and public repository are already linked from the Innovation Studio project. Verify any public video permissions and licensing of media separately.
- A public project listing establishes visibility, **not** independent confirmation of final judging eligibility.
