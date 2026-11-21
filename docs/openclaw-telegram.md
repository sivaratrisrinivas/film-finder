# OpenClaw Telegram channel (trimmed)

Sources: https://docs.openclaw.ai/channels/telegram/setup, https://docs.openclaw.ai/channels/telegram/access-control, https://docs.openclaw.ai/channels/telegram. Fetched 2026-11-21. Local: OpenClaw 2026.11.6, config at `~/.openclaw/openclaw.json`, gateway as a systemd user service on 127.0.0.1:18789.

## Kimi as OpenClaw's model (DONE 2026-11-21)
Kimi isn't in OpenClaw's catalog, so we added it as a custom Cerebras model with `openclaw config set --batch-file` (`models.mode: "merge"`, `models.providers.cerebras.models[]` with id `moonshotai-kimi-k3.1-pro-trial`, `api: "openai-completions"`, `reasoning: true`). Both `agents.defaults.model` and `agents.defaults.utilityModel` are set to `cerebras/moonshotai-kimi-k3.1-pro-trial`. The "not present in server catalog" warning is expected (Cerebras lists `-test`), and the model still works.
- Test: `openclaw agent --agent main --session-id test -m "hi" --json`
- Measured: the default agent's system prompt is about 18.1K input tokens per turn. It's cached after the first turn (17.4K cacheRead, 696 uncached). First turn took 30s (cold), the second 4.8s of agent time.
- `models refresh` only works with the gateway stopped (`systemctl --user stop openclaw-gateway`).

## Setup
1. In Telegram, message `@BotFather` (check the exact handle), send `/newbot`, and save the token.
2. `openclaw channels add --channel telegram --token <bot-token>` (env fallback `TELEGRAM_BOT_TOKEN`; config wins over env).
3. Verify with `openclaw channels status --probe`. If the gateway is offline, run `openclaw gateway start`.
4. Pairing flow (default): DM the bot, then `openclaw pairing list telegram` and `openclaw pairing approve telegram <CODE>`. Codes expire after 1 hour.

Long polling is the default, so it needs no public URL or webhook. Hot reload applies channel config changes automatically.

## Letting strangers use it (our "deploy")
```json5
{ channels: { telegram: { enabled: true, dmPolicy: "open", allowFrom: ["*"] } } }
```
- `dmPolicy` values: `pairing` (default), `allowlist` (numeric IDs in `allowFrom`), `open` (requires `"*"`), `disabled`.
- The docs warn: "Use it only for intentionally public bots with tightly restricted tools." **So the public agent must only have our film-search tools. No shell, no file access.**
- `allowFrom` takes numeric Telegram user IDs, not @usernames.

## Groups (we don't need these)
Groups default to `allowlist`. Privacy Mode is on by default (change it with `/setprivacy` in BotFather, then re-add the bot).

## Gotchas
- `tokenFile` must be a regular file, not a symlink.
- With multiple accounts, set `defaultAccount` and bind the agent: `{ agentId: "main", match: { channel: "telegram", accountId: "default" } }` in `bindings`.
- The bot identity is cached for 24h. Changing the token clears the cache.
