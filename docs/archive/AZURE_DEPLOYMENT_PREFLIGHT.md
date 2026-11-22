# Azure deployment — current status

> **ARCHIVED — HISTORICAL REFERENCE ONLY (November 2026)**
>
> This document describes the original VYBE hackathon implementation, validation, planning, or submission. It is not an active deployment or testing instruction. The Azure deployment has been retired; the current public portfolio is a static GitHub Pages demonstration. See the [current README](../../README.md) and [architecture](../ARCHITECTURE.md).

VYBE is already deployed to an Azure Container App. This page describes the deployed setup; it is not a pre-deployment approval checklist.

- **Live application:** https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io
- **Runtime:** One container image serving the React frontend and FastAPI backend.
- **Release path:** GitHub Actions → private GHCR image → existing Azure Container App.
- **Microsoft Foundry:** Server-side model-assisted Ask the Match and grounded narration, with deterministic fallbacks.
- **Azure AI Speech:** Server-side audio synthesis, with browser speech fallback.

The legacy `infra/azure/deploy.sh` provisions infrastructure and is **not** the release path for the existing application. See [deployment details](infra/azure/README.md) and [architecture](../ARCHITECTURE.md).

**Production freeze:** Merging changes into `main`, including documentation-only changes, can start the deployment workflow. Do not merge during judging without explicit owner approval.
