# GHCR publication and Azure deployment — retired

## Current maintenance policy

Automatic GHCR publication has been removed from the
active CI/CD design. No manual publication workflow is
provided.

The previous publication workflow remains recoverable
from Git history. Existing registry versions are not
deleted by this repository change.

The owner inventory on 25 November 2026 identified a
private GHCR package with 147 versions: 49 tagged and
98 untagged. These are registry records, not necessarily
147 independent container images.

Package deletion was subsequently authorized and completed under CI-18 Option A. See the closure evidence below.

## Azure deployment

The original Azure deployment has been retired.

The historical deployment workflow is preserved at
[deploy-azure-containerapp.yml](archive/ci-cd/deploy-azure-containerapp.yml).
It is outside the active GitHub Actions workflow directory.

Do not restore or execute this workflow without a separately
approved infrastructure plan, credentials and cost controls.

## Local container execution

The application can still be built locally from the
repository Dockerfile. See [local development](LOCAL_DEVELOPMENT.md).

CI continues to build, scan and smoke-test the production
container without publishing it.

## Cost policy

No paid hosting or new Azure resources are authorized.
GitHub Pages and standard public-repository CI remain
part of the portfolio maintenance design.

Optional Azure integrations and historical research
scripts may incur charges if explicitly configured and run.

Zero cost is a maintenance target, not a guarantee
against future pricing changes or external service usage.


## Final registry disposition

The owner authorized deletion of the complete private VYBE
container package (ID 16021674), accepting loss of its historical
registry versions and confirming no external consumers.

The owner-executed GitHub CLI verification confirmed deletion
and absence from active inventory, with all 147 historical
version records accounted for.

Repository content and release inventory remained unchanged.
The temporary package-deletion permission was removed.

See [CI/CD closure evidence](CI_CD_COST_POLICY.md).

No registry publication or paid deployment is authorized.
Local container builds remain available from source.
