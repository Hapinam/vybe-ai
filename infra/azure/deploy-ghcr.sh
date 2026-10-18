#!/usr/bin/env bash
set -euo pipefail

# Run from repository root. GHCR package must already be publicly pullable.
# This script intentionally does NOT build/publish a container or create an ACR.
: "${AZURE_SUBSCRIPTION_ID:?Set AZURE_SUBSCRIPTION_ID}"
: "${GHCR_IMAGE:?Set GHCR_IMAGE to a verified public ghcr.io/owner/repo:commit-sha}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-vybe-hackathon}"
LOCATION="${LOCATION:-germanywestcentral}"
APP_NAME="${APP_NAME:-vybe-demo}"
ENV_NAME="${ENV_NAME:-vybe-env}"

case "$GHCR_IMAGE" in
  ghcr.io/*:*) ;;
  *) echo "GHCR_IMAGE must be a tagged ghcr.io image" >&2; exit 1 ;;
esac

if [[ "${CONFIRM_AZURE_DEPLOY:-}" != "YES" ]]; then
  printf 'DRY RUN: no Azure writes. Subscription: %s; group: %s; region: %s; app: %s; image: %s\n' \
    "$AZURE_SUBSCRIPTION_ID" "$RESOURCE_GROUP" "$LOCATION" "$APP_NAME" "$GHCR_IMAGE"
  echo "This does not verify GHCR image visibility or Azure pricing."
  exit 0
fi

# Read-only checks before any Azure write.
az account show --subscription "$AZURE_SUBSCRIPTION_ID" --query id -o tsv >/dev/null
[[ "$(az group exists --name "$RESOURCE_GROUP")" == "true" ]] || { echo "Existing resource group missing" >&2; exit 1; }
[[ "$(az group show -n "$RESOURCE_GROUP" --query location -o tsv)" == "$LOCATION" ]] || { echo "Resource group region mismatch" >&2; exit 1; }
if az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" -o none 2>/dev/null; then
  echo "Existing app detected; refusing automatic replacement" >&2; exit 1
fi
# Do not provision against a private GHCR package: unauthenticated manifest must be accessible.
# Docker pull also verifies architecture/manifest availability before billable Azure writes.
docker pull "$GHCR_IMAGE"

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
az provider register --namespace Microsoft.App --wait
if ! az containerapp env show -n "$ENV_NAME" -g "$RESOURCE_GROUP" -o none 2>/dev/null; then
  az containerapp env create -n "$ENV_NAME" -g "$RESOURCE_GROUP" -l "$LOCATION" -o none
fi
az containerapp create \
  -n "$APP_NAME" -g "$RESOURCE_GROUP" --environment "$ENV_NAME" \
  --image "$GHCR_IMAGE" --target-port 8000 --ingress external \
  --min-replicas 0 --max-replicas 1 --cpu 0.5 --memory 1.0Gi -o none
FQDN="$(az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)"
printf 'Deployed at: https://%s\nHealth: https://%s/health\n' "$FQDN" "$FQDN"
