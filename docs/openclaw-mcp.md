# OpenClaw MCP servers (trimmed)

Sources (fetched 2026-11-22): https://docs.openclaw.ai/cli/mcp/transports, https://docs.openclaw.ai/cli/mcp/registry, https://docs.openclaw.ai/gateway/config-extensions, https://docs.openclaw.ai/gateway/config-tools/tool-policy, https://docs.openclaw.ai/gateway/configuration/hot-reload. Not read yet: https://docs.openclaw.ai/gateway/config-tools (per-agent tools), https://docs.openclaw.ai/gateway/configuration/environment-variables.

## Register a stdio server
Config key `mcp.servers.<name>` in `~/.openclaw/openclaw.json`. Stdio is chosen by having `command` (remote servers use `url`).
| Field | Meaning |
|---|---|
| `command` | executable to spawn (required) |
| `args` | array of arguments |
| `env` | extra environment variables (merge vs replace: not documented) |
| `cwd` / `workingDirectory` | working directory |
| `requestTimeoutMs` | per-server request timeout, default 60s (tool listing at session start uses 10s if unset) |
| `enabled`, `toolFilter: {include, exclude}` | optional |

CLI (works while the gateway runs; the change is sent to the gateway):
`openclaw mcp add <name> --command <exe> --arg <a> --cwd <dir> --env K=V --timeout <sec>`, plus `list`, `show`, `status`, `doctor [--probe]`, `probe`, `set <name> <json>`, `tools`, `unset`.

**Reload:** `mcp` config changes hot-reload with no gateway restart. The next turn picks up changed servers.

**Gotchas seen on 2026.11.6 (2026-11-22), contradicting the docs:**
- `openclaw mcp add` and `mcp probe` refuse to run while the gateway is up ("requires exclusive offline state ownership"). Run `systemctl --user stop openclaw-gateway`, then the command, then `start`. `mcp show` and `mcp status` work online. `config set` works online and hot-reloads.
- `mcp add` gives the server 5s to start by default. Our Python server needs about 3.2s warm, so a cold start timed out. Registered with `--connect-timeout 20` (`connectionTimeoutMs: 20000`).

**Our registration (DONE 2026-11-22):** `mcp.servers.filmfinder = {command: <repo>/.venv/bin/python, args: ["mcp_server.py"], cwd: <repo>, connectionTimeoutMs: 20000}`; `agents.entries.filmfinder.tools.alsoAllow: ["filmfinder__*"]`.

## Env and secrets
- OpenClaw rejects interpreter-startup and loader env keys (`PYTHONSTARTUP`, `NODE_OPTIONS`, `LD_*`, ...).
- `openclaw mcp doctor` warns about literal secrets in `env`. `${VAR}` references are allowed.
- **Our choice:** pass no secrets through OpenClaw. `find_film.py`/`tools.py` read `CEREBRAS_API_KEY` and `TMDB_TOKEN` from the repo's `.env`.

## Tool names and policy
- Tools are exposed as `<server>__<tool>` (doc examples: `docs__search`, `outlook__*`). Server names outside `[A-Za-z0-9_-]` are rewritten.
- The `minimal` profile hides MCP tools (`bundle-mcp`), so our agent needs an explicit allow such as `alsoAllow: ["filmfinder__*"]`.
- `allow` and `alsoAllow` cannot both be set in the same scope. The docs name the per-agent scope `agents.entries.*.tools`. **Check our actual config key before editing** (the handoff did not record it).
- Repeated tool-call failures pause the server briefly.

## Python side: `mcp` 2.3.0 (VERIFIED import 2026-11-22)
In 2.x, FastMCP was renamed: `from mcp.server.mcpserver import MCPServer`; `s = MCPServer("filmfinder")`; `@s.tool()`; `s.run("stdio")`.
