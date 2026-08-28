# Receipt schemas

Every tool returns JSON containing `schema_version`, `tool`, `status`, `limitations`, and `generated_at`. Evidence Gate receipts also contain `checked` and `findings`. Release Gate receipts contain tool-specific fields such as `requirements`, `blockers`, `checks`, and `artifacts`.

Allowed top-level states are `PASS`, `FAIL`, `UNVERIFIED`, `NOT_RUN`, and `BLOCKED`.

```json
{
  "schema_version": "dailyai.evidence-gate-receipt/v1",
  "tool": "verify_artifact",
  "status": "PASS",
  "checked": 1,
  "findings": [],
  "limitations": ["This check does not establish factual truth."],
  "generated_at": "2026-08-20T12:00:00+00:00"
}
```

Receipts supplied as evidence are schema-checked before they can contribute to a `PASS`; a caller-provided status string alone is insufficient. Empty evidence remains `UNVERIFIED` or `FAIL` according to the tool contract.

Input schemas are exposed by MCP tool discovery. The Python type annotations are the canonical source for the generated MCP schemas.
