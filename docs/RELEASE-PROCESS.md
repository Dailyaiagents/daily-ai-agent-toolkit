# Release process and recovery

Version `0.1.0` is published only from an annotated, verified tag whose commit is reachable from protected `main` and whose required CI matrix passed at that exact SHA. GitHub immutable releases, tag protection, and four reviewer-gated environments are repository controls, not assumptions in source code; their API receipts must be retained before tagging.

The build job has no OIDC authority. It installs only hash-locked dependencies, runs tests and the runtime vulnerability audit, builds each distribution twice, validates archives and MCP manifests, generates package-specific SBOMs, and uploads immutable workflow artifacts. Separate jobs hold the minimum authority for each external surface:

| Surface | Environment | Recovery |
| --- | --- | --- |
| Evidence Gate on PyPI | `pypi-evidence-gate` | Do not retry if public `0.1.0` bytes differ from the manifest. If the exact files already exist, verify them and resume downstream jobs. |
| Release Gate on PyPI | `pypi-release-gate` | Same rule; the second package is independent and never uses `skip-existing`. |
| Evidence Gate in MCP Registry | `mcp-registry-evidence-gate` | Rerun this job only after exact PyPI digest, size, attestation, and four-tool discovery checks pass. |
| Release Gate in MCP Registry | `mcp-registry-release-gate` | Rerun this job independently; never republish the other server as a side effect. |
| GitHub release | repository contents token | Runs only after both registry records and both provenance jobs pass. A release is created once; conflicting existing assets are a blocker. |

If one immutable PyPI package publishes and the other fails, preserve the successful package, diagnose authentication or environment configuration, and rerun only the failed package job. Do not change version `0.1.0`, identity, namespace, or bytes. If the failed package cannot be published with exact manifest bytes, stop at `BLOCKED-AUTH`; do not create the MCP records or GitHub release.

Post-release verification downloads the public release bundle, checks every manifest digest, and verifies GitHub build provenance for both wheels and both source distributions. Public PyPI verification separately downloads with cache disabled, compares exact digest and size, verifies PEP 740 attestations, installs the hash-locked runtime plus each wheel with `--no-deps`, and discovers exactly four tools per server.

PyPI and GitHub do not permit replacing immutable version bytes. Any source correction after publication requires a new version and a new tag; it is never repaired by overwriting `0.1.0`.
