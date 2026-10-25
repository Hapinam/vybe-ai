# VYBE Azure launch and judging runbook

> **Document status (October 25, 2026):** This document preserves historical checks and planning. Earlier references to future deployment or unverified production tests are historical, not current release status. The current deployment is in [Architecture](ARCHITECTURE.md); owner-observed production responses are in [the evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). The final video was uploaded to https://youtu.be/-pfgaeGjSN8. No CI check alone certifies Azure inference, cost, WCAG, or all devices.


**Prepared October 18, 2026. No Azure resources are provisioned by this document.**

## Deployment decision

- **Target launch:** October 22, 2026, after cost/security review and explicit approval.
- **Public availability target:** through November 21, 2026; confirm the judging window before cleanup.
- **Planning budget:** 500 CZK for the entire period; **not an enforced Azure spend cap**.
- **Existing resource group:** `rg-vybe-hackathon`; region `germanywestcentral`.
- **Runtime:** one container serving React static files and FastAPI, external HTTPS ingress on port 8000; min replicas 0, max 1.
- **AI:** a real Microsoft Foundry-hosted model is **mandatory** for the final live demo. Deterministic fallback remains for safe failures; do not claim live service until approved and verified.

## Cost model — preliminary, not a quote

Official Microsoft documentation describes Container Apps Consumption free monthly grants of **180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests per subscription**, shared with other apps in that subscription. At zero replicas, the app incurs no replica compute usage charge; other services can still bill.

The selected deployment path uses an existing **private GHCR** package rather than provisioning Azure Container Registry. ACR pricing is not part of the intended baseline; include GHCR, Container Apps, Foundry inference, logging, egress and tax in the forecast.

| Item | Planning assumption | Must verify on Oct 21 |
| --- | --- | --- |
| Private GHCR | Existing package; no new ACR planned | Package permissions, token security and any applicable GitHub charges |
| Foundry model | Pay-as-you-go token usage | Available compatible model, quota, input/output token pricing and usage estimate |
| Container Apps Consumption | May remain inside shared free grants for light traffic | Subscription's existing free-grant usage and live traffic |
| Container Apps environment | Consumption-only environment itself can be free; other profile choices differ | Actual selected environment type |
| Log Analytics | Potential ingestion and retention charges | Workspace choice, data ingestion, retention and billing |
| Other | Tax, exchange rates, egress, incidental resources | Actual cost estimate |

**No defensible exact CZK total is possible without the subscription's price sheet, region, logging choice, current usage and expected traffic.** Do not equate a 500 CZK Cost Management budget with a hard cap.

Official references:
- https://learn.microsoft.com/en-us/azure/container-apps/billing
- https://learn.microsoft.com/en-us/azure/container-apps/environment
- https://azure.microsoft.com/en-us/pricing/details/container-apps/
- https://azure.microsoft.com/en-us/pricing/calculator/

## Preflight: read-only Azure inspection

Run only after the owner chooses to perform a **read-only inspection** of the subscription. These commands are *not* the deployment and do not create resources:

```bash
az account show --query '{name:name,id:id,tenantId:tenantId}' -o json
az group show --name rg-vybe-hackathon --query '{name:name,location:location,id:id}' -o json
az resource list --resource-group rg-vybe-hackathon --query '[].{name:name,type:type,location:location}' -o table
az acr list --resource-group rg-vybe-hackathon --query '[].{name:name,sku:sku.name,admin:adminUserEnabled}' -o table # inventory only; no ACR planned
az containerapp list --resource-group rg-vybe-hackathon --query '[].{name:name,location:location}' -o table
```

Avoid putting subscription IDs, keys, or access tokens into public issues or logs. The resource inventory may be shared with redacted IDs.

## Mandatory launch gates

- [ ] Confirm current `main` commit and no unexpected deployment-code changes.
- [ ] Review actual Azure prices for region and subscription; include the **entire** retention period and reserve headroom.
- [ ] Confirm any registry, environment and Log Analytics resources that already exist, to avoid duplicate charges.
- [ ] Confirm Cost Management budget alerts; understand they **do not** stop charges.
- [ ] Check any media used in the demo for third-party trademarks, copyrighted music, and reuse rights.
- [ ] Obtain **explicit owner approval** for billable Azure writes.
- [ ] Verify the current `main` SHA, CI gate, private GHCR image, and the existing `.github/workflows/deploy-azure-containerapp.yml` deployment chain. Merging to `main` can trigger image publishing and automatic revision deployment; review GitHub environment protections, existing Foundry/Speech secrets, and expected Azure cost before merging.
- [ ] Capture deployment output and resource inventory, without secrets.

## Public launch smoke test (after deployment only)

1. Open the verified **HTTPS root URL** in a private/incognito browser session without Azure sign-in.
2. Confirm the UI loads and `/health` returns `{"status":"ok",...}`.
3. Play the synthetic match; verify final score **Aurora FC 2–2 Harbor United**.
4. Young Fan: goal celebration, glossary and goal quiz.
5. Accessible: English/Arabic/Czech captions, contrast, large text, step-by-step controls. Browser speech is optional and OS-voice-dependent.
6. Analyst: half comparison, 15-minute weighted event activity and timeline filters.
7. Verify real Foundry tool selection (`foundry_model_tool_call`) and grounded narration (`azure_ai`), plus separate fallback behavior without model access.
8. Test from a separate network/device if possible. Confirm no login is needed for judges.
9. Update **README**, **Judges' Testing Guide**, and, if supported, the Innovation Studio project page with the **actual verified URL**. Never insert a guessed URL.
10. Capture a screenshot and timestamp of the public demonstration and check the current cost.

## If deployment fails

- Stop; do not repeatedly rerun the script blindly. It can create billable resources before failing.
- Inventory what was created and identify the failure.
- Obtain approval before cleanup, reconfiguration, or another deployment attempt.
- Keep the existing resource group intact.

## Cost watch and cleanup

- Inspect costs after launch and periodically until judging concludes; billing data can lag.
- If projected charges approach the owner's limit, seek approval for mitigation immediately.
- On or after November 21, inventory **Container App, environment, Foundry model/resource, Log Analytics workspace, registry credentials and any incidental resources**, and any incidental resources.
- **Do not delete resources without explicit approval.** Deleting only the Container App may leave ongoing charges; keep the existing resource group.

## Final submission verification

- Public Innovation Studio project listing: confirmed visible October 18.
- Project description, final 75-second video (https://youtu.be/-pfgaeGjSN8), public GitHub repo and judges guide: available. Portal submission confirmation remains separate.
- Live URL: https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io — October 24 deployment CI passed; October 25 owner-observed production AI responses recorded.
- Submission/judging acceptance status: not independently confirmed by a dedicated platform status.
- Never claim live Foundry, managed Agent Service, WCAG certification, or production security certification without actual validation.
