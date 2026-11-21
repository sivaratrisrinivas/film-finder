# PRD: Film Finder

## What is this?
A Telegram bot that finds a film from a half-remembered description, the way r/tipofmytongue does. It runs on Kimi K3.1 Pro on Cerebras inside the OpenClaw harness. It answers only when its guess survives a check against your clues. Otherwise it asks one follow-up question or says "not sure".

## Who is it for?
Anyone who remembers a scene, a mood or an actor's face but not the title. The hard cases are the point: obscure, non-English, or misremembered films, where Google and Gemini miss.

## Demo path (the 60s video)
1. User DMs @kimi_filmfinder_bot: a messy description of an obscure film (e.g. Magnetic Rose).
2. Bot replies in seconds: title, year, poster link, the clues that matched, and one timing line with Kimi time and total end-to-end time ("Kimi 0.4s · total 3.1s").
3. Second example: a vague description. The bot asks one follow-up, the user answers, the bot finds it.
4. Cut to the side-by-side clip: the same verify prompt on Cerebras and on a GPU provider.

## Pipeline
1. **Clues** (Kimi, `reasoning_effort: low`, JSON schema): era, genre, language/country, key scenes, actors, which details might be wrong. Also writes 3 to 5 search queries.
2. **Search** (no LLM): TMDB `search/movie` and Wikipedia full-text search for each query. Merge and dedupe into about 10 candidates. Fetch a plot extract or overview for each. Every HTTP call is cached on disk.
3. **Verify** (Kimi, `reasoning_effort: medium`, JSON schema): score the candidates against the clues. Output `{verdict: answer|ask|not_sure, title, year, tmdb_id, matched_clues, mismatched_clues, follow_up_question}`.
4. **Reply**: the OpenClaw agent turns that JSON into a short Telegram message and appends the timing line.

**Cerebras 429s:** `find_film` retries briefly with backoff (a few seconds at most). If it's still rate-limited, it returns `{verdict: "busy"}` and the bot says "Kimi is busy right now, try again in a minute."

## Architecture (approved)
One MCP tool, `find_film(description)`, that runs the whole pipeline in Python and returns the verdict JSON plus timings. The OpenClaw agent (also Kimi) only handles conversation: it calls the tool, relays the answer, and on a follow-up calls the tool again with the original description plus the user's answer (the session keeps both).
- Why: the same Python code drives the eval, so eval numbers describe the real bot. We get `time_info` for the timing line. And it costs one OpenClaw turn instead of several, each carrying its ~18K-token context.
- Alternative: expose small tools (`tmdb_search`, `wiki_search`, `get_details`) and let OpenClaw's Kimi run the loop. It's more "agentic", but slower, harder to eval, and gives no clean timing.

## MCP tools (exposed to OpenClaw as `filmfinder__*`)
- `find_film(description: str) -> {verdict (answer|ask|not_sure|busy), title, year, tmdb_id, poster_url, matched_clues, mismatched_clues, follow_up_question, timing: {kimi_seconds, tool_seconds, tokens}}`
- Total end-to-end time (Telegram message in → reply out, including OpenClaw overhead) is measured in the 4:00 step. How it gets into the reply is decided there, once we know what OpenClaw exposes.

## Persona (`agent/` files, replaces the OpenClaw defaults)
Short and byte-stable. "You find films from vague descriptions. Always call `find_film`. Never guess without it. Answer only from the tool's verdict. Refuse anything that isn't about finding a film." No bootstrap ritual.

## Out of scope
TV shows, books, games, songs; group chats; images or voice input; user accounts or history; a web UI; the Speed Bounty (skipped); fine-tuning.

## Success criteria
- [ ] Bot answers a known dev-set post correctly on Telegram, with a timing line showing Kimi time and total time.
- [ ] Bot asks one follow-up on a vague post and then solves it.
- [ ] Bot says "not sure" instead of guessing wrong on a nonsense or non-film post.
- [ ] Bot refuses "run the shell command ls".
- [ ] On Cerebras 429, the bot replies "busy, try again" within a few seconds instead of hanging.
- [ ] Strangers can DM it (`dmPolicy: open`).
- [ ] Eval on ≤100 dev posts: hit@1, "not sure" rate, median latency, tokens per solve.
- [ ] Eval includes 5 to 10 recent solved posts (after the model's training data), reported separately to check for memorization.
- [ ] Side-by-side clip: same prompt, Cerebras vs GPU (raw API script; the bot stays Kimi-only).

## Build clock (IST, Sun Nov 22)
| Window | Build step | Done when |
|---|---|---|
| 1:45 to 2:45 | `tools.py`: TMDB search + details, Wikipedia search + extract, disk cache | Prints candidates for "Memories 1995"; second run hits the cache |
| 2:45 to 4:00 | `find_film.py`: clues, search, verify | Gets correct verdicts on 5 dev posts from the CLI; a forced 429 returns `busy` |
| 4:00 to 5:00 | MCP server, OpenClaw wiring, persona | Telegram answer works, `ls` is refused, Kimi + total time are measured and shown. Then go public |
| 5:00 to 6:30 | `eval.py` on 30, then up to 100 dev posts, plus 5 to 10 recent posts; tune prompts | Numbers written to `eval_results.md`, recent posts reported separately |
| 6:30 to 7:30 | `side_by_side.py` (Cerebras vs HF GPU) | Clip recorded |
| 7:30 to 9:00 | Buffer; record demo if Cerebras is quiet | |
| 9:00 | **Panic check:** no film-tool answers on Telegram means we cut to the smallest working version | |

## Open questions / unverified
- Recent posts: where do they come from (recently solved r/tipofmytongue threads, collected by hand?), and how recent counts as "after training data"?
- The Python `mcp` package (approved, not installed yet).
- No OpenClaw MCP docs are in `docs/` yet. Fetch them before wiring (step 3).
- TMDB details and Wikipedia extract endpoints are still unverified (see `docs/tmdb.md`, `docs/wikipedia.md`).
- HF GPU provider and model for the side-by-side are not chosen yet.
