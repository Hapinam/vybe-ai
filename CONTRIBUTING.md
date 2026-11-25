# Contributing to VYBE

VYBE is a human-centered, synthetic-football AI hackathon project.

## Maintenance status

Active hackathon development is closed. Keep the public portfolio reproducible and review dependency, security and documentation changes through pull requests. Dependabot routine version updates are monthly for npm, pip, Docker and GitHub Actions. Security alerts and security updates are enabled. Automatic GHCR publication is retired and the historical package has been deleted. GitHub Pages remains active. Do not reactivate Azure or registry publication without separate owner approval.

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


## Maintenance requirements

Use signed commits and reviewed pull requests. Preserve the required
Quality Gate and CodeQL checks.

Use the documented dependency lockfiles and do not bypass hash
verification. Review dependency licensing and preserve applicable
third-party notices.

See [CI/CD policy](docs/CI_CD_COST_POLICY.md),
[security policy](SECURITY.md) and
[third-party licensing](docs/THIRD_PARTY_LICENSES.md).
