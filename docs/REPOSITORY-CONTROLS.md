# Repository controls

Status updated on 2026-08-28 for `Dailyaiagents/daily-ai-agent-toolkit`.

## Confirmed live controls

- Signed annotated tag `v0.1.0` resolves through tag object `98538457c925d225745b5b14a082ea1023f85b5a` to release source commit `8602a594697da4fff76c2505f93e6b9e374b501e`.
- GitHub reports both the tag and target commit signatures as verified and valid.
- Hosted CI passed all six Ubuntu/macOS Python 3.11–3.13 jobs plus dependency and workflow-security audits at the exact release target.
- Secret scanning, push protection, validity checks, web commit signoff, and automatic head-branch deletion are enabled.
- An active `Protect release tags` ruleset blocks deletion and non-fast-forward updates for `refs/tags/v*`, with no bypass actors.
- An active no-bypass `Protect main` ruleset requires signed commits, a pull request review, strict success from all eight hosted checks, resolved review threads, and last-push approval; it blocks deletion and non-fast-forward updates.
- Four deployment environments exist: one PyPI and one MCP Registry environment for each package.
- Every deployment environment disallows administrator bypass, requires independent reviewer `cooperdavidreed-personal`, and prevents self-review.
- Deployment policies accept `v*` tags and the protected `main` branch. The latter exists only for a reviewed, fail-closed resume of an already immutable release tag.

## Fail-closed publication state

Independent GitHub review is configured. Personal account `cooperdavidreed-personal` has repository-only write access, approved the receipt update, and is the sole required deployment reviewer. The owner/service account cannot approve its own deployment.

The local public signing key is registered with GitHub. No private key material was uploaded.

PyPI Trusted Publishers are configured for both fixed projects, workflow file, and environments. No long-lived PyPI token is used. MCP namespace publication remains gated by GitHub OIDC and the two protected registry environments; no improvised namespace fallback is permitted.

## Remaining external gates

- The original tag-triggered run failed safely before publication because checkout dereferenced the annotated tag locally. No PyPI file, MCP record, GitHub release, or release asset was created by that run.
- The first protected-main resume run also failed before publication because GitHub's attestation API rejected a repository-specific SLSA build-type URI. The corrected predicate retains the tag dependency but uses GitHub's supported workflow build type.
- A following resolver run failed before build when accumulated workflow-run JSON exceeded the operating system's environment size limit. The resolver now transfers API payloads through bounded runner-temporary files instead of environment variables.
- The next run completed the reproducible build but GitHub rejected the custom predicate because its immutable-tag dependency preceded the canonical Actions source dependency. Both predicate builders now put the exact workflow ref and digest first while retaining the independently verified tag ref and digest as a required second dependency.
- The following run published and independently verified both PyPI `0.1.0` packages, then the MCP Registry rejected the lowercase manifest namespace because GitHub OIDC authorized the organization's exact-case `io.github.Dailyaiagents/*` namespace. The `0.1.1` patch manifests and all generated proof surfaces now use that registry-authorized casing; no MCP record or GitHub release existed at the rejection boundary.
- Publication resumes only after that narrow correction is independently reviewed, merged through protected `main`, and its four deployment approvals are granted.

This document is a dated control receipt, not a claim that external publication has occurred.
