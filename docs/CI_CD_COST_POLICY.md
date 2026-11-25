# CI/CD and Zero Cloud Cost Policy

## Active repository-defined workflows

- PR Quality Gate
- CodeQL advanced setup
- GitHub Pages

GitHub-managed dynamic workflow records are separate
from these three repository-defined files.

## Required quality checks

The mandatory quality-gate check requires successful
completion of:

- API tests on Python 3.11 and 3.13.
- Frontend typechecking and production build.
- Playwright browser tests.
- Real API and browser integration tests.
- Production container build, Gitleaks secret scan,
  Trivy HIGH/CRITICAL vulnerability scan with fixes
  available, sensitive-file inspection and smoke tests.
- Independent Python and npm dependency audits.

The same locally built container image is scanned
and smoke-tested. It is not published.

Browser and full-stack failure artifacts retain their
seven-day retention. Existing full-stack API logs
remain included.

Manual execution of the complete Quality Gate remains
available for on-demand validation.

Obsolete runs for the same pull request may be cancelled.
Main-branch runs are not cancelled by this PR concurrency
policy. Pages and CodeQL workflows remain unchanged.

Dependency caches do not replace npm lockfile enforcement
or Python hash verification.

## Dependency maintenance

Routine version updates are scheduled monthly.
Compatible minor and patch updates are grouped.
Major updates remain subject to individual review.

The owner enabled Dependabot Alerts and Security Updates
on 25 November 2026. The initial alert query returned zero
open alerts; this is not a guarantee of vulnerability absence.

Security updates are not intentionally deferred to the
monthly version-update schedule. Automatic merge remains
disabled.

Python lockfile update compatibility is not yet proven.
Every Python dependency PR must be checked for consistent
runtime and test locks, hashes and successful CI.
Regenerate locks using the documented procedure when needed.

## Publication and infrastructure

Automatic GHCR publication is retired.
The historical Azure workflow is archived outside the
active workflow directory.

No new Azure deployment or paid infrastructure is authorized.
Existing registry packages are retained pending a separate
owner decision.

## Administrative baseline

The owner-provided inventory on 25 November 2026 recorded:

- GitHub Actions billable usage: USD 0.
- VYBE gross usage: USD 9.74 before discounts.
- GitHub Packages billable usage: USD 0.
- 116 Actions artifacts, approximately 2.71 MiB.
- 52 Actions caches, approximately 816.32 MiB.
- 147 private GHCR version records.
- Zero repository secrets and variables.
- GitHub Pages as the only repository environment.

Existing artifacts and caches are left to normal expiration
and eviction policies. No manual deletion is authorized.

These observations are dated snapshots, not guarantees
of future billing.

## Repository protection

The existing required quality-gate, signed commits,
pull-request rules and CodeQL scanning requirements
remain unchanged.

Historical research artifacts and application source
are outside the scope of this consolidation.
