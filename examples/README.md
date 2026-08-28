# Deterministic examples

`cases.json` contains 20 offline examples covering all eight Evidence Gate and Release Gate tools. Each case declares its own temporary fixtures, tool input, and expected stable outcome.

Run the complete catalog from the repository root:

```console
python scripts/run-examples.py
```

Use `--json` for a machine-readable summary. The runner ignores volatile receipt fields such as `generated_at` and validates only declared statuses, counts, and finding codes. Fixtures are created in a temporary directory and removed after each case. No case accesses the network, external accounts, or paths outside its temporary root.

These examples demonstrate deterministic local behavior. A passing example does not establish factual truth, validate an external URL, approve a release, publish an artifact, or prove a production result.
