# PR 62 — Full-stack smoke and Foundry/Azure validation gates

This PR adds a **separate** CI job that runs a real FastAPI process, Vite and Chromium. Unlike existing mocked Playwright E2E tests, the smoke test calls actual replay/insights/Director endpoints through the Vite proxy. The new test uses deterministic fallback with all Foundry model environment variables explicitly empty. It does **not** prove a real Azure or Foundry deployment.

## Local verification

From the repository root, in separate terminals:

```bash
cd apps/api
python -m pip install -e .
python -m uvicorn vybe.main:app --host 127.0.0.1 --port 8000
```

```bash
cd apps/web
npm ci
npx playwright install chromium
npx playwright test --config=playwright.fullstack.config.ts
```

The test checks: real API health, UI replay to fulltime, Studio evidence and analyst persona, direct Director endpoint fallback with exact evidence IDs, and absence of API errors. The CI workflow installs Chromium and starts the API itself. No model credentials are required or used.

## Preflight: no paid resources

1. Inspect existing resources using read-only commands in `docs/LAUNCH_READINESS_AUDIT.md`.
2. Choose a real Foundry-hosted Azure OpenAI deployment **only after** the owner approves its cost; record model name, region, API compatibility, per-token pricing and quota.
3. Set a conservative spend plan for ACR Basic, Container Apps, Log Analytics, model tokens, build operations and applicable tax. Budget alerts are not hard caps.
4. The current adapter supports **Azure OpenAI-compatible model tool calling**; it is not a managed Microsoft Foundry Agent Service agent. Do not mislabel it in the submission.
5. Do not execute `CONFIRM_AZURE_DEPLOY=YES` or create any billable Azure resources without explicit owner approval.
6. Verify the public HTTPS demo, browser accessibility, server-side secrets, failure fallback and cleanup plan after approved deployment.

**No deployment, cloud model invocation or PR merge is performed by this PR.**
