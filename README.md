# Daily AI Agent Toolkit

Local, deterministic tools for checking AI-generated work before it is released.

The toolkit contains two Model Context Protocol (MCP) servers and six portable Agent Skills. They inspect retained artifacts, declared claim support, literal citations, completion contracts, blockers, and release receipts without calling a model, uploading files, or requiring a Daily AI Agents account.

> **Release status:** `0.1.0` release candidate. Public PyPI and MCP Registry publication is pending the final release gate.

## Why this exists

AI systems can produce convincing output without proving that required artifacts exist, cited text is present, or a completion contract was actually satisfied. These tools make those narrow checks repeatable and preserve uncertainty instead of silently upgrading it to success.

They deliberately do **not** determine broad truth, judge semantic entailment, approve a release, validate a live service, or establish legal or security compliance.

## Included tools

| Component | Interface | Purpose |
| --- | --- | --- |
| Evidence Gate | MCP server, four tools | Inspect artifacts, declared claim evidence, literal citation containment, and aggregate verification states. |
| Release Gate | MCP server, four tools | Check completion contracts, preserve requirement states, format blockers, and build retained release receipts. |
| Six Agent Skills | Portable skill directories | Reuse artifact, claim, contract, failure-state, and verification procedures with deterministic self-tests. |

### Evidence Gate

- `verify_artifact`
- `audit_claims`
- `audit_citations`
- `summarize_verification`

### Release Gate

- `check_contract`
- `evaluate_completion`
- `format_blockers`
- `build_release_receipt`

### Agent Skills

- `artifact-verifier`
- `claim-truth-gate`
- `completion-contract`
- `contract-checker`
- `fail-loud`
- `verification-bench`

## Install and run

Python 3.11 or newer is required.

```bash
python -m pip install dailyaiagents-evidence-gate==0.1.0
python -m pip install dailyaiagents-release-gate==0.1.0

dailyai-evidence-gate --root /absolute/path/to/workspace
dailyai-release-gate --root /absolute/path/to/workspace
```

Until the packages are public, install from a clean checkout:

```bash
python -m pip install ./servers/evidence-gate ./servers/release-gate
```

Both servers use MCP stdio transport. A representative client configuration is:

```json
{
  "mcpServers": {
    "dailyai-evidence-gate": {
      "command": "dailyai-evidence-gate",
      "args": ["--root", "/absolute/path/to/workspace"]
    },
    "dailyai-release-gate": {
      "command": "dailyai-release-gate",
      "args": ["--root", "/absolute/path/to/workspace"]
    }
  }
}
```

See [client configuration](docs/CLIENTS.md) for the supported transport boundary.

## Reproduce the proof

Run the complete local gate:

```bash
bash scripts/test-all.sh
```

The release candidate includes:

- unit tests for both servers;
- deterministic self-tests for all six skills;
- 20 declared-outcome examples spanning all eight MCP tools;
- rooted-path and symlink-escape protections;
- clean-wheel installation and stdio tool-discovery checks;
- package-specific checksums, SBOMs, and build provenance.

See the [examples](examples/), [technical report](docs/TECHNICAL-REPORT.md), [receipt schemas](docs/RECEIPT-SCHEMAS.md), [release and recovery process](docs/RELEASE-PROCESS.md), and [local verification record](LOCAL-VERIFICATION.md). A passing local check proves only the condition and scope named in its receipt.

## Architecture and security boundary

Live repository controls and current fail-closed publication gates are recorded in [Repository controls](docs/REPOSITORY-CONTROLS.md).

```text
MCP client
   |  stdio + structured inputs
   v
Evidence Gate / Release Gate
   |  canonical path resolution beneath --root
   v
Local retained files  --->  structured status + scoped receipt
```

The servers do not use network access, telemetry, model inference, arbitrary shell execution, or hosted Daily AI Agents infrastructure. Inputs are treated as data rather than shell fragments. URL-only evidence remains `UNVERIFIED`, and literal citation containment is not semantic support.

Read [SECURITY.md](SECURITY.md) and the [threat model](docs/THREAT-MODEL.md) before using the toolkit on sensitive work.

## Project leadership

The toolkit was conceived and led by **Cooper Reed**, founder of **Daily AI Agents LLC**, with implementation, testing, release engineering, and documentation developed as a public engineering project. Public claims about the toolkit should link to reproducible checks or retained release evidence in this repository.

## Contributing and support

- [Contributing guide](CONTRIBUTING.md)
- [Support policy](SUPPORT.md)
- [Release process](RELEASE.md)
- [Changelog](CHANGELOG.md)

Apache-2.0 licensed.
