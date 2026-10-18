#!/usr/bin/env bash
set -euo pipefail

# Explicit manual deployment; nothing is provisioned just by merging a PR.
# Requires: Azure CLI with containerapp extension, Docker and Azure login.
# Example:
#   AZURE_SUBSCRIPTION_ID="..." RESOURCE_GROUP="rg-vybe-demo" \
#   LOCATION="westeurope" APP_NAME="vybe-demo-unique" bash infra/azure/deploy.sh

: "${AZURE_SUBSCRIPTION_ID:?Set AZURE_SUBSCRIPTION_ID}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-vybe-hackathon}"
LOCATION="${LOCATION:-germanywestcentral}"
APP_NAME="${APP_NAME:-vybe-demo}"
ENV_NAME="${ENV_NAME:-vybe-env}"
: "${REGISTRY_NAME:?Set a stable REGISTRY_NAME explicitly}"
IMAGE_NAME="vybe:$(git rev-parse --short HEAD)"

# Explicit opt-in required before ANY Azure write.
if [[ "${CONFIRM_AZURE_DEPLOY:-}" != "YES" ]]; then
  printf 'DRY RUN: no Azure writes. Target: %s / %s / %s / %s\n' "$AZURE_SUBSCRIPTION_ID" "$RESOURCE_GROUP" "$LOCATION" "$REGISTRY_NAME"
  printf 'Set CONFIRM_AZURE_DEPLOY=YES only after reviewing resources and costs.\n'
  exit 0
fi

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
# The existing hackathon resource group must be reused, never silently created.
[[ "$(az group exists --name "$RESOURCE_GROUP")" == "true" ]] || { echo "Expected existing resource group missing" >&2; exit 1; }
[[ "$(az group show --name "$RESOURCE_GROUP" --query location -o tsv)" == "$LOCATION" ]] || { echo "Resource group region mismatch" >&2; exit 1; }
# Refuse to spend on registry builds or new resources if the app already exists.
if az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
  echo "Existing app detected: refusing automatic replacement" >&2
  exit 1
fi

az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
if ! az acr show --resource-group "$RESOURCE_GROUP" --name "$REGISTRY_NAME" --output none 2>/dev/null; then
  az acr create --resource-group "$RESOURCE_GROUP" --name "$REGISTRY_NAME" --sku Basic --admin-enabled false --output none
fi
az acr build --registry "$REGISTRY_NAME" --image "$IMAGE_NAME" .
if ! az containerapp env show --name "$ENV_NAME" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
  az containerapp env create --name "$ENV_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --output none
fi

ACR_ID="$(az acr show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)"
ACR_SERVER="$(az acr show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query loginServer -o tsv)"
IDENTITY_NAME="${APP_NAME}-pull"
if ! az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
  az identity create --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --output none
fi
IDENTITY_ID="$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)"
PRINCIPAL_ID="$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query principalId -o tsv)"
if [[ "$(az role assignment list --assignee "$PRINCIPAL_ID" --scope "$ACR_ID" --role AcrPull --query 'length(@)' -o tsv)" == "0" ]]; then
  az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --role AcrPull --scope "$ACR_ID" --output none
fi

# Azure RBAC propagation may take a few minutes after role assignment.
az containerapp create \
  --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --environment "$ENV_NAME" \
  --image "$ACR_SERVER/$IMAGE_NAME" --target-port 8000 --ingress external \
  --user-assigned "$IDENTITY_ID" --registry-server "$ACR_SERVER" --registry-identity "$IDENTITY_ID" \
  --min-replicas 0 --max-replicas 1 --cpu 0.5 --memory 1.0Gi --output none

FQDN="$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)"
printf 'Deployed at: https://%s\n' "$FQDN"
printf 'Check: https://%s/health\n' "$FQDN"
