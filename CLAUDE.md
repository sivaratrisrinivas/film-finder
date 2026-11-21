# CLAUDE.md

The rules my AI assistant follows in every session on this project. This is the single source of truth; AGENTS.md just points here. Keep it short: if a line would not change how you work, delete it.

## Docs

Read the matching file in docs/ before writing code against that API. Never use an endpoint, parameter, or model name that does not appear in these files.

- `docs/handoff.md`: what we're building and the build plan. Read at the start of every session.
- `docs/hackathon.md`: the rules brief (hard requirements, prizes, deadline). Read before any scope decision.
- `docs/schedule.md`: the phase schedule with IST times. Check it before starting new work.
- `docs/cerebras.md`: Cerebras chat completions API and Kimi K3.1 Pro params (`reasoning_effort`, tools, `time_info`). Read before any LLM call.
- `docs/openclaw-telegram.md`: OpenClaw Telegram channel setup and DM access policy. Read before touching the bot.
- `docs/tmdb.md`: TMDB search/details/keywords endpoints. Read before writing the TMDB tool.
- `docs/wikipedia.md`: MediaWiki search and extract API. Read before writing the Wikipedia tool.

The four working principles adapt Andrej Karpathy's observations on the mistakes AI coding assistants make (posted on X, 2026: x.com/karpathy/status/2015883857489522876), popularized as a CLAUDE.md by Forrest Chang (github.com/forrestchang/andrej-karpathy-skills).

## 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State your assumptions explicitly before implementing. If uncertain, ask.
- If my request has multiple interpretations, present them instead of silently picking one.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop, name exactly what is confusing, and ask.

## 2. Simplicity first

Write the minimum code that solves the stated problem. Nothing speculative.

- No features beyond what was asked. No abstractions for single-use code.
- No "flexibility" or "configurability" I did not request.
- No error handling for scenarios that cannot happen.
- If you wrote 200 lines and 50 would do, rewrite it. Test: would a senior engineer call this overcomplicated?

## 3. Surgical changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting. Don't refactor things that aren't broken.
- Match the existing style, even where you would do it differently.
- Remove imports, variables, and functions that YOUR change orphaned; leave pre-existing dead code alone and mention it instead.
- The test: every changed line traces directly to my request.

## 4. Goal-driven execution

Define success criteria before starting. Loop until verified.

- Turn tasks into verifiable goals: "fix the bug" becomes "write a test that reproduces it, then make it pass".
- For multi-step work, state a short plan with a verification check per step, then execute it.
- "Make it work" is not a success criterion. If we have not agreed on what done looks like, ask before building.

## Honesty rules (read every turn)

- Never invent a function, class, type, import, or fact. Verify symbols exist (read the file or grep) before using them.
- If you cannot verify something, say "I have not verified this" and do not build on the unverified claim.
- Never claim a test or build passed unless you ran it this session and saw it pass. Never invent error messages or API responses.
- Do not add a dependency that is not already in the project without asking first.
- "I don't know, let me check" beats a confident guess. Always.

## Hackathon rules (apply to every reply)

- Optimize for a working demo at the deadline (Sun Nov 22, 11:30 PM IST), not for clean code. Submission work starts by 8:30 PM IST.
- The core model is Kimi K3.1 Pro on Cerebras, running inside the OpenClaw harness. Never swap either out.
- Never add a library, language, or service outside our stack unless I ask.
- When I report a bug, ask for the exact error text before guessing.
- Keep answers under 200 words unless I ask for code.
- If something will take longer than the time we have left, say so and offer the smaller version instead.
- Rate limit: 100 requests and 100K tokens per minute. Keep the system prompt byte-stable so cached tokens don't count. Cache every TMDB/Wikipedia call.
- Commit every 30 minutes (a time-boxed exception to "don't commit unless asked").

## About this project

- What we are building: a film finder for half-remembered descriptions (r/tipofmytongue style). It pulls clues out of the user's text, searches TMDB and Wikipedia, checks the top candidates against the clues, and answers only when confident. Otherwise it asks one follow-up question or says "not sure". Users reach it through an OpenClaw bot on Telegram.
- Stack: Python 3.14 (venv at `.venv`; activate with `source .venv/bin/activate`), Node 26 via nvm for the OpenClaw CLI (2026.11.6). The OpenClaw gateway runs as a systemd user service on 127.0.0.1:18789 (`systemctl --user status openclaw-gateway`). LLM: Cerebras OpenAI-compatible API, key in env `CEREBRAS_API_KEY`. No build or test commands exist yet.
- Data: `get_30_film_posts.py` pulls solved film posts from the HF dataset `webis/tip-of-my-tongue-known-item-search-triplets`. `tomt_30_films.csv` is the manual baseline set and `tomt_dev_100.csv` is the agent dev set (keep evals at 100 or fewer because of rate limits). `score_baseline.py` is the manual Google/Gemini scoring helper.
- Conventions worth knowing: `TMDB_TOKEN` lives in `.env`, which is gitignored, and its value needs quotes and whitespace stripped. Flat scripts in the repo root, no package structure. The eval posts are old public threads, so the model may have memorized answers; also test on recent posts.

## Guardrails

- Never commit secrets, .env files, or credentials. Keys live in environment variables.
- Ask before anything hard to undo: deleting files, migrations, deploys, force pushes.
- Never push or deploy unless I ask (routine 30-minute commits are allowed, see above).
