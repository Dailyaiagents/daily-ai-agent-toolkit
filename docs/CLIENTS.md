# Client configuration

Both servers use MCP stdio transport. Clients must launch the installed command and pass an absolute workspace root.

```json
{
  "mcpServers": {
    "dailyai-evidence-gate": {
      "command": "dailyai-evidence-gate",
      "args": ["--root", "/absolute/path/to/workspace"]
    }
  }
}
```

The same shape applies to `dailyai-release-gate`. Client-specific configuration locations change over time; consult the client’s current documentation.
