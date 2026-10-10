#!/usr/bin/env bash
set -euo pipefail

# Explicit manual deployment; nothing is provisioned just by merging a PR.
# Requires: Azure CLI with containerapp extension, Docker and Azure login.
# Example:
#   AZURE_SUBSCRIPTION_ID="..." RESOURCE_GROUP="rg-vybe-demo" \
#   LOCATION="westeurope" APP_NAME="vybe-demo-unique" bash infra/azure/deploy.sh

: "${AZURE_SUBSCRIPTION_ID:?Set AZURE_SUBSCRIPTION_ID}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-vybe-demo}"
LOCATION="${LOCATION:-westeurope}"
APP_NAME="${APP_NAME:-vybe-demo}"
ENV_NAME="${ENV_NAME:-vybe-env}"
REGISTRY_NAME="${REGISTRY_NAME:-vybeacr$RANDOM$RANDOM}"
IMAGE_NAME="vybe:$(git rev-parse --short HEAD)"

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az acr create --resource-group "$RESOURCE_GROUP" --name "$REGISTRY_NAME" --sku Basic --admin-enabled false --output none
az acr build --registry "$REGISTRY_NAME" --image "$IMAGE_NAME" .
az containerapp env create --name "$ENV_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --output none

ACR_ID="$(az acr show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)"
ACR_SERVER="$(az acr show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query loginServer -o tsv)"
IDENTITY_NAME="${APP_NAME}-pull"
az identity create --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --output none
IDENTITY_ID="$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)"
PRINCIPAL_ID="$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query principalId -o tsv)"
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --role AcrPull --scope "$ACR_ID" --output none

# Azure RBAC propagation may take a few minutes after role assignment.
az containerapp create \
  --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --environment "$ENV_NAME" \
  --image "$ACR_SERVER/$IMAGE_NAME" --target-port 8000 --ingress external \
  --user-assigned "$IDENTITY_ID" --registry-server "$ACR_SERVER" --registry-identity "$IDENTITY_ID" \
  --min-replicas 0 --max-replicas 1 --cpu 0.5 --memory 1.0Gi --output none

FQDN="$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)"
printf 'Deployed at: https://%s\n' "$FQDN"
printf 'Check: https://%s/health\n' "$FQDN"
