# Hackathon rules brief: Cerebras x Kimi K3.1 Pro

Source: docs/handoff.md (no official rules page saved yet; paste it here if we get one). Written 2026-11-21.

## Hard requirements (miss any one and we're out)
- Core model is Kimi K3.1 Pro on Cerebras (base URL https://api.cerebras.ai/v1).
- Built on the OpenClaw harness.
- Core functionality is built during the hackathon. Scaffolding and data prep from before kickoff are allowed.
- Submission is an X post with a demo video of 60 seconds or less, tagging @Cerebras and @Kimi_Moonshot, with #KimiOnCerebras.
- Deadline: Sun Nov 22, 11:30 PM IST (18:00 UTC). Kickoff was Sat Nov 21, 11:30 PM IST.

## Prizes (organic reach only, no judges)
1. **X impressions** (most winnable). Reach comes from the hook in the first 3 seconds and from visible speed. Show Cerebras next to a GPU provider (HF credits, about $20).
2. **r/cerebras upvotes** (optional post, flair "Kimi K3.1 Pro Hackathon"). Reddit rewards a working bot people can try and honest numbers (hit@1, latency).

## What earns reach
- **Speed you can see**: a side-by-side race, with tokens/sec or seconds on screen.
- **Relatable "aha"**: "that movie where..." is a universal itch. Pick a hard case (obscure, non-English, misremembered) that Gemini gets wrong.
- **Try it yourself**: a public Telegram bot link in the post turns viewers into users and replies.

## Constraints
- 100 requests and 100K tokens per minute. Cached tokens don't count.
- At 18:15 UTC Sat the key could list `moonshotai-kimi-k3.1-pro-test`, but chat calls to both `-test` and `-trial` returned `model_not_found`. **Blocker. Ask organizers which ID to use and when access goes live.**

## Ask an organizer today
1. The exact Kimi model ID: handoff says `-trial`, `/v1/models` lists `-test`. Neither works yet.
2. Does using a GPU provider only for the side-by-side comparison break the "must use Kimi on Cerebras" rule? (It shouldn't, if the bot itself runs only on Cerebras.)
3. Is a Reddit post required, or only the X post?
