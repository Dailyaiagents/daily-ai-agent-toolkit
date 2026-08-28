# Release Gate

<!-- mcp-name: io.github.Dailyaiagents/release-gate -->

A local MCP server that compares retained evidence with explicit completion requirements and produces release receipts. It does not run arbitrary shell commands or publish anything.

```bash
dailyai-release-gate --root /path/to/workspace
```

## Tools

- `check_contract`: compare required artifact paths with a JSON contract.
- `evaluate_completion`: preserve the declared state of every requirement.
- `format_blockers`: turn non-passing findings into explicit blockers.
- `build_release_receipt`: hash artifacts and summarize retained checks.

## Clean install

```bash
python3.11 -m venv .venv
.venv/bin/pip install dailyaiagents-release-gate==0.1.1
.venv/bin/dailyai-release-gate --root "$PWD"
```

The server does not execute arbitrary commands, approve a release, or publish an artifact. See the repository's [threat model](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/main/docs/THREAT-MODEL.md) and [receipt schemas](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/main/docs/RECEIPT-SCHEMAS.md).
