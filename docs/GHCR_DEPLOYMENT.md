# GHCR image publication — retained, Azure deployment retired

**Current status (November 2026):** GHCR publishing remains configured. The original Azure Container Apps deployment is retired; publishing a container image does **not** make it publicly accessible as a running Azure service.

## Build and publish

`.github/workflows/publish-ghcr.yml` runs after a successful `PR Quality Gate` workflow run for a push to `main`. It downloads and verifies the tested workflow's image-publication decision. **Documentation-only changes are excluded from image publication**. For qualifying changes, it verifies the tested SHA is still `main`, reruns backend tests, scans for secrets and vulnerabilities, and publishes `ghcr.io/hapinam/vybe-ai:<full-commit-sha>` to the GHCR package (historically intended to be private; current visibility must be checked separately).

The exclusion covers `docs/**`, root README and CONTRIBUTING, and the API, web, demo and Azure README files. Quality checks still run. Web README changes may also trigger a Pages rebuild. Gitleaks scans the working tree without Git history; Trivy gates HIGH/CRITICAL findings with fixes available (`--ignore-unfixed`). See [testing and security](TESTING_AND_SECURITY.md).

## Azure deployment: historical workflow only

`.github/workflows/deploy-azure-containerapp.yml` uses **manual `workflow_dispatch` only**, requiring a full image SHA and explicit `DEPLOY` confirmation. It is **not** triggered by GHCR publication or merges.

The Azure app and related resources were deleted after the hackathon; the workflow was disabled operationally and its `azure-demo` environment and credentials removed. **Do not enable or run it** without a separately approved new infrastructure plan and restored safeguards. The retained workflow file does not mean Azure is available.

## Costs and evidence

GHCR image storage/publication is distinct from hosting. Provisioning new Azure Container Apps, AI model endpoints, Speech, monitoring, or network services may incur costs. Budgets are alerts, not hard caps.

Historical Azure deployment documentation is retained in [the archive](archive/infra/azure/README.md). For the active portfolio and local runtime see [architecture](ARCHITECTURE.md) and [root README](../README.md). No live Foundry inference is claimed for the current GitHub Pages portfolio.
