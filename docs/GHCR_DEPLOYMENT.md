# Cost-conscious GHCR deployment (review only)

This path replaces the ACR dependency with a **public GHCR package**, but does not guarantee a free Azure deployment. The original ACR script remains available for comparison. Neither workflow nor script provisions Azure on merge.

## Current subscription inventory (owner-provided, 2026-10-18)
- Subscription: `Dawood_SUB` (do not commit subscription IDs).
- Resource group: `rg-vybe-hackathon`, `germanywestcentral`.
- `az resource list`, `az acr list` and `az containerapp list` returned no resources in the group.
- Monthly `Demo_Budget` amount 10.0, **currency not yet verified**. Budget alerts are not spending limits.
- Total target: **500 CZK** including all services through the planned judging availability window.

## Publication (no Azure charges; manual action)
1. Confirm repository code and Docker image contents are suitable for public distribution.
2. Run GitHub Actions **Publish VYBE image to GHCR** via `workflow_dispatch` only after approving publication. It publishes `ghcr.io/hapinam/vybe-ai:<full-main-commit-sha>`.
3. In GitHub Packages, set the container package visibility to **Public** if it is initially private. This is a deliberate public distribution decision.
4. Verify an **unauthenticated** `docker pull ghcr.io/hapinam/vybe-ai:<full-main-commit-sha>` succeeds. A private package will not work with this deployment path. Never store a PAT in a public workflow or command log.
5. Confirm the published image is from the intended `main` commit. Workflow may be run from other refs, so inspect the run ref.

## Azure deployment — requires a separate, explicit owner approval
Review actual subscription costs and current spend, the Consumption environment/logging configuration, billing currency, budget notifications and total retention period first. The environment may create or use logging services; GHCR only removes ACR charges.

From a Bash shell at the repository root, after explicit approval:
```bash
export AZURE_SUBSCRIPTION_ID="<subscription ID, local only>"
export GHCR_IMAGE="ghcr.io/hapinam/vybe-ai:<verified full commit SHA>"
bash infra/azure/deploy-ghcr.sh   # DRY RUN, no Azure writes
# Only after separate approval for Azure resources and cost:
CONFIRM_AZURE_DEPLOY=YES bash infra/azure/deploy-ghcr.sh
```
Do not run the final command just because this file exists. Script refuses replacing an existing Container App, uses min replicas 0 and max 1, and does not create an ACR. It may still create a Container Apps environment, associated logging resources and a billable public Container App. A failed deployment can leave resources charging; inventory them before retrying.

After launch, verify public HTTPS root, `/health`, all fan modes, Ask the Match, and the 2–2 replay. Update judges links only with a verified URL. Get explicit approval before deleting resources after judging.
