#!/usr/bin/env bash
set -euo pipefail

# Run from repository root. GHCR package remains private.
# This script intentionally does NOT build/publish a container or create an ACR.
: "${AZURE_SUBSCRIPTION_ID:?Set AZURE_SUBSCRIPTION_ID}"
: "${GHCR_IMAGE:?Set GHCR_IMAGE to a verified private ghcr.io/owner/repo:commit-sha}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-vybe-hackathon}"
LOCATION="${LOCATION:-germanywestcentral}"
APP_NAME="${APP_NAME:-vybe-demo}"
ENV_NAME="${ENV_NAME:-vybe-env}"

case "$GHCR_IMAGE" in
  ghcr.io/*:*) ;;
  *) echo "GHCR_IMAGE must be a tagged ghcr.io image" >&2; exit 1 ;;
esac

# Foundry is mandatory for the approved live hackathon release. Validate only
# presence and endpoint/deployment syntax here; never echo credentials.
# Dry runs check supplied values and report missing names without requiring secrets.
# This validation does not contact Azure or incur model usage.
python3 - <<'PY'
import os
import re
from urllib.parse import urlparse

names = (
    "VYBE_FOUNDRY_MODEL_ENDPOINT", "VYBE_FOUNDRY_MODEL_DEPLOYMENT",
    "VYBE_FOUNDRY_MODEL_KEY", "VYBE_AZURE_OPENAI_ENDPOINT",
    "VYBE_AZURE_OPENAI_DEPLOYMENT", "VYBE_AZURE_OPENAI_KEY",
)
missing = [name for name in names if not os.environ.get(name)]
if os.environ.get("CONFIRM_AZURE_DEPLOY") == "YES" and missing:
    raise SystemExit("Missing required Foundry configuration variable(s): " + ", ".join(missing))
for prefix in ("VYBE_FOUNDRY_MODEL", "VYBE_AZURE_OPENAI"):
    deployment = os.environ.get(prefix + "_DEPLOYMENT")
    if deployment and not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", deployment):
        raise SystemExit("Invalid model deployment name: " + prefix)
    if not os.environ.get(prefix + "_ENDPOINT"):
        continue
    endpoint = os.environ[prefix + "_ENDPOINT"].rstrip("/")
    parsed = urlparse(endpoint)
    if (parsed.scheme != "https" or not parsed.hostname or
        not parsed.hostname.endswith(".openai.azure.com") or
        parsed.username or parsed.password or parsed.path not in ("", "/") or
        parsed.query or parsed.fragment):
        raise SystemExit("Invalid Azure OpenAI-compatible endpoint: " + prefix)
if missing:
    print("DRY RUN: Missing Foundry variable(s): " + ", ".join(missing))
PY

if [[ "${CONFIRM_AZURE_DEPLOY:-}" != "YES" ]]; then
  printf 'DRY RUN: no Azure writes. Subscription: %s; group: %s; region: %s; app: %s; image: %s\n' \
    "$AZURE_SUBSCRIPTION_ID" "$RESOURCE_GROUP" "$LOCATION" "$APP_NAME" "$GHCR_IMAGE"
  echo "This does not verify GHCR credentials or Azure pricing."
  exit 0
fi

# Read-only checks before any Azure write.
az account show --subscription "$AZURE_SUBSCRIPTION_ID" --query id -o tsv >/dev/null
[[ "$(az group exists --name "$RESOURCE_GROUP")" == "true" ]] || { echo "Existing resource group missing" >&2; exit 1; }
[[ "$(az group show -n "$RESOURCE_GROUP" --query location -o tsv)" == "$LOCATION" ]] || { echo "Resource group region mismatch" >&2; exit 1; }
if az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" -o none 2>/dev/null; then
  echo "Existing app detected; refusing automatic replacement" >&2; exit 1
fi
# Authenticate to private GHCR before Azure writes.
: "${GHCR_USERNAME:?Set GHCR_USERNAME}"
: "${GHCR_READ_TOKEN:?Set GHCR_READ_TOKEN with read:packages}"
printf '%s' "$GHCR_READ_TOKEN" | docker login ghcr.io --username "$GHCR_USERNAME" --password-stdin >/dev/null
docker pull "$GHCR_IMAGE" >/dev/null

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
az provider register --namespace Microsoft.App --wait
if ! az containerapp env show -n "$ENV_NAME" -g "$RESOURCE_GROUP" -o none 2>/dev/null; then
  az containerapp env create -n "$ENV_NAME" -g "$RESOURCE_GROUP" -l "$LOCATION" -o none
fi
# Create using an ephemeral, owner-only configuration file rather than passing the token
# in argv. Azure stores it as a Container Apps secret referenced by the registry.
ENV_ID="$(az containerapp env show -n "$ENV_NAME" -g "$RESOURCE_GROUP" --query id -o tsv)"
export ENV_ID RESOURCE_GROUP APP_NAME GHCR_IMAGE GHCR_USERNAME GHCR_READ_TOKEN LOCATION
python3 - <<'PY'
import json
import os
import pathlib
import subprocess
import tempfile

# Prefer memory-backed storage on Linux to avoid writing credentials to disk.
tmp_root = "/dev/shm" if pathlib.Path("/dev/shm").is_dir() else None
config = {
    "location": os.environ.get("LOCATION", "germanywestcentral"),
    "properties": {
        "managedEnvironmentId": os.environ["ENV_ID"],
        "configuration": {
            "ingress": {"external": True, "targetPort": 8000, "transport": "auto"},
            "secrets": [
                {"name": "ghcr-read-token", "value": os.environ["GHCR_READ_TOKEN"]},
                {"name": "foundry-model-key", "value": os.environ["VYBE_FOUNDRY_MODEL_KEY"]},
                {"name": "azure-openai-key", "value": os.environ["VYBE_AZURE_OPENAI_KEY"]},
            ],
            "registries": [{
                "server": "ghcr.io",
                "username": os.environ["GHCR_USERNAME"],
                "passwordSecretRef": "ghcr-read-token",
            }],
        },
        "template": {
            "containers": [{
                "name": "vybe",
                "image": os.environ["GHCR_IMAGE"],
                "resources": {"cpu": 0.5, "memory": "1Gi"},
                "env": [
                    {"name": "VYBE_FOUNDRY_MODEL_ENDPOINT", "value": os.environ["VYBE_FOUNDRY_MODEL_ENDPOINT"]},
                    {"name": "VYBE_FOUNDRY_MODEL_DEPLOYMENT", "value": os.environ["VYBE_FOUNDRY_MODEL_DEPLOYMENT"]},
                    {"name": "VYBE_FOUNDRY_MODEL_KEY", "secretRef": "foundry-model-key"},
                    {"name": "VYBE_AZURE_OPENAI_ENDPOINT", "value": os.environ["VYBE_AZURE_OPENAI_ENDPOINT"]},
                    {"name": "VYBE_AZURE_OPENAI_DEPLOYMENT", "value": os.environ["VYBE_AZURE_OPENAI_DEPLOYMENT"]},
                    {"name": "VYBE_AZURE_OPENAI_KEY", "secretRef": "azure-openai-key"},
                ],
            }],
            "scale": {"minReplicas": 0, "maxReplicas": 1},
        },
    },
}
with tempfile.TemporaryDirectory(prefix="vybe-aca-", dir=tmp_root) as directory:
    path = pathlib.Path(directory) / "app.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    path.chmod(0o600)
    subprocess.run([
        "az", "containerapp", "create",
        "--name", os.environ["APP_NAME"],
        "--resource-group", os.environ["RESOURCE_GROUP"],
        "--yaml", str(path), "--output", "none",
    ], check=True)
PY
FQDN="$(az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" --query properties.configuration.ingress.fqdn -o tsv)"
printf 'Deployed at: https://%s\nHealth: https://%s/health\n' "$FQDN" "$FQDN"
