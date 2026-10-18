# VYBE — Microsoft Foundry required launch gate

**Product decision (18 October 2026): Microsoft Foundry is a required part of the live VYBE demo.** Deterministic fallback is retained for safety and local development; it does **not** satisfy the live Foundry acceptance gate.

## What exists today (verified in source)
- `apps/api/vybe/director_agent.py`: Azure OpenAI-compatible Chat Completions call selects one of three read-only match tools. Valid responses report `generation_mode=foundry_model_tool_call`. This is **model tool calling**, **not** managed Microsoft Foundry Agent Service.
- `apps/api/vybe/ai.py`: Azure OpenAI-compatible grounded goal narration. Valid responses report `generation_mode=azure_ai`.
- Both integrations require a compatible Azure OpenAI resource endpoint ending in `.openai.azure.com`; arbitrary Foundry project endpoints are not supported by these adapters.
- No real Foundry resource, model deployment, paid call or end-to-end Azure verification has been demonstrated. Do not claim otherwise.

## Recommended low-cost design (subject to portal availability and owner approval)
1. Use a Microsoft Foundry resource and a compatible **serverless Standard / Global Standard** small chat model supporting tool calls, such as `gpt-4.1-mini` if available to the subscription. Avoid provisioned throughput, dedicated GPU, managed hosted agents and paid tool sessions for this budget.
2. Deploy the compatible model in Foundry, confirm the actual Azure OpenAI endpoint and deployment name. Do not assume a generic `services.ai.azure.com` project endpoint works with the current code.
3. Supply server-side secrets to Azure Container Apps (not Vite variables, GitHub or screenshots). Both adapters need their **own** three settings; the same compatible resource/deployment may be reused after testing:
   - `VYBE_FOUNDRY_MODEL_ENDPOINT`, `VYBE_FOUNDRY_MODEL_DEPLOYMENT`, `VYBE_FOUNDRY_MODEL_KEY`
   - `VYBE_AZURE_OPENAI_ENDPOINT`, `VYBE_AZURE_OPENAI_DEPLOYMENT`, `VYBE_AZURE_OPENAI_KEY`
4. Configure secret references on the Container App revision; never place API keys in shell command arguments, source, workflow logs or browser bundles.
5. Keep `minReplicas=0`, `maxReplicas=1`, small CPU/memory, no ACR, and minimal/short-retention logging. Scale-to-zero is **not** a hard spending cap.

## Acceptance checklist — must pass before hackathon submission
- [ ] Subscription/model quota, deployment type, supported region and current **actual** token pricing checked in Foundry/Azure pricing.
- [ ] Combined forecast for Container Apps, Foundry tokens, logs, egress and tax fits **500 CZK total** through judging, not merely the existing EUR 10/month alert budget.
- [ ] Separate explicit owner approval obtained before any Azure resource creation, paid inference or secret provisioning.
- [ ] Read-only Azure inventory and preflight succeed; private GHCR remains private.
- [ ] Approved Foundry model deployment is live and reachable from the Container App.
- [ ] `/v1/matches/director/ask` returns `foundry_model_tool_call`, a permitted `selected_tool` and evidence IDs for a supported factual question.
- [ ] A supported goal narration returns `azure_ai` with validated fact IDs; unsafe or unavailable model responses fall back deterministically.
- [ ] At least one live request is demonstrated without leaking secrets, plus an intentionally disconnected fallback test.
- [ ] Live demo and documentation accurately distinguish Foundry **model integration** from managed **Agent Service**. If the judging rules explicitly require Agent Service, implement and test it separately.
- [ ] Recheck spending daily and remove resources after judging with separate deletion approval.

## Cost and architecture references
- Microsoft Foundry deployment overview: https://learn.microsoft.com/en-us/azure/foundry/concepts/deployments-overview
- Deployment types: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/deployment-types
- Agent Service overview: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview

**This document performs no Azure writes and authorizes no paid services.**


## Prelaunch request protection (October 18)

The API middleware now uses two **per-process, ASGI-peer-address** sliding-window
limits: 240 requests/minute across match endpoints and 30 requests/minute
shared by `/v1/matches/director/ask` and `/v1/matches/narrate/{event_id}`.
The latter applies before a model call and also counts toward the overall 240/minute bucket, so model traffic can reduce the available replay capacity.
`X-Forwarded-For` is deliberately ignored to avoid client-supplied spoofing.

**Important limitation:** Container Apps ingress may make many users share a
single peer bucket; these limits are not per-person quotas, distributed
counters, concurrency limits or a monetary cap. Model deployment TPM/RPM quota
and spend monitoring must be reviewed on October 21 before approval.
Do not claim the limits guarantee the 500 CZK total budget.
