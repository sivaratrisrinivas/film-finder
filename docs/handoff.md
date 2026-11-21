# Film-finder — handoff

## What it is
An agent that finds a film from a half-remembered description (r/tipofmytongue style). Asks one follow-up if needed, searches, verifies its guess against the user's clues, and says "not sure" instead of guessing wrong.

## Hackathon: Cerebras x Kimi K3.1 Pro (24h, deadline Sun Nov 22, 11:30 PM IST)
- MUST use Kimi K3.1 Pro on Cerebras as the core model: `moonshotai-kimi-k3.1-pro-trial` (standard Cerebras API, base URL https://api.cerebras.ai/v1). Thinking is ON by default (reasoning tokens count toward TPM) — set `reasoning_effort: "low"` for cheap steps.
- MUST use the OpenClaw harness.
- Limits: 100 requests and 100K tokens per minute. Cached tokens don't count, so keep the system prompt stable.
- Core functionality must be built during the hackathon; scaffolding and data prep are allowed.
- Submission: X post with a ≤60s demo video, tag @Cerebras @Kimi_Moonshot, #KimiOnCerebras. Optional r/cerebras post with flair "Kimi K3.1 Pro Hackathon". Prizes = organic reach (X impressions, Reddit upvotes). Demo should show Cerebras speed, ideally side-by-side with a GPU provider (use HF credits, ~$20).

## Environment (done)
- WSL2 Ubuntu 26.04, Node 26.13 (nvm), Python 3.14, venv at `.venv`.
- OpenClaw 2026.11.6 installed; Cerebras plugin installed; Cerebras key saved; gateway running as a systemd user service on 127.0.0.1:18789.
- Before kickoff, Kimi returned `model_not_found` and other models `payment_required` ($0 balance). Cerebras staff confirmed no credits needed; access turns on at kickoff.
- To do at kickoff: confirm Kimi responds via curl, set it as OpenClaw's default model (re-run `openclaw onboard`, choose Cerebras + saved sign-in), add a Telegram channel (`openclaw channels add`).

## Data and tools
- `.env` holds `TMDB_TOKEN` (TMDB v4 read token). `.env` is gitignored — never commit it.
- `get_30_film_posts.py` pulls solved film posts from HF dataset `webis/tip-of-my-tongue-known-item-search-triplets` (4,958 usable).
- `tomt_30_films.csv` = manual baseline set; `tomt_dev_100.csv` = dev set for the agent (keep evals ≤100 during the hackathon because of rate limits).
- `score_baseline.py` = manual Google/Gemini scoring helper.

## Baseline so far (5 of 30 judged)
- Google 2/4, Gemini 3/4, 1 disputed label (Tarnation vs 51 Birch Street — likely a dataset mislabel).
- Both did well on famous films with specific clues; both missed an obscure anime (Magnetic Rose, from Memories, 1995).
- The real competitor is Gemini, not Google. Pitch: hard cases — obscure, non-English, misremembered films.
- Caveat: test posts are old public Reddit threads, so models may have memorized answers. Later, test on recent posts too.

## Plan for the build
1. Clue extraction (Kimi): turn the messy post into structured clues (era, genre, language, key scenes, which details might be wrong).
2. Search tools: TMDB search, Wikipedia search. Cache every call.
3. Verify (Kimi, with reasoning on): check the top candidates against the clues; answer only if confident, else ask one follow-up or say "not sure".
4. OpenClaw bot on Telegram.
5. Small eval on `tomt_dev_100.csv`: hit@1, "not sure" rate, latency, tokens per solve.
6. Demo video and X post.

## Kickoff update (Nov 21, 11:49 PM IST)
- Kimi WORKS with model `moonshotai-kimi-k3.1-pro-trial` (~0.12s per short reply). `-test` is listed but returns model_not_found — ignore it.
- Kimi reasons by default (79 reasoning tokens on a 5-word reply). Reasoning tokens count toward the 100K TPM limit; set `reasoning_effort` low for cheap steps.
- Next: set this model as OpenClaw's default (re-run `openclaw onboard` → Cerebras → saved sign-in; the model may not be in the plugin's built-in list, so it might need adding by hand), then add a Telegram channel.

## Set Up phase: done (Nov 22, ~12:50 AM IST)
- OpenClaw default + utility model = Kimi (custom Cerebras model, see `docs/openclaw-telegram.md`).
- Telegram bot **@kimi_filmfinder_bot** is live, still `dmPolicy: pairing` (only the owner is paired). It goes public (`dmPolicy: "open"`, `allowFrom: ["*"]`) as soon as the first film tool works in Build.
- Public agent `filmfinder` (workspace `agent/`) is the only Telegram binding. Tools: `minimal` profile, deny runtime/fs/ui/nodes/automation/web/sessions/memory/media/message/gateway, elevated off. Film tools will be added via an MCP server and `alsoAllow: ["filmfinder__*"]`.
- `session.dmScope: per-channel-peer` (one session per Telegram user).
- Disabled OpenClaw's auto-created "Proactive check (main)" cron job.
- `agent/` holds OpenClaw's default persona files (incl. BOOTSTRAP.md "what should I call you" ritual). Not committed. Replace them with the film-finder persona in Build.

### Open items carried into Plan/Build
- **Retest:** bot must refuse "run the shell command ls" (the test was cut off by Cerebras 429s).
- **Cerebras capacity:** at kickoff, even tiny requests got 429 `queue_exceeded` ("high traffic"). That's platform-wide, not our limit. Record the demo at a quiet hour. OpenClaw already replies "rate-limiting, try again in a few minutes".
- **Latency:** first Telegram answer took ~2 min (429 retries); OpenClaw spent ~10s assembling context before calling Kimi. Default prompt is ~18K tokens (cached after first turn). Slim persona + minimal tools should cut it. Measure again.
- **Speed Bounty** (Santa's Speedy Shopper): decide in Plan.
