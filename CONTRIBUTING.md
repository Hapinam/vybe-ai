# Contributing to VYBE

VYBE is a human-centered, synthetic-football AI hackathon project.

## Maintenance status

Active hackathon development is closed. Keep the public portfolio reproducible and review dependency, security and documentation changes through pull requests. Dependabot remains configured for weekly npm, pip and GitHub Actions updates. Eligible non-documentation merges may publish a GHCR image; web changes may rebuild Pages. Do not reactivate Azure without separate owner approval.

## Workflow
1. Branch from `main` using `feat/`, `fix/`, or `docs/`.
2. Keep changes focused and open a pull request.
3. Add tests for changes to match facts or narrative validation.
4. Never commit secrets, personal information, real broadcast footage, or proprietary match data.
5. Review accessibility, explainability, and factual grounding before merging.

## Commit style
Use concise conventional commits such as `feat(api): add synthetic event schema`.

## Product guardrails
Always distinguish synthetic from real events. Do not allow AI-generated commentary to change deterministic scores or invent evidence.
