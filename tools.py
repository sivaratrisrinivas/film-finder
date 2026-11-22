"""TMDB and Wikipedia lookups, each cached on disk as JSON in .cache/."""
import hashlib
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

CACHE = Path(__file__).parent / ".cache"
CACHE.mkdir(exist_ok=True)
TMDB = "https://api.tmdb.org/3"  # api.themoviedb.org gets most TLS handshakes reset on Indian networks
KEY_TMDB = "https://api.themoviedb.org/3"  # cache keys keep the old host so existing entries still hit
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
    key = hashlib.sha256(json.dumps([url.replace(TMDB, KEY_TMDB), params], sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        stats["hits"] += 1
        return json.loads(path.read_text())
    stats["misses"] += 1
    # urllib, not httpx2: Wikimedia returns 403 to httpx2 even with a proper User-Agent.
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers=headers)
    for attempt in range(8):  # Indian networks reset most TMDB TLS handshakes; resets are fast
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            break
        except (ConnectionResetError, urllib.error.URLError) as e:
            if attempt == 7 or isinstance(e, urllib.error.HTTPError):
                raise
            time.sleep(0.1)
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
    return [{"title": s["title"], "snippet": html.unescape(re.sub(r"<[^>]+>", "", s["snippet"]))}
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
