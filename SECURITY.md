# Security policy

## Project status

VYBE is a synthetic-football hackathon prototype and public
technical portfolio. It is not a certified production service.

The historical Azure deployment and GHCR publication have been
retired. No new paid infrastructure is authorized.

## Supported versions

| Version | Maintenance |
| --- | --- |
| Current main branch | Best-effort reviewed maintenance |
| Historical hackathon release | Preserved; no dedicated security support |

There is no guaranteed response or remediation SLA.

## Reporting vulnerabilities

Please avoid public disclosure of exploitable vulnerability
details, credentials, personal data or sensitive logs.

GitHub Private Vulnerability Reporting is enabled.

To report a vulnerability privately, open the repository's
[Security tab](https://github.com/Hapinam/vybe-ai/security)
and select **Report a vulnerability**.

Include the affected version or commit, a description of the
issue, its potential impact and safe reproduction steps.

Do not include credentials, personal data or unrelated sensitive
information. Do not submit exploitable vulnerability details
through public issues.

## Security maintenance

Security and dependency changes are reviewed through signed
pull requests and required CI checks.

The project uses bounded read-only AI tools, deterministic
fallback, request limits, outbound HTTP protections, dependency
locking and automated security checks.

These measures reduce specific risks but do not guarantee
absence of vulnerabilities or suitability for production use.

## Additional documentation

- [Security audit](docs/SECURITY_AUDIT_REPORT.md)
- [Testing and security](docs/TESTING_AND_SECURITY.md)
- [CI/CD policy](docs/CI_CD_COST_POLICY.md)
- [Third-party licensing](docs/THIRD_PARTY_LICENSES.md)
