# Private GHCR deployment — review only

Decision: keep the GHCR package **Private**. This replaces the earlier public-image proposal. Public Azure HTTPS ingress for judges does not make the registry package public.

## Known budget and inventory (owner-provided October 18, 2026)
- Subscription: Dawood_SUB; resource group: `rg-vybe-hackathon`; region: `germanywestcentral`.
- The resource group inventory returned no resources.
- `Demo_Budget` is **EUR 10 monthly**; current reported spend EUR 0 (billing may lag). Alerts at 25%, 50%, 75%, 90%, 100%; **not** a hard spend limit.
- Separate target: approximately 500 CZK total through judging; check exchange rates, taxes, usage and logging before Azure writes.

## Publishing
- Run the manual GitHub Actions **Publish VYBE image to GHCR** only after the security checks pass.
- Leave package visibility **Private**; do not select Public in GitHub Packages.
- Tag is `ghcr.io/hapinam/vybe-ai:<full commit SHA>`. Verify package access using authenticated Docker pull.
- A GitHub token with `read:packages` and permission to access the package is required for Azure Container Apps to pull it. Prefer a dedicated, revocable, minimal-permission token and rotate it after judging. Do not put tokens in Git, tickets, chat, screenshots or CI logs.

## Azure
- `infra/azure/deploy-ghcr.sh` requires `AZURE_SUBSCRIPTION_ID`, `GHCR_IMAGE`, `GHCR_USERNAME`, and `GHCR_READ_TOKEN`.
- Dry run requires only subscription and image; it does not access Azure resources or publish anything.
- The script authenticates a local Docker pull before Azure writes, and supplies registry credentials when creating the Container App. The script does **not** put the token in Azure CLI command-line arguments. It generates an owner-only temporary JSON (valid YAML) Container Apps configuration, preferably under Linux memory-backed `/dev/shm`, with a `ghcr-read-token` application secret and `passwordSecretRef`. The file is deleted after the Azure CLI call. The token is still briefly present in process environment/memory and Azure deployment request; use a trusted host, never enable verbose shell tracing, and do not commit or share it. On hosts without `/dev/shm`, a restricted temporary file is used on disk.
- No deployment is authorized by merging this PR. `CONFIRM_AZURE_DEPLOY=YES` is an additional technical gate, **not** substitute for the owner's separate approval for billable Azure writes.
- Verify logging costs, public endpoint security and complete retention-period estimates first. After launch, test `/health`, UI and fan modes, replay and director; never claim live Foundry without validation.
