# VYBE — Azure Container Apps Deployment

The first deployment is deliberately **manual**, not automatic, so Azure resources and costs remain under your control.

## Architecture
A single container runs FastAPI and serves the built React app from the same origin. The `/health` and `/v1/` routes remain API endpoints. No external database or real match feed is required for the first demo.

## Prerequisites
- Azure subscription with permission to create resources and role assignments
- Azure CLI with Container Apps extension
- Git and a local checkout of this repository
- Run `az login` and confirm `az account show`

## Deploy
Review the script before running. From the repository root:

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export RESOURCE_GROUP="rg-vybe-hackathon"
export LOCATION="germanywestcentral"
export APP_NAME="vybe-demo-unique"
export REGISTRY_NAME="globallyuniqueacrname"
bash infra/azure/deploy.sh  # safe preflight: no Azure writes
# Only after explicitly approving costs and deployment:
# export CONFIRM_AZURE_DEPLOY=YES
# bash infra/azure/deploy.sh
```

Azure Container Registry names must be globally unique, lowercase alphanumeric, 5–50 characters. Container Apps application names and environments must be valid and available within their scope.

The script **requires the existing** `rg-vybe-hackathon` resource group in `germanywestcentral` and never creates a resource group. Without `CONFIRM_AZURE_DEPLOY=YES`, it prints configuration and exits before Azure CLI calls; this is a configuration-only preflight, **not** an Azure resource or cost validation. The subscription ID and stable registry name are required even for this preflight. With explicit confirmation, it may create a Basic Azure Container Registry, Container Apps environment, user-assigned managed identity, AcrPull role, and a public ingress app with scale-to-zero. It reuses supported existing resources and refuses to replace an existing Container App. Check the Azure resources and expected costs before confirmation.

## Costs and safeguards
- Azure Container Registry Basic and the Container Apps environment's associated logging infrastructure may incur costs even when the app is scaled to zero.
- Registry builds and network egress can incur charges.
- Review Azure Pricing Calculator and set a subscription budget alert before deployment.
- The script does not delete resources or set a spending cap.
- **Do not delete `rg-vybe-hackathon`** as a cleanup shortcut: it predates this deployment and may contain other resources or settings. Inspect and remove only the individually identified demo resources after judging.
- Azure budget alerts (including the existing €10 monthly alert budget) are notifications, **not a hard spending cap**.

## Validation
Visit the deployed URL, `/health`, play the synthetic match, switch personas and verify the API calls work. The application is a prototype, not yet production hardened.

## Pre-deployment security gates
- API match endpoints reject bodies larger than **256 KiB** with HTTP 413, including streamed bodies, and limit requests to **60 per minute per ASGI peer IP** with HTTP 429. Health and static UI are exempt.
- **Important:** The in-process limiter is per worker/replica, not a shared or durable quota. It does not replace an Azure edge/WAF/API gateway rate limit, authentication, or upstream body-size cap. Configure these controls before publicly exposing paid Azure AI functionality.
- The app intentionally ignores `X-Forwarded-For` for rate-limit identity. Behind a reverse proxy, the ASGI peer may be the proxy, so many visitors could share one quota. Validate trusted proxy configuration and the observed peer IP in Azure before deciding on the production limit; never trust arbitrary client-provided forwarding headers.
- Keep Azure AI API keys in Container Apps secrets or a managed secret store; never commit keys, `.env` files, or deployment credentials. Prefer managed identity where supported.
- Before deployment, verify GitHub API tests (Python 3.11 and 3.13), web build, container smoke test, and dependency audits; review image dependencies and scan repository history for secrets. No automated full source-code security certification is claimed.
- After deployment, test HTTPS, health, API 413/429 behavior, end-to-end UI, accessibility, Azure AI fallback, logs without secrets, cost alerts, and removal of the dedicated resource group after the demo.
