# Demo video plan (DRAFT, 60s max)

Goal: X Audience Choice (impressions). Hook in the first 3s, Cerebras speed visible, honest numbers.
Hard rules (hackathon.md): ≤60s; no notifications, browser tabs, API keys, emails or credentials on screen.

## Shot list
| Time | Shot | On screen | Voice-over / caption |
|---|---|---|---|
| 0–3s | Hook | Telegram: user types a vague memory, "I think John Goodman or someone who looks like him works for the CIA, in a pretty memorable scene he screams really loudly at someone in his office about his experience and then breaks a window." → Charlie Wilson's War (bot: "Philip Seymour Hoffman… explaining the John Goodman look-alike memory") | "You remember the scene. Not the title." |
| 3–15s | Answer | Bot replies: 🎬 title, poster, matched clues, `⚡ Kimi Xs · search+verify Ys` | "Kimi K3.1 Pro on Cerebras pulls the clues, searches TMDB and Wikipedia, and checks its guess." |
| 15–28s | Follow-up | Vague message ("guy stuck reliving things") → one question → "guest at a wedding" → Palm Springs | "Not sure? It asks one question instead of guessing." |
| 28–48s | Speed race | `python side_by_side.py`: same model, same prompt, Cerebras vs Nebius vs Together, live tok/s | "Same model, same prompt. Cerebras: ~290 tokens/sec. GPU hosts: ~190 and ~45." (5-run medians: 293 / 192 / 44 tok/s; say tok/s, not "answers first") |
| 48–56s | Honesty card | "100 solved r/tipofmytongue posts: 41% right first try, 14% wrong, the rest it asked or said not sure" | "When it isn't sure, it asks instead of guessing." |
| 56–60s | CTA | Bot handle + repo URL | "Try it: @kimi_filmfinder_bot" |

## Must be true before recording
- [ ] Cerebras queue < 2s (check with the timer's queue probe).
- [ ] Telegram round trip is fast enough to show uncut. Today it's ~1 min: OpenClaw context ~15s, search+verify 14–35s (Kimi only ~5s of that, so most is TMDB/Wikipedia; the home network resets TLS handshakes; the hotspot was faster). If any wait is cut, caption it "trimmed".
- [x] Hook chosen: Charlie Wilson's War (2/2 correct via `find_film.py`, Kimi 3.4s, search+verify 9.2s). Not yet tested on Telegram.
- [ ] Bot public (`dmPolicy: open`) so the CTA works.
- [ ] Do Not Disturb on, single clean browser window, no `.env` or terminal history with keys.

## Open questions
- Voice-over or captions only?
- Screen recorder and editor (not chosen).

## Post copy (DRAFT; fill [brackets] from recorded numbers only)
Team: Srinivas. X [@SrinivasSi78619](https://x.com/SrinivasSi78619), Reddit u/srinivassachin.

### X (official submission; attach the ≤60s video)
One post (X Premium, so no 280 limit). The first line is the hook: it's all people see before "Show more".
```
You know when a movie scene is stuck in your head but the title won't come? I typed one of those into my bot: a CIA guy who looks like John Goodman screams at someone in his office and then breaks a window.

It came back with Charlie Wilson's War. Then it pointed out that my description had the wrong actor. The guy screaming was Philip Seymour Hoffman, not John Goodman, and it still found the film.

That's Film Finder, a Telegram bot I built for the Kimi K3.1 Pro hackathon. It pulls the clues out of whatever you half-remember, searches TMDB and Wikipedia, and checks its guess against those clues before answering. Kimi runs on @Cerebras at 293 tokens a second, while the same model on two GPU hosts ran at 192 and 44 (median of 5 runs each).

That checking step matters because a confident wrong answer is worse than no answer. So when it isn't sure, it asks you one question or just says so. On 100 solved r/tipofmytongue posts it got 41 right on the first answer and 14 wrong, and the rest went to a follow-up or a "not sure".

Try it (live while Kimi access lasts, may say "busy" at peak): https://t.me/kimi_filmfinder_bot
Code: https://github.com/sivaratrisrinivas/film-finder
Team: @SrinivasSi78619

@Kimi_Moonshot #KimiOnCerebras
```

### Reddit r/cerebras (flair "Kimi K3.1 Pro Hackathon")
Title: `Film Finder: a tip-of-my-tongue movie bot on Kimi K3.1 Pro + Cerebras that says "not sure" instead of guessing`
```
I built a Telegram bot (@kimi_filmfinder_bot) for those "what was that movie where..." moments.

How it works: Kimi K3.1 Pro on Cerebras extracts clues from your description (era, scenes, which details you might be misremembering), searches TMDB and Wikipedia, then verifies the real candidates against your clues. It answers only if the guess holds up; otherwise it asks one follow-up question or says it's not sure. It can only pick films the search actually returned, so it can't invent one.

Honest numbers: on 100 old solved r/tipofmytongue posts it was right on the first answer ~41% of the time and confidently wrong 14%; the rest it asked a question or said not sure. On 13 posts from the last two months (which the model can't have memorized) it was much weaker: 1 right, 2 asks pointing at the right film, 4 wrong. Tightening the verify step and testing on fresh posts is the next step.

Speed: same model and prompt, median of 5 runs: Cerebras 293 tok/s, Nebius 192, Together 44 (GPU hosts via Hugging Face). Cerebras had the highest throughput; on this short task Nebius still finished first because Kimi wrote fewer reasoning tokens there.

Video: [link] · Code: https://github.com/sivaratrisrinivas/film-finder
```
