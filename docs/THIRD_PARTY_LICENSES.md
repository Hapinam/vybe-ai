# Third-party licensing review

**Review date:** 26 November 2026.

**Reviewed baseline:**
57c2b826ddacb93d660bc73aa33a71a5815705be

VYBE's original [MIT License](../LICENSE) remains unchanged.
Third-party components retain their respective licenses.

## npm dependency inventory

The frontend package-lock.json contains 61 dependency records,
including platform-specific optional packages.

| Declared license | Records |
| --- | ---: |
| MIT | 40 |
| MPL-2.0 | 12 |
| Apache-2.0 | 5 |
| ISC | 2 |
| BSD-3-Clause | 1 |
| 0BSD | 1 |
| Total | 61 |

No missing license fields were identified.

The MPL-2.0 records comprise lightningcss and its
platform-specific packages.

## Python dependency inventory

The owner executed hash-enforced installation of the test
lockfile in a digest-pinned Python 3.11 Linux container.

All 25 package versions matched the lockfile. All distributions
contained at least one license-related file.

The combined inventory contains 14 runtime packages and
11 test-only packages.

| Package | Version | Scope | Declared license |
| --- | --- | --- | --- |
| annotated-doc | 0.0.7 | Runtime | MIT |
| annotated-types | 0.8.0 | Runtime | MIT |
| anyio | 4.16.0 | Runtime | MIT |
| certifi | 2026.11.20 | Test | MPL-2.0 |
| click | 8.5.1 | Runtime | BSD-3-Clause |
| fastapi | 0.165.0 | Runtime | MIT |
| h11 | 0.16.0 | Runtime | MIT |
| httpcore | 1.0.9 | Test | BSD-3-Clause |
| httpcore2 | 2.16.2 | Test | BSD-3-Clause |
| httpx | 0.28.1 | Test | BSD-3-Clause |
| httpx2 | 2.16.2 | Test | BSD-3-Clause |
| idna | 3.20 | Runtime | BSD-3-Clause |
| iniconfig | 2.3.1 | Test | MIT |
| opentelemetry-api | 1.45.2 | Runtime | Apache-2.0 |
| packaging | 26.4 | Test | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.7.0 | Test | MIT |
| pydantic | 2.14.4 | Runtime | MIT |
| pydantic-core | 2.50.5 | Runtime | MIT |
| pygments | 2.21.0 | Test | BSD-2-Clause |
| pytest | 9.2.0 | Test | MIT |
| starlette | 1.10.0 | Runtime | BSD-3-Clause |
| truststore | 0.10.5 | Test | MIT |
| typing-extensions | 4.16.0 | Runtime | PSF-2.0 |
| typing-inspection | 0.4.5 | Runtime | MIT |
| uvicorn | 0.54.0 | Runtime | BSD-3-Clause |

## Combined inventory

| Declared license | Records |
| --- | ---: |
| MIT | 52 |
| MPL-2.0 | 13 |
| BSD-3-Clause | 9 |
| Apache-2.0 | 6 |
| ISC | 2 |
| BSD-2-Clause | 1 |
| Apache-2.0 OR BSD-2-Clause | 1 |
| PSF-2.0 | 1 |
| 0BSD | 1 |
| Total | 86 |

No GPL or AGPL declarations were identified in this inventory.

## Distribution obligations

Preserve applicable copyright notices, license texts and
attribution when redistributing third-party software.

Apache-2.0 components may require preservation of applicable
NOTICE content and other notices under their license terms.

MPL-2.0 applies file-level source availability obligations when
covered software is distributed in executable form. It does not
automatically require unrelated VYBE source files to adopt MPL.

The identified MPL components are lightningcss and its
platform packages, and certifi in the Python test lockfile.

The dependency metadata inventory does not establish which
components or notices are present in the actual deployed
frontend bundle. Review emitted assets and upstream license
texts before final distribution acceptance.

This document is an inventory and maintenance record, not a
substitute for applicable third-party license texts.

## Scope and limitations

This review covers declared npm lockfile licenses and
owner-provided Python distribution metadata.

It does not establish complete legal compliance or review all
upstream copyright notices and license text contents.

Docker operating-system packages, base-image components,
build tooling outside the application lockfiles, browser
binaries, optional Ollama model licenses and historical cloud
services are outside this inventory.

Historical research and synthetic-data attribution remain
preserved. No official football-data affiliation is implied.

No application dependency or project license change is
proposed solely on the basis of this metadata inventory.

## Final frontend distribution verification

Production and static JavaScript source-map inspection
identified four third-party packages:

- react 19.3.1 (MIT)
- react-dom 19.3.1 (MIT)
- scheduler 0.28.0 (MIT)
- lucide-react 1.77.0 (ISC, including Feather MIT attribution)

Installed package versions matched the npm lockfile.
Complete upstream license texts are preserved in
[THIRD_PARTY_NOTICES.txt](../apps/web/public/THIRD_PARTY_NOTICES.txt).

The notice file was verified byte-for-byte in both frontend
build modes and in the final production Docker image.

Temporary audit source maps are not published.

This completes the scoped frontend distribution notice
verification. It is not a comprehensive legal certification.
The previously documented scope exclusions remain applicable.

Future dependency changes require review and, where necessary,
regeneration of the distributed notice file.
