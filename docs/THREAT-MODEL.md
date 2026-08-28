# Threat model

The toolkit reads files beneath a root explicitly supplied by the operator. It does not fetch URLs, execute artifact contents, run arbitrary checks, publish results, or contact a Daily AI Agents service.

## Protected boundaries

- File-descriptor-relative traversal with `O_NOFOLLOW` rejects files outside `--root`, including symlink swaps and symlinked directory components.
- Inputs are data, never shell fragments.
- Missing evidence remains `FAIL`, `UNVERIFIED`, `NOT_RUN`, or `BLOCKED`; it is never promoted to `PASS`.
- Receipts include scope and limitations so a local result is not represented as hosted or production proof.
- File reads are limited to 10 MiB and bounded input collections; oversized or malformed inputs fail closed.

## Confidentiality boundary

Treat every byte beneath the supplied root as disclosed to the MCP client. A caller can test paths, required terms, and digests repeatedly and use the responses as a content-membership oracle. Root containment prevents escape; it does not make content inside the root confidential from the caller. Use a dedicated, sanitized root containing only artifacts the client is permitted to inspect.

## Out of scope

These tools do not establish semantic truth, legal compliance, security certification, production reliability, or future behavior. They do not provide multi-tenant isolation or defend against an already-compromised host. Run them with the least filesystem access required and inspect consequential results independently.
