# Local verification record

Status: `VERIFIED_LOCAL — PYPI_0.1.0_VERIFIED — RELEASE_0.1.1_PENDING`

Local evidence was verified on 2026-08-27 and rerun for the `0.1.1` patch candidate on 2026-08-28. Both immutable PyPI `0.1.0` packages were published and independently verified; their lowercase ownership markers cannot authorize the GitHub organization's exact-case MCP namespace. No MCP Registry entry, GitHub release, social post, or standalone media upload exists. PyPI `0.1.1` publication remains pending the protected release gate.

## Source boundary

- Standalone public candidate derived from clean public-only commit `c970ceb` and hardened in this sprint.
- Protected `main` retains GitHub-verified signed history. The release resolver, hosted CI run, and signed annotated tag—not a self-referential hash in this file—establish the exact `0.1.1` release commit.
- No private repository history was imported.
- Public path, credential-marker, archive-path, and secret-pattern scans passed.
- The exact live repository-control state and authorization blockers are recorded in `docs/REPOSITORY-CONTROLS.md`.

## Deterministic gates

- Python tests: 33/33 passed.
- Agent Skill self-tests: 6/6 passed.
- Declared-outcome examples: 20/20 matched across all eight MCP tools.
- Both wheels and source distributions built twice byte-for-byte identically.
- Package-specific reproducible CycloneDX 1.6 runtime-lock SBOM validation passed.
- Hash-locked runtime and release dependencies installed successfully; `pip-audit` reported zero known runtime vulnerabilities.
- Clean local wheel installations discovered exactly four tools per server.
- Evidence Gate and Release Gate manifests passed live `mcp-publisher validate` checks.
- Release tag/version, package/registry alignment, ownership markers, CLI entry points, and archive-content checks passed.
- Shell syntax, Python compilation, and diff-whitespace checks passed.
- Prior GitHub-hosted CI passed all six Ubuntu/macOS Python 3.11–3.13 jobs plus dependency and workflow-security audits; exact `0.1.1` hosted CI remains a release gate below.

## Demo artifact

- File: `daily-ai-agent-toolkit-demo-v0.1.1.mp4`
- Runtime: 179.046 seconds.
- Video: H.264, 1920×1080, 30 fps.
- Audio: AAC narration generated locally with the macOS system voice.
- Captions: embedded English `mov_text` track plus retained SRT and transcript.
- Captions: 28 cues, each no longer than seven seconds and no more than two lines.
- SHA-256: `44590cb57f4fcb82241b6b4aa317baea44222833946a4ead799173211b9ac6a5`.

## Publication boundary

The existing public repository and prior hosted CI are verified; the exact `0.1.1` release commit remains subject to the gates below. The following remain `UNVERIFIED` until checked against exact public release surfaces:

- unauthenticated GitHub release availability;
- public PyPI installation of both corrected `0.1.1` packages;
- public MCP Registry discovery of both server identities;
- GitHub-hosted CI and signed provenance for the exact `0.1.1` release tag;
- the public site-repository link; and
- any resume or LinkedIn claim gated on publication.

The generated `dist/release/RELEASE-MANIFEST.json` and `SHA256SUMS` are local candidates. The tag workflow will rebuild them from the immutable public commit and attach signed provenance; those workflow-produced artifacts, not pre-commit local hashes, are authoritative for the public release.
