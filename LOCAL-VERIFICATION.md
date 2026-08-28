# Local verification record

Status: `VERIFIED_LOCAL_AND_HOSTED_CI — RELEASE BLOCKED-AUTH`

Local evidence was verified on 2026-08-27. The exact signed source commit was published and its hosted CI was verified on 2026-08-28. No GitHub release, package, registry entry, deployment, social post, or standalone media upload has occurred.

## Source boundary

- Standalone public candidate derived from clean public-only commit `c970ceb` and hardened in this sprint.
- Public `main` is the one-commit, GitHub-verified SSH-signed commit `73b4ae46e5a1e1482c5613d978fc0581bd93dc64`.
- No private repository history was imported.
- Public path, credential-marker, archive-path, and secret-pattern scans passed.
- The exact live repository-control state and authorization blockers are recorded in `docs/REPOSITORY-CONTROLS.md`.

## Deterministic gates

- Python tests: 19/19 passed.
- Agent Skill self-tests: 6/6 passed.
- Declared-outcome examples: 20/20 matched across all eight MCP tools.
- Both wheels and source distributions built twice byte-for-byte identically.
- Package-specific reproducible CycloneDX 1.6 runtime-lock SBOM validation passed.
- Hash-locked runtime and release dependencies installed successfully; `pip-audit` reported zero known runtime vulnerabilities.
- Clean local wheel installations discovered exactly four tools per server.
- Evidence Gate and Release Gate manifests passed live `mcp-publisher validate` checks.
- Release tag/version, package/registry alignment, ownership markers, CLI entry points, and archive-content checks passed.
- Shell syntax, Python compilation, and diff-whitespace checks passed.
- GitHub-hosted CI passed all six Ubuntu/macOS Python 3.11–3.13 jobs plus dependency and workflow-security audits at the exact public commit.

## Demo artifact

- File: `daily-ai-agent-toolkit-demo-v0.1.0.mp4`
- Runtime: 179.046 seconds.
- Video: H.264, 1920×1080, 30 fps.
- Audio: AAC narration generated locally with the macOS system voice.
- Captions: embedded English `mov_text` track plus retained SRT and transcript.
- Captions: 28 cues, each no longer than seven seconds and no more than two lines.
- SHA-256: `485964ad6528a2b0e828d72a0e8f43e9cf493df0685fb879ae92e70ba5b5fec3`.

## Publication boundary

The public repository source, exact commit signature, and hosted CI are verified. The following remain `UNVERIFIED` until checked against exact public release surfaces:

- unauthenticated GitHub release availability;
- public PyPI installation of both `0.1.0` packages;
- public MCP Registry discovery of both server identities;
- GitHub-hosted CI and signed provenance;
- the public site-repository link; and
- any resume or LinkedIn claim gated on publication.

The generated `dist/release/RELEASE-MANIFEST.json` and `SHA256SUMS` are local candidates. The tag workflow will rebuild them from the immutable public commit and attach signed provenance; those workflow-produced artifacts, not pre-commit local hashes, are authoritative for the public release.
