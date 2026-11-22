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

## Dev set: all 100 posts of `tomt_dev_100.csv` (Nov 22, 9:16–10:20 AM IST, Cerebras queue <1s)

Same pipeline as run 2. The first 24 rows were resumed from the earlier partial run (4 kept, busy ones re-run).

| | Matcher | Hand-checked |
|---|---|---|
| Busy | 3 | 3 |
| hit@1 | 37/97 (38%) | ~40/97 (41%) |
| Confident wrong | 18 (19%) | 14 (14%) + 1 disputed label |
| Ask / not sure | 15 / 27 | 15 / 27 |
| Median time / tokens per post | 18.3s / 3630 | |

Matcher misses counted as hits: The Wisher (Spliced, likely the US alias), Die Wolke (The Cloud), The Silence of the Sea. Disputed: Tarnation → 51 Birch Street.
Real wrong answers: Cypher → Criminal, Missing Link → Ao: The Last Hunter, Hope Springs → Love Actually, American Gangster → The Business, The Dukes of Hazzard → Beverly Hills Ninja, Transformers → Hackers, Blue Streak → First Sunday, Starship → Star Odyssey, Biloxi Blues → The Virgin Soldiers, Cheaters → Real Genius, Soul Survivors → Soultaker, The Commuter → 16 Blocks, Flipping Out → Flipped, Night Flight → Only Angels Have Wings.
The 30-post sample (7% wrong) was optimistic; on 100 posts it's 14%.

## Recent posts: `tomt_recent.csv`, 13 posts from Oct–Nov 2026 (Nov 22, ~10:20 AM IST, 0 busy)

| | Result |
|---|---|
| hit@1 | 1/13 (Dogman 2023) |
| Asked, with the right film as its top candidate | 2 (The Help, The Phantom of Liberty) |
| Confident wrong | 4/13 (31%): Mr. K → Spaceman, The World Is Not Enough → The Monster Squad, Paranormal Xperience 3D → The Devil's Ground, Primer → Time Chasers |
| Other asks / not sure | 3 / 3 |
| Median time / tokens | 25.7s / 6163 |

These threads were posted after the model's training data, so Kimi can't have seen them. Much weaker results here than on the old dev set suggest the dev numbers are inflated by memorized threads. Small sample (13).

## Speed race: `side_by_side.py`, Into the Wild verify prompt (Nov 22, ~10:22 AM IST, one run)

Same model (Kimi K3.1 Pro), same prompt, `reasoning_effort: medium`, streaming, started at the same moment.

| | First token | Tokens | tok/s | Total |
|---|---|---|---|---|
| Cerebras | 0.54s | 282 | 283 | 1.53s |
| Nebius (GPU, via HF) | 0.69s | 170 | 308 | 1.25s |
| Together (GPU, via HF) | 6.99s | 206 | 52 | 10.98s |

All three answered Into the Wild (2007). One run, short outputs; tok/s over ~1s of generation is noisy.
