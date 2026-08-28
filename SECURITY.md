# Security policy

## Supported versions

Only the latest released minor version is supported.

## Data boundary

Both MCP servers run locally over stdio. They do not make network requests. File-reading tools reject paths outside the root supplied at startup.

Treat every byte beneath the supplied root as disclosed to the MCP client: repeated queries can act as a content-membership oracle. Use a dedicated sanitized root. Do not point the tools at secrets, credential stores, regulated records, or customer data unless your own environment and handling policy explicitly permits that disclosure.

Path traversal is file-descriptor-relative and rejects symlink components. Individual file reads are limited to 10 MiB, and input collections are bounded. These controls constrain local reads; they are not a multi-tenant sandbox.

## Reporting

Report a vulnerability privately to `support@usedailyai.com`. Do not include live credentials or sensitive records in the report.
