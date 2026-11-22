# Film Finder

**Describe a film you half-remember. Get the title, or an honest "not sure".**
A Telegram bot for r/tipofmytongue-style questions, running on Kimi K3.1 Pro on Cerebras inside the OpenClaw harness.

Try it: [@kimi_filmfinder_bot](https://t.me/kimi_filmfinder_bot) on Telegram.

<!-- DEMO VIDEO: add after recording -->

## What it does
You type something like *"guy stuck reliving things"*. The bot asks one question (*"a TV weatherman, a soldier fighting aliens, or a guest at a wedding?"*). You answer *"guest at a wedding"*, and it replies with **Palm Springs (2020)**: the poster, the clues that matched, and how long Kimi took.

It answers only when its guess survives a check against your clues. Otherwise it asks one follow-up question or says it's not sure. A wrong answer is worse than no answer.

## How it works
```
your message ─► OpenClaw agent (Kimi) ─► find_film tool
                                           1. Clues   Kimi, low reasoning, JSON schema: era, genre, language, key scenes,
                                                       which details may be misremembered, title guesses, search queries
                                           2. Search  TMDB (titles, years, plot, keywords, posters) +
                                                       Wikipedia full-text search on plot details (finds films with no title guess)
                                           3. Verify  Kimi, medium reasoning: check up to 10 real candidates against the clues
                                                       → answer | ask one question | not sure
```
- Kimi may only pick from the candidates TMDB and Wikipedia returned, so it can't invent a film.
- Each request makes two Kimi calls plus an OpenClaw turn, so model speed adds up. That's where Cerebras matters.
- Every TMDB and Wikipedia call is cached on disk.

## Results
Eval on solved r/tipofmytongue posts (`eval_results.md`, traces in `runs/`):

| | 100 old dev posts | 13 recent posts (Oct–Nov 2026) |
|---|---|---|
| Correct first answer (hand-checked) | ~40/97 (41%) | 1/13 |
| Confidently wrong | 14/97 (14%) | 4/13 (31%) |
| Asked a question or said "not sure" | 42/97 | 8/13 (2 asks had the right film as top candidate) |
| Right when it answered (precision) | ~40/54 (74%) | 1/5 (20%) |

The recent posts were written after the model's training data. The gap between the two columns suggests the old-post numbers are helped by memorized threads.

Speed, same model (Kimi K3.1 Pro) and same prompt, median of 5 runs (`side_by_side.py`):

| | First token | tokens/sec | Total |
|---|---|---|---|
| Cerebras | 1.04s | **293** | 2.39s |
| Nebius (GPU, via HF) | 0.75s | 192 | 1.55s |
| Together (GPU, via HF) | 0.97s | 44 | 4.84s |

Cerebras has the highest throughput. On this short task Kimi wrote more reasoning tokens on Cerebras, so Nebius finished first.

## Run it yourself
Requires Python 3.14 and `pip install mcp`.
1. Create `.env` with `CEREBRAS_API_KEY=...` and `TMDB_TOKEN=...` (TMDB v4 read token). For the speed race, also add `HF_TOKEN=...` (Hugging Face, "Inference Providers" permission).
2. Run one query: `python find_film.py "young man walks into the Alaskan wilderness alone, based on a true story"`
3. Eval: `python eval.py tomt_dev_100.csv 30` (resumes; only missing or busy posts re-run).
4. Speed race: `python side_by_side.py`.
5. Telegram bot: register `mcp_server.py` as an OpenClaw MCP server and use the persona in `agent/`. See `docs/openclaw-mcp.md` and `docs/openclaw-telegram.md`.

## Limits
- The eval posts are old public threads, so Kimi may have memorized some answers. That's why recent posts are scored separately.
- Some Indian networks reset most connections to `api.themoviedb.org`, so `tools.py` uses `api.tmdb.org`.
- Movies only: no TV, books or games.

Built in 24 hours for the Cerebras × Kimi K3.1 Pro hackathon. #KimiOnCerebras
