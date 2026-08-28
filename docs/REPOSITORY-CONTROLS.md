# Repository controls

Status captured on 2026-08-27 for `Dailyaiagents/daily-ai-agent-toolkit`.

## Confirmed live controls

- The repository exists publicly and is intentionally empty until the exact release candidate passes the independent audits.
- Secret scanning, push protection, validity checks, web commit signoff, and automatic head-branch deletion are enabled.
- An active `Protect release tags` ruleset blocks deletion and non-fast-forward updates for `refs/tags/v*`, with no bypass actors.
- Four deployment environments exist: one PyPI and one MCP Registry environment for each package.
- Every deployment environment disallows administrator bypass, requires a reviewer, prevents self-review, and accepts only `v*` tags.

## Fail-closed publication state

`BLOCKED-AUTH`: the organization currently has one member, `dailyaiagents-cpu`. That same account is the only eligible environment reviewer, so `prevent_self_review` deliberately prevents it from approving its own publication jobs. A distinct trusted organization member must be invited and configured as the required reviewer before a tag can publish.

The local release commit can be SSH-signed, but registration of its public signing key with GitHub is also `BLOCKED-AUTH` until Cooper signs in to GitHub in the handed-off Chrome tab. No private key material will be uploaded.

PyPI Trusted Publishing and MCP Registry namespace verification remain `UNVERIFIED` until their authenticated provider-side setup is completed. Token or improvised-namespace fallbacks are prohibited.

## Controls intentionally deferred

- The default-branch ruleset will be installed immediately after the first verified, signed `main` push, because the empty repository has no default branch ref to protect yet.
- Release/tag creation, PyPI publication, MCP Registry publication, and public-release verification remain blocked until the authorization gates above are cleared.

This document is a dated control receipt, not a claim that external publication has occurred.
