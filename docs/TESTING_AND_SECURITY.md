# Testing and security

## Local checks

From `apps/api`, after installing the test extras: `python -m pytest -q` using the project virtual environment. CI tests Python 3.11 and 3.13.

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

The replay bulk endpoint docstring incorrectly mentions kickoff inclusion (actual behavior is post-event snapshots only). Consider consistent `npm ci` in web-build, reducing duplicate CI work, and reviewing ignore patterns for sensitive/local artifacts in a separate engineering PR. No code or workflow changes are required for documentation closure.

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
