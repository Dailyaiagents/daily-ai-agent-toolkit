# Evidence Gate

<!-- mcp-name: io.github.dailyaiagents/evidence-gate -->

A local MCP server that checks retained artifacts, declared claim support, and literal citation containment. It does not determine truth on its own and does not fetch URLs.

```bash
dailyai-evidence-gate --root /path/to/workspace
```

See the repository documentation for client configuration and limitations.

## Tools

- `verify_artifact`: file presence, size, hash, and declared text rules.
- `audit_claims`: declared evidence availability without semantic overclaiming.
- `audit_citations`: normalized literal containment in local sources.
- `summarize_verification`: aggregate receipts without upgrading uncertainty.

## Clean install

```bash
python3.11 -m venv .venv
.venv/bin/pip install dailyaiagents-evidence-gate==0.1.0
.venv/bin/dailyai-evidence-gate --root "$PWD"
```

See the repository's [threat model](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/main/docs/THREAT-MODEL.md), [receipt schemas](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/main/docs/RECEIPT-SCHEMAS.md), and [changelog](https://github.com/Dailyaiagents/daily-ai-agent-toolkit/blob/main/CHANGELOG.md). URL evidence remains `UNVERIFIED`; literal containment is not semantic entailment.
