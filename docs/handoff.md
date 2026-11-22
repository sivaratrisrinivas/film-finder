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

## Plan phase: DONE (Nov 22, ~1:20 AM IST)
`PRD.md` approved. Decisions: Speed Bounty **skipped**; GPU side-by-side = same prompt, raw API script; reply ends with a timing line (Kimi time + total end-to-end). Additions: 429/timeout → `busy`; eval includes recent posts for memorization.

## Build status (Nov 22, ~3:40 AM IST; see update below)
Files (all committed and pushed):
- `tools.py`: TMDB search/details + Wikipedia search/extract, disk cache `.cache/`, stdlib `urllib` (Wikimedia 403s `httpx2`), 5 retries (the home network resets ~half of TMDB TLS handshakes; the hotspot works). VERIFIED.
- `find_film.py`: clues (Kimi low, json_schema) → search (TMDB + Wiki, Wiki-only fallback) → verify (Kimi medium). 429 → 2 retries → `busy`; 20s timeout → `busy`. CLI: `python find_film.py --dev 5` or `python find_film.py "<text>"`. Search + busy path VERIFIED; **Kimi steps never ran** (Cerebras outage), so json_schema `strict` on Cerebras is unverified.
- `mcp_server.py`: `mcp` 2.3.0 `MCPServer`, tool `find_film`. Stdio test VERIFIED (lists tool, call returns busy).
- `eval.py`: hit@1 matcher (selftest: `python eval.py --selftest`), per-group summary, traces to `runs/<csv>.jsonl` (commit them). Not run on real data yet.
- `tomt_recent.csv`: 13 recent solved posts (Oct–Nov 2026), group `recent`, answers stripped from the post text. Hand-check misses on Paranormal Xperience 3D (TMDB may say "XP3D") and Mr. K (no year).
- `agent/`: film-finder persona (AGENTS/SOUL/IDENTITY/USER), BOOTSTRAP.md deleted. Originals were only in a session scratchpad (gone).
- OpenClaw: `mcp.servers.filmfinder` registered (connect timeout 20s); `agents.entries.filmfinder.tools.alsoAllow: ["filmfinder__*"]`. Details and gotchas in `docs/openclaw-mcp.md`.
- `CEREBRAS_API_KEY` is in `.env` (the scripts read it from there).

**Blocker:** since ~20:00 UTC Nov 21, Cerebras chat completions queue 18–55s (confirmed platform-wide by staff on Discord: "awaiting the service leveling out"). `/v1/models` works.

## Build status update (Nov 22, ~5:55 AM IST)
- Cerebras queue recovered to ~0.2s at 23:42 UTC, but 429s still come in bursts.
- `find_film.py --dev 5`: 4/5 answered (Gone in 60 Seconds, Intersection, Into the Wild exact; "The Wisher (2002)" for Spliced, likely the US alias, not verified). Cypher = busy (probably a 20s timeout while Cerebras queued). json_schema `strict` WORKS on Cerebras. 429 retries raised to 1/2/4/8s (`find_film.py:84`).
- **Telegram bug fixed:** OpenClaw's automatic Tool Search had deferred `filmfinder__find_film`, so Kimi answered from memory. Fix: `tools.toolSearch.exclude: [{source: "mcp", name: "filmfinder__*"}]` in `~/.openclaw/openclaw.json` (see `docs/openclaw-mcp.md`). After the fix plus `/new` in Telegram, the bot called the tool: poster, "Matched:", timing line.
- Telegram end-to-end time was ~4 min: 15s OpenClaw context, 1.3s tool pick, ~17s tool, then ~3.5 min of Cerebras 429 retries on the final reply. The pipeline itself is ~35s.
- Timing line relabelled to `⚡ Kimi Xs · search+verify Ys` (`agent/AGENTS.md:12`) because the tool can't see OpenClaw's own time. Not yet seen live (unverified whether a gateway restart is needed).
- Vague query ("guy stuck reliving things") was tested only before the fix (it guessed). Retest after `/new`.
- Config backups: `openclaw.json.before-toolsearch` / `.before-public` were in the session scratchpad (may be gone).

Next steps, in order:
- [x] `python find_film.py --dev 5` (see update above).
- [x] Telegram end-to-end: tool called, timing line, `ls` refused.
- [x] Retest on Telegram after `/new` (6:00 AM IST): "guy stuck reliving things" got one follow-up (weatherman / soldier / wedding guest); "guest at a wedding" got Palm Springs (2020) with poster. New timing label shows with no gateway restart (`⚡ Kimi 5.15s · search+verify 34.56s`). The ask reply also carried a timing line (AGENTS.md says to send only the question; harmless). Round trip ~1 min, no 429 stalls.
- [ ] Go public: `dmPolicy: "open"`, `allowFrom: ["*"]` under `channels.telegram`. **Decision: wait until close to demo recording** so strangers don't eat quota during evals. The auto-mode classifier blocked the assistant from applying it; the user runs it: `! openclaw config patch '{channels:{telegram:{dmPolicy:"open",allowFrom:["*"]}}}' && systemctl --user restart openclaw-gateway` (patch syntax unverified).
- [ ] `python eval.py tomt_dev_100.csv 30`, then 100; `python eval.py tomt_recent.csv`. Write `eval_results.md`.
- [ ] `side_by_side.py` (Cerebras vs HF GPU, same prompt). Provider/model not chosen.
- [ ] 9:00 AM IST panic check: no film-tool answers on Telegram means cut to the smallest working version.

## How to resume in a new session
1. Read `CLAUDE.md` (auto-loaded), this file, `docs/schedule.md`, `docs/hackathon.md`.
2. Working style: go **phase by phase** on the cheat sheet (https://thehackathonplaybook.dev/cheat-sheet). At each phase, name the cheat-sheet prompt being applied, do it in small steps, and **wait for the user's OK** before each config change and before moving to the next phase. No rush.
3. Re-create the 30-minute commit timer (session-only cron): commit if `git status` shows changes, then `git push origin main` (never force), never `.env` or `.cache/`. `agent/` (persona) is committed now.
4. Re-create the Cerebras watcher (background loop, every 3 min, tiny "Say ok" call, report `time_info.queue_time`; alert when < 2s). Background jobs die with the session.
5. Continue from **"Build status"** below: the next action is the first unchecked item.
