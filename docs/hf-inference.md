# Hugging Face Inference Providers (for side_by_side.py only)

Sources (read 2026-11-22): https://huggingface.co/docs/inference-providers/index, https://huggingface.co/docs/inference-providers/tasks/chat-completion, https://huggingface.co/docs/inference-providers/pricing, and a live `GET https://router.huggingface.co/v1/models` (no auth needed).

The bot itself stays Kimi on Cerebras. HF is used only for the GPU side of the speed comparison.

## Call
- `POST https://router.huggingface.co/v1/chat/completions`, OpenAI-compatible.
- Headers: `Authorization: Bearer $HF_TOKEN`, `Content-Type: application/json`.
- Token: fine-grained, permission "Make calls to Inference Providers". Lives in `.env` as `HF_TOKEN`.
- Pick the provider with a model suffix: `moonshotai/Kimi-K3.1-Pro:nebius`, `moonshotai/Kimi-K3.1-Pro:together`. Never use `:fastest`/`:cheapest`/no suffix: those may route elsewhere (Cerebras is an HF provider for other models).
- Streaming: `"stream": true` gives SSE. `stream_options: {include_usage: true}` adds a final chunk with `usage` and empty `choices`.
- Response has `usage` (`prompt_tokens`, `completion_tokens`, `total_tokens`). No timing field: measure wall-clock ourselves.
- Not verified: whether `reasoning_effort` and `response_format` json_schema pass through to these providers. The models list says `supports_structured_output: true` for both.

## Kimi K3.1 Pro on HF (router stats, 2026-11-22 ~7:15 AM IST; HF's numbers, not ours)
| provider | throughput tok/s | first token ms | quantization | $/M in / out |
|---|---|---|---|---|
| nebius | 120 | 1040 | fp4 | 2 / 10 |
| together | 45 | 803 | (not listed) | 2 / 10 |

18 providers serve it in total; Cerebras is not one of them.

## Billing
- Free accounts get no monthly credits; PRO gets $2/month. Extra credits are pay-as-you-go at provider rates, no HF fee.
- One verify call (~3K in, ~1–2K out) is about $0.02.
