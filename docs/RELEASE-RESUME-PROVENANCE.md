# Immutable-tag release resume provenance profile

This document defines the custom SLSA provenance used when the release workflow
must resume an existing immutable tag. The workflow is reviewed and executed
from protected `main`, while package bytes are rebuilt only from the separately
validated signed tag target.

The predicate uses GitHub's supported
`https://actions.github.io/buildtypes/workflow/v1` build type and its standard
workflow external parameters. The release tag is added as a second resolved Git
dependency rather than represented as a different or unsupported build type.

## External parameters

- `workflow.ref`: the Git ref from which the recovery workflow runs.
- `workflow.repository`: the canonical GitHub repository URL.
- `workflow.path`: `.github/workflows/release-evidence.yml`.

The standard GitHub internal parameters retain the event name, repository ID,
repository-owner ID, and `github-hosted` runner environment.

## Resolved dependencies

The predicate contains two required Git dependencies:

1. `release-source`: `refs/tags/<releaseTag>` with the exact Git commit digest
   resolved from the GitHub-verified annotated tag object.
2. `release-workflow`: the protected ref and exact commit digest from which
   `.github/workflows/release-evidence.yml` was loaded.

## Procedure

The resolver rejects lightweight or invalidly signed tags, tags that are not
ancestors of `main`, and tag targets without the exact successful CI job set.
The build checks out the resolved target SHA, fetches the tag without tag
following, rechecks the tag object and commit, and verifies its SSH signature
against the pinned release key. Artifacts are named by the release target SHA.

GitHub signs the custom `https://slsa.dev/provenance/v1` predicate. The workflow
then verifies the Sigstore bundle against the repository, signer workflow,
signer digest, source ref, source digest, and GitHub-hosted runner requirement.
It also checks the signed predicate's two resolved dependencies before any
provenance bundle is retained or attached to a release.

This predicate distinguishes source code from workflow configuration. A resume
run on `main` does not claim that the updated workflow existed in the older tag.
