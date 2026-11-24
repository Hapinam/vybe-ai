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
