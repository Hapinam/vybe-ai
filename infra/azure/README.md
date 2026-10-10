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
export RESOURCE_GROUP="rg-vybe-demo"
export LOCATION="westeurope"
export APP_NAME="vybe-demo-unique"
export REGISTRY_NAME="globallyuniqueacrname"
bash infra/azure/deploy.sh
```

Azure Container Registry names must be globally unique, lowercase alphanumeric, 5–50 characters. Container Apps application names and environments must be valid and available within their scope.

The script provisions a resource group, Basic Azure Container Registry, Container Apps environment, user-assigned managed identity, AcrPull role, and a public ingress app with scale-to-zero.

## Costs and safeguards
- Azure Container Registry Basic and the Container Apps environment's associated logging infrastructure may incur costs even when the app is scaled to zero.
- Registry builds and network egress can incur charges.
- Review Azure Pricing Calculator and set a subscription budget alert before deployment.
- The script does not delete resources or set a spending cap.
- To delete **all resources in the dedicated demo resource group** after judging, review the group contents and run:
  `az group delete --name rg-vybe-demo`
- Do not delete a shared resource group.

## Validation
Visit the deployed URL, `/health`, play the synthetic match, switch personas and verify the API calls work. The application is a prototype, not yet production hardened.
