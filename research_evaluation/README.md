# VYBE Research and Evaluation

This directory preserves historical research and evaluation
artifacts created during the development of VYBE.

## Directory Structure

| Directory | Purpose | Preserved artifacts |
|---|---|---:|
| model/ | Model benchmarking, contract evaluation and Foundry evidence | 38 |
| security/ | Security and robustness evaluation | 12 |
| speech/ | Speech generation and voice evaluation | 29 |

## Preservation Policy

The 78 original research artifacts are preserved byte-for-byte in
[the original archival commit](https://github.com/Hapinam/vybe-ai/tree/dd8ffe61131963646486aacca418c8cac8f69164/research_evaluation).
The current tree retains 77 unchanged originals and one security-hardened
script (`speech/scripts/vybe_discover_azure_voices.py`), which no longer
prints individual authenticated service response fields to the console.
Its JSON output is unchanged in structure. The original remains available
in Git history for historical integrity.

These artifacts represent historical experiments and
should not be interpreted as current production benchmarks,
supported operational procedures, or release guarantees.

## Execution Safety

These scripts are not part of the current application
runtime, deployment process, or supported test suite.

Some historical scripts may modify application source
files, tests, or configuration when executed.

Review each script before execution and use an isolated
environment rather than an active development worktree.

## Cloud Dependencies and Costs

Some historical experiments require Azure services,
Azure CLI authentication, external model providers,
or locally installed Ollama models.

Executing these experiments may create cloud usage costs
or require access to resources that no longer exist.

Do not execute cloud-dependent scripts without reviewing
their authentication requirements and potential costs.

## Security and Privacy

Historical artifacts must be reviewed before redistribution.

Never commit credentials, access tokens, API keys,
or sensitive personal information.

## Licensing and Redistribution

Preservation does not establish redistribution rights.

Third-party datasets, generated outputs, service-specific
materials, and model-related artifacts may be subject to
separate licensing or contractual restrictions.

Public redistribution requires an appropriate review.

## Historical Status

These materials are retained for research traceability,
reproducibility, and historical reference.

They are not maintained production components.

## Current research inventory

The current archive contains 79 historical artifacts:
77 unchanged original artifacts, one security-hardened
original script and one subsequently preserved Foundry
evidence file.

The detailed Foundry evidence was added through
[PR #131](https://github.com/Hapinam/vybe-ai/pull/131).

Documentation and .gitattributes are excluded from
the historical artifact count.

See [Research Findings](FINDINGS.md) for methodology,
results, limitations and links to the original evidence.

## Additional execution precautions

VYBE_generate_new_voice.py uses Azure CLI authentication
to obtain service credentials and may incur Azure costs.

Some historical model scripts accept configurable
base URLs. Do not assume that every experiment is
restricted to loopback or operates without network access.

Review endpoints, authentication, subprocess behavior
and file-writing behavior before execution.

The historical Azure resources have been retired.
Their preservation in research documentation does not
authorize recreating or using those services.
