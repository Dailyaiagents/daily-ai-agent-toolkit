# Release policy and runbook

The release is fail-closed. A local build or a manually dispatched workflow
produces candidates only; only a protected `v<version>` tag can reach public
registries. Published versions are immutable.

## Deterministic candidate build

Use Python 3.11 and the same pinned tooling as the release workflow:

```bash
python -m pip install --require-hashes -r requirements/runtime.lock
python -m pip install --require-hashes -r requirements/release.lock
python -m pip install --no-deps -e servers/evidence-gate -e servers/release-gate
bash scripts/test-all.sh
pip-audit --strict --require-hashes --no-deps -r requirements/runtime.lock
python scripts/verify-release.py --tag v0.1.0
bash scripts/release-build.sh dist/release
bash scripts/release-sbom.sh dist/release
mcp-publisher validate servers/evidence-gate/server.json
mcp-publisher validate servers/release-gate/server.json
```

`release-build.sh` sets `SOURCE_DATE_EPOCH` from the source commit, builds every
wheel and source distribution twice in isolated temporary directories, and
requires byte-for-byte equality. `verify-release.py` checks aligned versions,
PyPI/MCP ownership markers, safe archive paths, private-path/secret signatures,
and artifact names. `release-sbom.sh` creates a reproducible, package-specific
CycloneDX 1.6 SBOM from the complete runtime lock and links each package root to
the full dependency graph. `SHA256SUMS` and `RELEASE-MANIFEST.json` cover
packages, SBOMs, demo media, documentation, and Registry manifests.

## One-time external configuration

Configure protected GitHub environments with required reviewer approval and
deployment branches restricted to release tags:

- `pypi-evidence-gate`: PyPI Trusted Publisher for project
  `dailyaiagents-evidence-gate`, owner `Dailyaiagents`, repository
  `daily-ai-agent-toolkit`, workflow `release-evidence.yml`.
- `pypi-release-gate`: the same configuration for project
  `dailyaiagents-release-gate`.
- `mcp-registry-evidence-gate`: protects GitHub OIDC publication of only
  `io.github.dailyaiagents/evidence-gate`.
- `mcp-registry-release-gate`: protects GitHub OIDC publication of only
  `io.github.dailyaiagents/release-gate`. No long-lived registry token is stored.

The GitHub organization must own the namespace, and PyPI projects must exist or
have pending Trusted Publishers configured before the first tag. Organization
owners should approve the environment deployments. Do not use API tokens as a
fallback when OIDC configuration is incomplete.

## Publication sequence

1. Confirm the worktree is clean and CI passes on Python 3.11-3.13 on Ubuntu
   and macOS.
2. Confirm both `pyproject.toml` and both `server.json` files contain the tag's
   exact version.
3. Create and push the annotated protected tag `v<version>` only after explicit
   release approval.
4. Approve the two PyPI environments. The workflow publishes each package from
   its own artifact directory using PyPI Trusted Publishing and attestations.
5. After both packages succeed, approve the two independent MCP Registry environments. The workflow
   waits for both wheels, source distributions, and ownership markers to become
   public, then clean-installs both packages and discovers exactly four tools
   from each server before authenticating with GitHub OIDC. Each job publishes
   only its fixed validated metadata file and can be recovered independently.
6. The workflow creates the GitHub release only after package and MCP Registry
   publication succeed, attaching distributions, SBOMs, checksums, and the
   release manifest. GitHub build-provenance attestations cover all wheels and
   source distributions.
7. Verify clean public installs and Registry search results. Retain the URLs and
   workflow run as the public release receipt.

If authentication, ownership, or a registry is unavailable, stop with
`BLOCKED-AUTH` or `BLOCKED-EXTERNAL`. Never rename a project opportunistically,
skip a failed package, reuse a version, or rewrite release history. Mark a
superseded or unsafe release explicitly and issue a new version.
