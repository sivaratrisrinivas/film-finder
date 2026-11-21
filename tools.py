"""TMDB and Wikipedia lookups, each cached on disk as JSON in .cache/."""
import hashlib
import json
import os
import re
from pathlib import Path

import httpx2

CACHE = Path(__file__).parent / ".cache"
CACHE.mkdir(exist_ok=True)
TMDB = "https://api.themoviedb.org/3"
WIKI = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "film-finder-hackathon/0.1"}
stats = {"hits": 0, "misses": 0}


def _token():
    tok = os.environ.get("TMDB_TOKEN")
    if not tok:
        for line in (Path(__file__).parent / ".env").read_text().splitlines():
            if line.startswith("TMDB_TOKEN="):
                tok = line.split("=", 1)[1]
    return tok.strip().strip("\"'").strip()


def _get(url, params, headers):
    key = hashlib.sha256(json.dumps([url, params], sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        stats["hits"] += 1
        return json.loads(path.read_text())
    stats["misses"] += 1
    r = httpx2.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    path.write_text(json.dumps(data))
    return data


def tmdb_search(query, year=None):
    params = {"query": query}
    if year:
        params["year"] = year
    data = _get(f"{TMDB}/search/movie", params, {"Authorization": f"Bearer {_token()}"})
    return [
        {"tmdb_id": r["id"], "title": r["title"], "original_title": r["original_title"],
         "year": (r.get("release_date") or "")[:4], "language": r["original_language"],
         "overview": r["overview"]}
        for r in data["results"][:5]
    ]


def tmdb_details(tmdb_id):
    d = _get(f"{TMDB}/movie/{tmdb_id}", {"append_to_response": "keywords"},
             {"Authorization": f"Bearer {_token()}"})
    return {
        "tmdb_id": d["id"], "title": d["title"], "original_title": d["original_title"],
        "year": (d.get("release_date") or "")[:4], "language": d["original_language"],
        "countries": d.get("origin_country", []), "runtime": d.get("runtime"),
        "genres": [g["name"] for g in d.get("genres", [])],
        "keywords": [k["name"] for k in d.get("keywords", {}).get("keywords", [])],
        "overview": d["overview"],
        "poster_url": f"https://image.tmdb.org/t/p/w500{d['poster_path']}" if d.get("poster_path") else None,
    }


def wiki_search(query, limit=5):
    data = _get(WIKI, {"action": "query", "list": "search", "srsearch": query,
                       "srlimit": limit, "format": "json"}, UA)
    return [{"title": s["title"], "snippet": re.sub(r"<[^>]+>", "", s["snippet"])}
            for s in data["query"]["search"]]


def wiki_extract(title):
    data = _get(WIKI, {"action": "query", "prop": "extracts", "explaintext": 1, "exintro": 1,
                       "titles": title, "format": "json"}, UA)
    page = next(iter(data["query"]["pages"].values()))
    return page.get("extract", "")


if __name__ == "__main__":
    for c in tmdb_search("Memories", 1995)[:2]:
        print("TMDB:", c["tmdb_id"], c["title"], c["year"])
    d = tmdb_details(tmdb_search("Memories", 1995)[0]["tmdb_id"])
    print("Details:", d["title"], d["year"], d["genres"], d["keywords"][:5], d["poster_url"])
    for s in wiki_search("Magnetic Rose anime")[:2]:
        print("Wiki:", s["title"], "|", s["snippet"][:80])
    print("Extract:", wiki_extract("Memories (1995 film)")[:120])
    print("Cache:", stats)
