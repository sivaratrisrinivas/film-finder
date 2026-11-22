# Eval results

Pipeline: `find_film.py` (Kimi K3.1 Pro on Cerebras: clues → TMDB + Wikipedia search → verify). Traces in `runs/`.
"Hand-checked" counts English/original titles and aliases the automatic matcher misses (e.g. "Die Wolke" for "The Cloud").

## Dev set: first 30 posts of `tomt_dev_100.csv` (Nov 22, 6:15–6:45 AM IST)

| | Run 1 (old verify prompt) | Run 2 (stricter verify + year-aware poster lookup) |
|---|---|---|
| Busy (Cerebras 429 / timeout) | 4 | 1 |
| hit@1, matcher | 9/26 (35%) | 11/29 (38%) |
| hit@1, hand-checked | ~12/26 (46%) | ~14/29 (48%) |
| Confident wrong, hand-checked | 5 (19%) | 2 (7%) + 1 disputed label |
| Ask / not sure | 1 / 8 | 6 / 6 |
| Median time per post | 19.4s | 18.5s |
| Median tokens per post | 3306 | 3183 |

Run 2 = full 30 with the new prompt, then the 9 busy posts and 3 regressions rerun after raising `max_completion_tokens` to 8000 (one busy was `finish_reason=length`: reasoning used the whole 4000 cap).

Remaining wrong answers: The Ant Bully → Johnny the Giant Killer (1950); Magnetic Rose → Biohazard 4D-Executer (2000) (run 1 got Memories, so this one is unstable). Disputed: Tarnation → 51 Birch Street (likely a dataset mislabel).

Caveat: these are old public Reddit threads, so Kimi may have memorized some answers.

## Recent posts: `tomt_recent.csv`, 13 posts from Oct–Nov 2026 (Nov 22, ~6:50 AM IST)

Incomplete: 9 of 13 came back busy (Cerebras congestion). Of the 4 that ran: 1 hit (Dogman 2023), 3 not sure, 0 wrong. Rerun pending.
