# Private GHCR deployment — current pipeline

VYBE uses a **private GHCR package** and an existing Azure Container App, `vybe-app`, in resource group `rg-vybe-hackathon` (`germanywestcentral`).

## Build and publish

`.github/workflows/publish-ghcr.yml` is triggered after a successful `main` PR Quality Gate on a push. It reruns backend tests, scans for secrets and vulnerabilities, and publishes `ghcr.io/hapinam/vybe-ai:<full-commit-sha>`. The workflow verifies that the tested SHA is still the current `main` before publishing. Keep the GHCR package private.

## Deploy

`.github/workflows/deploy-azure-containerapp.yml` runs after a successful publish on `main`, uses the `azure-demo` GitHub environment and `AZURE_CREDENTIALS` secret, verifies the published SHA is still `main`, updates the existing app to a new revision, waits for healthy provisioning, tests `/health`, and then directs 100% traffic to that revision.

**Merging into `main` may therefore automatically deploy.** Check workflow status and environment protections before approving a merge. Do not run legacy first-time provisioning scripts to update the app. The retired `infra/azure/deploy-ghcr.sh` was removed because the app already exists.

## Configuration, cost and validation

Preserve the existing Azure Container App registry credentials and Foundry/Speech configuration; the update workflow is not a secret-provisioning workflow. Keep credentials in Azure/GitHub secrets, never source control or logs. Verify real Foundry model availability and Azure Speech playback separately from CI. The private GHCR image avoids an additional ACR for this path, but inference, speech, Container Apps, logging and network traffic may incur costs. Cost Management budgets are alerts, not hard caps.

After deployment, verify the image SHA, active revision, traffic split, HTTPS UI, `/health`, replay, personas, language output and rollback revision. See `docs/FOUNDRY_REQUIRED_LAUNCH.md` for Foundry-specific acceptance criteria.
