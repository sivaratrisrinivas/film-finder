# Cerebras chat completions (trimmed)

Source: https://inference-docs.cerebras.ai/api-reference/chat-completions. Fetched 2026-11-21.

## Kimi model ID: `moonshotai-kimi-k3.1-pro-trial` (VERIFIED 2026-11-21 18:21 UTC)
- Returns HTTP 200 with total_time of about 0.12s for a short reply. `-test` shows up in `/v1/models` but returns `model_not_found`. Ignore it.
- Reasoning is ON by default: "Say OK." used 36 reasoning tokens. With `reasoning_effort: "low"` it used 14. Reasoning tokens count toward the 100K TPM limit.

## Endpoint
`POST https://api.cerebras.ai/v1/chat/completions`, header `Authorization: Bearer $CEREBRAS_API_KEY`. OpenAI-compatible.

## Params we use
| Param | Values |
|---|---|
| `model`, `messages` | required. Roles: system, user, assistant, tool |
| `reasoning_effort` | kimi-k3.1-pro: `low`, `medium`, `high`, `max` (docs default `max`; verified that reasoning is on when unset). Use `low` for cheap steps |
| `reasoning_format` | `parsed` (default for kimi-k3.1-pro) puts reasoning in `message.reasoning` |
| `tools` | `[{type:"function", function:{name, description, parameters, strict}}]` |
| `tool_choice` | `none`, `auto`, `required`, `{type:"function",function:{name}}` |
| `parallel_tool_calls` | bool, default true |
| `response_format` | `{type:"json_schema", json_schema:{name, schema, strict}}` or `{type:"json_object"}` (non-stream only) |
| `stream` | bool |
| `max_completion_tokens` | includes reasoning tokens |
| `temperature` | 0 to 2 |
| `prompt_cache_key` | routing hint for cache reuse. Use a constant |

## Response fields to log
- `usage.prompt_tokens`, `usage.completion_tokens` (includes reasoning), `usage.prompt_tokens_details.cached_tokens`, `usage.completion_tokens_details.reasoning_tokens`
- `time_info.queue_time`, `prompt_time`, `completion_time`, `total_time` (seconds). Use these for the speed demo.

## Limits
100 requests/min and 100K tokens/min. Cached tokens don't count.

## Sample
```bash
curl https://api.cerebras.ai/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer $CEREBRAS_API_KEY" \
  -d '{"model":"moonshotai-kimi-k3.1-pro-trial","reasoning_effort":"low","max_completion_tokens":256,
       "messages":[{"role":"user","content":"Hello!"}]}'
```
