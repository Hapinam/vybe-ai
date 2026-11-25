# VYBE — Research Findings

This document summarizes preserved historical experiments.
It does not replace or modify their original evidence.

## Research objectives

VYBE investigated grounded model tool selection, application
contract compliance, robustness against unsupported requests,
and multilingual football narration.

The deterministic synthetic match engine remains the source
of truth for match facts. Models are not trusted to invent
scores, events or tactical explanations.

## HTTP application contract evaluation

The preserved benchmark contains 20 models, 12 cases per
model and 240 recorded executions.

The original Qwen result was combined with the results of
19 additional models using the same HTTP benchmark script.

Warm median latency excludes case H01, as implemented by
the historical runner.

| Model | Passed | Total | Warm median (s) |
| --- | ---: | ---: | ---: |
| qwen3-coder:30b | 12 | 12 | 1.333 |
| gemma4:12b-it-q4_K_M | 12 | 12 | 7.561 |
| granite4.2:8b-q4_K_M | 11 | 12 | 3.725 |
| gemma4:26b | 11 | 12 | 5.359 |
| gpt-oss:20b | 10 | 12 | 12.173 |
| ministral-3:14b-instruct-2512-q4_K_M | 9 | 12 | 3.692 |
| nemotron-3.5-bolt:e4b | 9 | 12 | 4.558 |
| qwen3.5:9b | 9 | 12 | 9.907 |
| qwen3.8:27b | 8 | 12 | 31.371 |
| nemotron-3-nano-gpu:latest | 6 | 12 | 3.599 |
| nemotron-3-nano:4b | 6 | 12 | 4.558 |
| d3:4b | 2 | 12 | 0.015 |
| d1:latest | 2 | 12 | 0.027 |
| clef-flash:latest | 2 | 12 | 0.029 |
| nimble:latest | 2 | 12 | 0.03 |
| kev:latest | 2 | 12 | 0.033 |
| pplx-decider:latest | 2 | 12 | 0.035 |
| phi4-reasoning:14b-plus-q8_0 | 2 | 12 | 0.035 |
| tev1:4b | 2 | 12 | 0.037 |
| deepseek-r1:14b-qwen-distill-q8_0 | 2 | 12 | 180.02 |

Qwen3 Coder and Gemma 4 12B both passed all 12 cases.
Qwen3 Coder had the lower recorded warm median latency
of these two models.

This supports the historical selection of qwen3-coder:30b
for the optional local Match Director in this specific
application context.

It does not establish general LLM superiority or equivalent
performance on other hardware.

Sources:

- [HTTP summary](model/results/vybe_http_all20_results/vybe_http_all20_summary.csv)
- [Combined HTTP results](model/results/vybe_http_all20_results/vybe_http_all20_combined.csv)
- [Original Qwen results](model/results/vybe_http_local_qwen_v1_results.csv)
- [Benchmark runner](model/scripts/vybe_http_all20_runner.py)
- [Original HTTP benchmark](model/scripts/vybe_http_local_qwen_v1.py)
- [Runner notes](model/results/vybe_http_all20_results/vybe_http_all20_run_notes.txt)

## Security and robustness evaluation

Three finalists were evaluated across 24 cases each,
giving 72 recorded executions.

| Model | Passed | Model cases | Prefilter | Wrong tool | Contract failures | Median model latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gemma4:12b-it-q4_K_M | 19/24 | 17/22 | 2/2 | 3 | 2 | 7.843 |
| qwen3-coder:30b | 20/24 | 18/22 | 2/2 | 3 | 1 | 1.548 |
| granite4.2:8b-q4_K_M | 20/24 | 18/22 | 2/2 | 4 | 0 | 3.992 |

Qwen3 Coder and Granite passed 20 of 24 cases.
Gemma passed 19 of 24 cases.

Qwen had the lowest recorded median model latency.
Granite recorded zero contract failures, but four
wrong-tool selections.

No finalist passed every case.

The two prefilter cases are application-level controls,
not evidence of model-level security capability.

Sources:

- [Security summary](security/results/vybe_http_security_finalists_v1_results/summary.csv)
- [Combined security results](security/results/vybe_http_security_finalists_v1_results/combined.csv)
- [Security benchmark script](security/scripts/vybe_http_security_finalists_v1.py)

## Other model experiments

Earlier routing, native tool-calling, scenario and
contract evaluations are retained in the model results
directory.

Their scoring methods and workloads differ. Results
must not be pooled into a single accuracy ranking
without a separately validated common methodology.

See [model results](model/results/) and
[model scripts](model/scripts/).

## Speech research

The speech archive contains 21 scripts and eight JSON
manifests covering historical voice discovery, voice
comparisons, pronunciation, wording, sports narration
and multilingual speech experiments.

The preserved candidate manifest includes Arabic and
multilingual neural voice candidates.

Historical production evidence records the owner's
acceptance of Evelyn Arabic speech and reported iPhone
Safari playback.

The original generated audio samples are not included
in the current archive. Independent listening evaluation
cannot be reconstructed from the manifests alone.

No numerical speech-quality score, listener-study result
or accessibility certification is claimed.

Sources:

- [Voice candidates](speech/manifests/vybe_voice_candidates.json)
- [Speech manifests](speech/manifests/)
- [Speech scripts](speech/scripts/)
- [Historical speech rollout](../docs/archive/AZURE_SPEECH_ROLLOUT.md)

## Historical cloud evidence

Two complementary records are preserved:

- [Detailed API observations](model/results/VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md):
  owner-supplied production response payloads.
- [Production evidence summary](../docs/archive/VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md):
  owner-observed resource-level token activity and
  reported speech/mobile behavior.

Neither establishes an independent request-level Azure
inference trace or managed Foundry Agent Service usage.

The former Azure application is retired. The public
GitHub Pages portfolio uses recorded deterministic
content, not live model inference.

## Limitations and reproducibility

These are historical, application-specific experiments
using synthetic football data.

The HTTP benchmark used a temporary local Ollama adapter.
It did not benchmark the public frontend or Azure.

Model versions, quantization, hardware, workload,
provider behavior and warm-up conditions affect results.

The original scripts and CSVs remain available for
inspection. The experiments were not rerun for this
documentation update.

Historical scripts may modify a supplied worktree,
contact configured external endpoints or incur cloud
usage costs. Read the [execution safety policy](README.md)
before considering reproduction.

These results are not production capacity measurements,
security certification or general-purpose AI benchmarks.
