# VYBE — Azure Container Apps Deployment

The first deployment is deliberately **manual**, not automatic, so Azure resources and costs remain under your control.

## Architecture
A single container runs FastAPI and serves the built React app from the same origin. The `/health` and `/v1/` routes remain API endpoints. No external database or real match feed is required for the first demo.

## Prerequisites
- Azure subscription with permission to create resources and role assignments
- Azure CLI with Container Apps extension
- Git and a local checkout of this repository
- Run `az login` and confirm `az account show`

## Deploy — preferred private GHCR path

Use `infra/azure/deploy-ghcr.sh` from the repository root. It uses the existing private GHCR image rather than creating Azure Container Registry, and requires the existing resource group `rg-vybe-hackathon` in `germanywestcentral`.

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export GHCR_IMAGE="ghcr.io/hapinam/vybe-ai:<verified-full-main-commit-sha>"
export RESOURCE_GROUP="rg-vybe-hackathon"
export LOCATION="germanywestcentral"
bash infra/azure/deploy-ghcr.sh  # no Azure writes
```

The dry-run validates image syntax and supplied Foundry endpoint/deployment values and reports missing Foundry variable names; it does not require credentials or contact Azure. The approved deployment also requires `GHCR_USERNAME`, `GHCR_READ_TOKEN` (with `read:packages` and package access), plus `VYBE_FOUNDRY_MODEL_ENDPOINT`, `VYBE_FOUNDRY_MODEL_DEPLOYMENT`, `VYBE_FOUNDRY_MODEL_KEY`, `VYBE_AZURE_OPENAI_ENDPOINT`, `VYBE_AZURE_OPENAI_DEPLOYMENT`, and `VYBE_AZURE_OPENAI_KEY`. Both endpoints must be HTTPS Azure OpenAI resource roots ending in `.openai.azure.com`.

The script validates Azure subscription/group, pulls the private image locally, and creates a Container Apps environment if needed plus a public app. It injects model and registry credentials as app secrets and refuses to replace an existing app. **Do not set `CONFIRM_AZURE_DEPLOY=YES` without separate explicit owner approval for spending and provisioning.** Never run with shell tracing (`bash -x`) when secrets are present.

The older `infra/azure/deploy.sh` is an **alternative ACR-based path**, not the selected launch path. It may create additional billable resources.

## Costs and safeguards
- The selected GHCR path avoids creating Azure Container Registry; Container Apps logging infrastructure may still incur costs at zero replicas.
- Foundry tokens, logging, network egress and applicable GitHub package usage may incur charges.
- Review Azure Pricing Calculator and set a subscription budget alert before deployment.
- The script does not delete resources or set a spending cap.
- **Do not delete `rg-vybe-hackathon`** as a cleanup shortcut: it predates this deployment and may contain other resources or settings. Inspect and remove only the individually identified demo resources after judging.
- Azure budget alerts (including the existing €10 monthly alert budget) are notifications, **not a hard spending cap**.

## Validation
Visit the deployed URL, `/health`, play the synthetic match, switch personas and verify the API calls work. The application is a prototype, not yet production hardened.

## Pre-deployment security gates
- API match endpoints reject bodies larger than **256 KiB** with HTTP 413, including streamed bodies, and limit requests to **240 per minute per ASGI peer IP**, plus a shared **30 per minute** bucket for model-capable endpoints with HTTP 429. Health and static UI are exempt.
- **Important:** The in-process limiter is per worker/replica, not a shared or durable quota. It does not replace an Azure edge/WAF/API gateway rate limit, authentication, or upstream body-size cap. Configure these controls before publicly exposing paid Azure AI functionality.
- The app intentionally ignores `X-Forwarded-For` for rate-limit identity. Behind a reverse proxy, the ASGI peer may be the proxy, so many visitors could share one quota. Validate trusted proxy configuration and the observed peer IP in Azure before deciding on the production limit; never trust arbitrary client-provided forwarding headers.
- Keep Azure AI API keys in Container Apps secrets or a managed secret store; never commit keys, `.env` files, or deployment credentials. Prefer managed identity where supported.
- Before deployment, verify GitHub API tests (Python 3.11 and 3.13), web build, container smoke test, and dependency audits; review image dependencies and scan repository history for secrets. No automated full source-code security certification is claimed.
- After deployment, test HTTPS, health, API 413/429 behavior, end-to-end UI, accessibility, Azure AI fallback, logs without secrets, cost alerts, and separately approved cleanup of individually identified resources; never delete the existing resource group as a shortcut.
