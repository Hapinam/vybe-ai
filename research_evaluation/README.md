# VYBE Research and Evaluation

This directory preserves historical research and evaluation
artifacts created during the development of VYBE.

## Directory Structure

| Directory | Purpose | Original files |
|---|---|---:|
| model/ | Model benchmarking and contract evaluation | 37 |
| security/ | Security and robustness evaluation | 12 |
| speech/ | Speech generation and voice evaluation | 29 |

## Preservation Policy

The 78 original research artifacts are preserved without
content modifications to maintain historical integrity.

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
