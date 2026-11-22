"""find_film(description): clues (Kimi) -> search (TMDB + Wikipedia) -> verify (Kimi)."""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import tools

URL = "https://api.cerebras.ai/v1/chat/completions"
MODEL = "moonshotai-kimi-k3.1-pro-trial"
TIMEOUT = 20  # seconds; the bot wants a fast "busy". eval.py raises it.

# System prompts are constants so they stay byte-stable and get cached.
CLUES_PROMPT = """You help identify films from half-remembered descriptions (like r/tipofmytongue).
Read the user's description and extract structured clues. Then propose:
- guesses: up to 5 specific film titles that might match, best first (use the original or English title as listed on TMDB). Empty if you have no idea.
- wiki_queries: 3 short keyword queries for Wikipedia full-text search built from the most distinctive plot details (no filler words).
Mark details that are probably misremembered in possibly_wrong. Use empty strings or lists for unknown fields."""

VERIFY_PROMPT = """You check candidate films against a user's half-remembered description.
For each candidate you get its metadata and plot summary. Decide:
- "answer": one candidate clearly matches the most distinctive clues and nothing important contradicts it.
- "ask": one or more candidates are plausible but you cannot be sure; write ONE short follow-up question for the user that would best tell them apart or confirm the best one.
- "not_sure": no candidate fits well, or the text is not a film description.
Never pick a film that is not in the candidate list. Allow for misremembered details, but a wrong answer is much worse than "not_sure".
Do not "answer" when: the match rests only on a premise many films share (a parasite, kids with powers, a haunted house); a mismatched clue contradicts a core plot event (who dies, who is revived, how it ends); or the candidate's year contradicts the user's era. Use "ask" instead.
If the candidate is a book, story or remake with several film versions, use "ask" to find out which one, unless the user's era picks one.
year is the release year of the film you pick: from the candidate data, or from the user's era if the candidate has none. Empty if unknown.
candidate_index is the 0-based index of the best candidate (-1 if none). List the user's clues that the best candidate matches and contradicts."""

CLUES_SCHEMA = {
    "type": "object",
    "properties": {
        "era": {"type": "string"},
        "genre": {"type": "string"},
        "language_country": {"type": "string"},
        "key_details": {"type": "array", "items": {"type": "string"}},
        "possibly_wrong": {"type": "array", "items": {"type": "string"}},
        "guesses": {"type": "array", "items": {"type": "string"}},
        "wiki_queries": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["era", "genre", "language_country", "key_details", "possibly_wrong", "guesses", "wiki_queries"],
    "additionalProperties": False,
}

VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["answer", "ask", "not_sure"]},
        "candidate_index": {"type": "integer"},
        "matched_clues": {"type": "array", "items": {"type": "string"}},
        "mismatched_clues": {"type": "array", "items": {"type": "string"}},
        "follow_up_question": {"type": "string"},
        "year": {"type": "string"},
    },
    "required": ["verdict", "candidate_index", "matched_clues", "mismatched_clues", "follow_up_question", "year"],
    "additionalProperties": False,
}


class Busy(Exception):
    pass


def _key():
    key = os.environ.get("CEREBRAS_API_KEY")
    if not key:
        for line in (Path(__file__).parent / ".env").read_text().splitlines():
            if line.startswith("CEREBRAS_API_KEY="):
                key = line.split("=", 1)[1]
    return key.strip().strip("\"'").strip()


def kimi(system, user, schema, name, effort, stats):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "reasoning_effort": effort,
        "response_format": {"type": "json_schema", "json_schema": {"name": name, "schema": schema, "strict": True}},
        "max_completion_tokens": 8000,
        "prompt_cache_key": "film-finder",
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {_key()}"})
    for delay in (1, 2, 4, 8, None):  # retry on 429 (~15s total), then give up as "busy"
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.loads(r.read())
            break
        except TimeoutError:  # Cerebras sometimes queues silently instead of returning 429
            raise Busy()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            if delay is None:
                raise Busy()
            time.sleep(delay)
    stats["kimi_seconds"] += data["time_info"]["total_time"]
    stats["tokens"] += data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]
    msg = data["choices"][0]["message"]
    if "content" not in msg:
        print(f"kimi: no content, finish_reason={data['choices'][0].get('finish_reason')}", file=sys.stderr)
        raise Busy()
    return json.loads(msg["content"])


def _safe(fn, *args):
    try:
        return fn(*args)
    except Exception:  # TMDB is flaky on the home network; carry on with what we have
        return None


def search(clues):
    """Return up to 10 candidates: {title, year, tmdb_id, language, genres, summary}."""
    with ThreadPoolExecutor(8) as pool:
        tmdb_hits = pool.map(lambda g: _safe(tools.tmdb_search, g), clues["guesses"][:5])
        wiki_hits = pool.map(lambda q: _safe(tools.wiki_search, q + " film", 3),
                             clues["guesses"][:5] + clues["wiki_queries"][:3])
        tmdb_hits, wiki_hits = list(tmdb_hits), list(wiki_hits)

    cands, seen = [], set()
    for hits in tmdb_hits:
        for h in (hits or [])[:2]:
            if h["tmdb_id"] not in seen:
                seen.add(h["tmdb_id"])
                cands.append({"tmdb_id": h["tmdb_id"], "title": h["title"], "year": h["year"]})
    titles = {c["title"].lower() for c in cands}
    for hits in wiki_hits:
        for h in (hits or [])[:2]:
            base = h["title"].split(" (")[0]
            if base.lower() not in titles and not base.startswith("List of"):
                titles.add(base.lower())
                cands.append({"tmdb_id": None, "title": base, "wiki_title": h["title"], "year": ""})
    cands = cands[:10]

    def enrich(c):
        if c["tmdb_id"]:
            d = _safe(tools.tmdb_details, c["tmdb_id"])
            if d:
                c.update(language=d["language"], genres=d["genres"], poster_url=d["poster_url"],
                         summary=(d["overview"] + " Keywords: " + ", ".join(d["keywords"][:15]))[:900])
                return c
        c["summary"] = (_safe(tools.wiki_extract, c.get("wiki_title") or c["title"]) or "")[:900]
        return c

    with ThreadPoolExecutor(8) as pool:
        cands = list(pool.map(enrich, cands))
    # Wikipedia hits that aren't films (people, places) usually lack "film" in the intro.
    return [c for c in cands if c["tmdb_id"] or "film" in c["summary"].lower()]


def find_film(description):
    t0 = time.time()
    stats = {"kimi_seconds": 0.0, "tokens": 0}
    try:
        clues = kimi(CLUES_PROMPT, description, CLUES_SCHEMA, "clues", "low", stats)
        cands = search(clues)
        listing = "\n\n".join(
            f"[{i}] {c['title']} ({c['year']}) lang={c.get('language', '?')} genres={c.get('genres', '?')}\n{c['summary']}"
            for i, c in enumerate(cands))
        user = f"Description:\n{description}\n\nExtracted clues:\n{json.dumps(clues)}\n\nCandidates:\n{listing or '(none)'}"
        v = kimi(VERIFY_PROMPT, user, VERIFY_SCHEMA, "verdict", "medium", stats)
    except Busy:
        return {"verdict": "busy", "message": "Kimi is busy right now, try again in a minute.",
                "timing": {**stats, "tool_seconds": round(time.time() - t0, 2)}}

    best = cands[v["candidate_index"]] if 0 <= v["candidate_index"] < len(cands) else {}
    if v["verdict"] != "not_sure" and best and not best.get("poster_url"):
        hit = (_safe(tools.tmdb_search, best["title"], v["year"] or None) or [None])[0]
        if hit:
            best.update(tmdb_id=hit["tmdb_id"], year=best["year"] or hit["year"],
                        poster_url=(_safe(tools.tmdb_details, hit["tmdb_id"]) or {}).get("poster_url"))
    return {
        "verdict": v["verdict"],
        "title": best.get("title"), "year": best.get("year"), "tmdb_id": best.get("tmdb_id"),
        "poster_url": best.get("poster_url"),
        "matched_clues": v["matched_clues"], "mismatched_clues": v["mismatched_clues"],
        "follow_up_question": v["follow_up_question"] if v["verdict"] == "ask" else "",
        "timing": {"kimi_seconds": round(stats["kimi_seconds"], 2), "tokens": stats["tokens"],
                   "tool_seconds": round(time.time() - t0, 2)},
    }


if __name__ == "__main__":
    if sys.argv[1] == "--dev":  # python find_film.py --dev 5
        import csv
        rows = list(csv.DictReader(open(Path(__file__).parent / "tomt_dev_100.csv")))[:int(sys.argv[2])]
        for row in rows:
            r = find_film(row["query"])
            print(f"{row['id']} | expected: {row['answer']} | got: {r['verdict']} {r.get('title')} ({r.get('year')}) | {r['timing']}")
    else:
        print(json.dumps(find_film(sys.argv[1]), indent=2))
