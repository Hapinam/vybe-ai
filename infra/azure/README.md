# VYBE — Azure Container Apps Deployment

VYBE is deployed to the existing Azure Container App `vybe-app` through GitHub Actions. Do not use the legacy first-deployment scripts to update the running app.

## Current deployment path

1. `.github/workflows/pr-quality-gate.yml` runs checks on `main`.
2. `.github/workflows/publish-ghcr.yml` builds, scans and publishes the verified `main` image to the private GHCR package, tagged with the full commit SHA.
3. `.github/workflows/deploy-azure-containerapp.yml` deploys that image to the existing `vybe-app` in `rg-vybe-hackathon`, waits for a healthy revision, smoke-tests its `/health` endpoint, and then switches 100% of traffic.

The workflow requires the configured `azure-demo` environment and `AZURE_CREDENTIALS` GitHub secret. Preserve the existing Container App settings, Foundry and Azure Speech secrets, registry configuration, scale settings, and previous revision for rollback. **Merging to main can trigger this deployment chain automatically.** Check the GitHub Actions runs and environment protections before merging.

The retired `infra/azure/deploy-ghcr.sh` was a one-time app-creation script and is intentionally removed. The older `infra/azure/deploy.sh` is a separate ACR-based provisioning path, **not** the selected update path; it may create billable resources and must not be used to upgrade `vybe-app`.

## Cost and safety

- Keep GHCR private and credentials in GitHub/Azure secrets; never print or commit tokens.
- Azure Container Apps, Foundry, Speech, logging and network usage may incur charges. Azure budget alerts do not cap spending.
- Do not delete `rg-vybe-hackathon` or other Azure resources as part of cleanup without approval.
- Before deploying, verify source SHA, test results, image provenance, environment protections and expected cost.
- After deploying, verify the public HTTPS UI, `/health`, match replay, all three languages, real Azure Speech output and grounded Foundry behavior. Inspect traffic allocation and retain rollback capability.

## Security notes

The API has application-level request size and rate limits, but those are not a substitute for edge controls or cloud spending limits. Never expose Foundry/Speech credentials to the browser. Review logs and operational costs after each release.
