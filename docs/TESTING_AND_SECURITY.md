# Testing and security

## Local checks

From `apps/api`, after installing requirements-test.lock with --require-hashes and the application with --no-deps: `python -m pytest -q` using the project virtual environment. CI tests Python 3.11 and 3.13.

From `apps/web`, use Node.js 22, `npm.cmd ci`, `npm.cmd run build`, `npx.cmd playwright install chromium` and `npx.cmd playwright test`. The normal configuration excludes the real API smoke test. With FastAPI running on port 8000, run `npx.cmd playwright test --config=playwright.fullstack.config.ts` separately. Clear static mode and use a clean deterministic environment. Browser speech tests mock speech; they do not verify audible output.

## Coverage and evidence

The reviewed baseline contains 22 API test modules and 10 browser test modules. Tests cover replay, input validation, grounding, provider routing/failures, temporal and shootout boundaries, rate limits, speech formatting, personas, storage failure and real API integration. This is a test inventory, not measured code coverage. The closure review did not rerun the suites. Prior CI results and owner manual checks are separate evidence.

## Security boundaries

- Per-process ASGI-peer rate limits: 240 requests/minute shared by `/v1/matches/*` and an additional 30/minute shared by director/ask, narrate and speech routes; `/health` is exempt; 256 KiB request body limit. Not distributed quotas or cost caps.
- Read-only allowlisted tools and verified fact segments; deterministic fallback. No arbitrary model commands.
- Ollama loopback HTTP restriction, no redirects or proxies.
- Gitleaks working-tree scan (`--no-git`), Trivy HIGH/CRITICAL with `--ignore-unfixed`, sensitive-file checks, Python/npm dependency audits and CodeQL. These do not certify absence of vulnerabilities or historical secrets.
- Never commit credentials or place them in frontend `VITE_` variables.

## Deferred maintenance

The replay bulk endpoint docstring incorrectly mentions kickoff inclusion (actual behavior is post-event snapshots only). Consider consistent `npm ci` in web-build and reducing duplicate CI work. Ignore hardening was subsequently implemented in PR #134. No code or workflow changes are required for documentation closure.

See [GHCR policy](GHCR_DEPLOYMENT.md) and [local development](LOCAL_DEVELOPMENT.md).

## Outbound HTTP security hardening — 2026-11-25

This maintenance change addresses FSEC-01, FSEC-02 and FSEC-04
from the final repository security audit.

### Transport controls

Azure AI narration, Azure Speech and the local Ollama adapter
use a shared HTTP opener that rejects redirects and disables
implicit proxy configuration.

Azure AI endpoints must use HTTPS with the default port or
explicit port 443, in addition to existing hostname and URL
validation requirements.

Environments requiring an outbound HTTP proxy are not supported
by these adapters without an explicitly reviewed transport change.

### Response limits

| Integration | Maximum response | Request timeout |
| --- | ---: | ---: |
| Azure AI narration | 65,536 bytes | 8 seconds |
| Azure Speech | 2,000,000 bytes | 12 seconds |
| Local Ollama director | 32,768 bytes | 30 seconds |

Azure AI responses exceeding the byte limit are rejected before
JSON parsing. Existing narration content validation and
deterministic fallback behavior remain in place.

The Azure AI byte limit is a defensive engineering threshold,
not a limit derived from live provider measurements.

### Sensitive error handling

Azure AI failure logs retain fixed diagnostic messages and
exception class names without raw exception messages or
tracebacks.

Azure Speech provider failures return a generic HTTP error
without displaying the underlying exception chain.

### Local verification

Validation was performed using Python 3.11 in a temporary
Docker image, with the API source mounted read-only and
container networking disabled during test execution.

| Test suite | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Focused security and adapter tests | 134 | 0 | 0 |
| Full API test suite | 335 | 0 | 0 |

The focused suite is included in the full API suite; these
counts are not additive.

Regression coverage includes response-size boundaries,
redirect rejection, proxy isolation, endpoint port validation,
sensitive exception handling and deterministic fallback.

No live Azure or Ollama requests were made. Live provider
compatibility and production behavior were not independently
validated by this test run.

The temporary test image was removed after execution.
Dependency versions were resolved from the existing project
version ranges rather than a fully pinned dependency lockfile.

## Supply Chain Security

GitHub Actions are pinned to full commit SHAs, with the
original version tags retained in comments.

Production Docker base images are pinned to registry
SHA256 digests.

Python application dependencies are recorded in:

- `apps/api/requirements.lock`: runtime dependencies.
- `apps/api/requirements-test.lock`: runtime and test dependencies.

Both files include direct and transitive package versions
and SHA256 distribution hashes. Runtime package versions
must match between the two lockfiles.

Docker and API CI installation enforce package hashes
using `pip install --require-hashes`. The local application
package is installed separately using `--no-deps`.

Dependency auditing includes the test lockfile, which
also contains the runtime dependency set.

### Dependency maintenance

- Keep pyproject.toml as the dependency declaration source.
- Regenerate both lockfiles using pip-tools 7.5.2 on
  Linux with Python 3.11.
- Resolve the test lockfile against the runtime lockfile.
- Review package version and hash changes.
- Run API tests on Python 3.11 and 3.13.
- Run dependency auditing and production container builds.
- Review Dependabot proposals before merging.

For a Linux development environment, install from
requirements-test.lock using --require-hashes, then
install the application using --no-deps.

### Reproducibility limitations

Lockfiles were generated on Linux with Python 3.11.
Other platforms and Python versions require validation.

Build-system dependencies, audit tooling, operating
system packages and transitive GitHub Action internals
are not comprehensively pinned by this change.

Dependabot recognition and automatic regeneration of
the new lockfiles require separate verification.

These controls improve supply chain integrity but do
not guarantee bit-for-bit reproducible builds.

### Supply chain validation evidence

Local validation on 2026-11-25:

- 16 unique GitHub Action version references pinned.
- 12 workflow files updated.
- Two production Docker base images pinned.
- 14 runtime and 25 combined runtime/test packages locked.
- Python 3.11: 335 API tests passed in 2.21 seconds.
- Python 3.13: 335 API tests passed in 2.74 seconds.
- Hash-enforced dependency installation passed.
- Locked dependency audit reported no known vulnerabilities.
- Production Docker build passed.
- Production pip check reported no broken requirements.
- All four temporary validation images were removed.

The API tests ran without network access. No Azure resources
were created or used.

The GHCR publication test step also uses the test lockfile.
That workflow integration and the final audit workflow
adjustments require GitHub CI validation.

The vulnerability audit is point-in-time evidence, not
a guarantee of the absence of vulnerabilities.

## Repository and runtime hardening

FSEC-03, FSEC-08 and FSEC-10 address bounded local rate
limiter state and defensive repository exclusions.

Each rate limiter dictionary tracks at most 1024 peers
by default. Expired peer entries are reclaimed when
capacity is needed. New peers receive HTTP 429 when
capacity is exhausted and no expired entries are available.

Existing request and model-route limits remain unchanged.
Rejection responses are sent outside the rate limiter lock.

The peer capacity is a defensive engineering threshold,
not a measured production capacity.

Distributed rate limiting is intentionally deferred for
the current portfolio and local demonstration scope.
It must be reconsidered before public multi-instance
deployment. The local limiter is not a global cost cap.

Git and Docker ignore rules exclude additional sensitive
and generated files. Historical research artifacts remain
in Git but are excluded from the Docker build context.

Ignore rules are defense in depth. They do not remove
previously committed secrets or replace secret scanning.

### Repository and runtime validation evidence

Local validation on 2026-11-25:

- Python 3.11: 344 API tests passed in 2.03 seconds.
- Python 3.13: 344 API tests passed in 2.69 seconds.
- Nine new regression test cases passed.
- Git ignore checks passed for selected sensitive and
  generated paths.
- No tracked files matched the effective Git ignore rules.
- Docker context verification confirmed exclusion of
  research_evaluation and .git while retaining required
  application source and dependency lockfiles.
- Production Docker build passed.
- Production pip check reported no broken requirements.
- All four temporary validation images were removed.

Tests used locked dependencies and digest-pinned Python
images. API tests ran without network access.

These results do not establish production load capacity,
distributed quota enforcement or comprehensive coverage
of every sensitive-file naming convention.

No research artifacts were modified and no Azure resources
were created or used.

## Consolidated audit status

See the [final security audit](SECURITY_AUDIT_REPORT.md)
for all 12 scoped findings, merged implementation PRs,
historical verification evidence and accepted limitations.

The earlier test inventory and closure observations in
this document are historical. The latest local API suite
recorded here contains 344 passing tests per Python version.
