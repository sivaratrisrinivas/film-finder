"""Eval find_film on a TOMT CSV (id, group, query, answer). Usage:
  python eval.py tomt_dev_100.csv [N]     -> runs/<csv>.jsonl + summary
  python eval.py --selftest               -> checks the title matcher
Hit = verdict "answer" AND title matches the gold Wikipedia title (year must agree within 1 if both known).
"""
import csv
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def norm(title):
    t = re.sub(r"\s*\([^)]*\)\s*$", "", title or "").lower().replace("&", "and")
    t = re.sub(r"[^a-z0-9 ]", "", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def gold_year(answer):
    m = re.search(r"\((\d{4}) film\)\s*$", answer)
    return int(m.group(1)) if m else None


def is_hit(result, answer):
    if result.get("verdict") != "answer" or norm(result.get("title")) != norm(answer):
        return False
    gy, y = gold_year(answer), str(result.get("year") or "")
    return not (gy and y.isdigit() and abs(int(y) - gy) > 1)


def selftest():
    a = lambda title, year="": {"verdict": "answer", "title": title, "year": year}
    cases = [
        (a("Into the Wild", "2007"), "Into the Wild (film)", True),
        (a("Noah", "2014"), "Noah (2013 film)", True),           # TMDB vs Wikipedia year drift
        (a("Noah", "1998"), "Noah (2013 film)", False),          # same title, different film
        (a("Charlie Wilson's War"), "Charlie Wilson's War (film)", True),
        (a("Commuter"), "The Commuter (film)", True),
        (a("Gone in Sixty Seconds", "1974"), "Gone in 60 Seconds (1974 film)", False),  # known gap: inspect by hand
        ({"verdict": "ask", "title": "Into the Wild"}, "Into the Wild (film)", False),
        ({"verdict": "busy"}, "Into the Wild (film)", False),
    ]
    for result, answer, want in cases:
        assert is_hit(result, answer) == want, (result, answer, want)
    print(f"selftest: {len(cases)} cases pass")


def summarize(rows):
    def block(rs, label):
        n = len(rs)
        live = [r for r in rs if r["result"]["verdict"] != "busy"]
        count = lambda v: sum(r["result"]["verdict"] == v for r in live)
        hits = sum(r["hit"] for r in live)
        wrong = sum(r["result"]["verdict"] == "answer" and not r["hit"] for r in live)
        secs = [r["result"]["timing"]["tool_seconds"] for r in live]
        toks = [r["result"]["timing"]["tokens"] for r in live]
        m = len(live) or 1
        print(f"{label}: n={n} busy={n - len(live)} | hit@1 {hits}/{len(live)} ({hits / m:.0%}) "
              f"wrong {wrong} ({wrong / m:.0%}) ask {count('ask')} not_sure {count('not_sure')} | "
              f"median {statistics.median(secs) if secs else 0:.1f}s, {statistics.median(toks) if toks else 0:.0f} tok")
    block(rows, "ALL")
    for g in sorted({r["group"] for r in rows}):
        block([r for r in rows if r["group"] == g], f"  {g}")


def main(path, n=None):
    from find_film import find_film
    posts = list(csv.DictReader(open(ROOT / path)))[: int(n) if n else None]
    out = ROOT / "runs" / (Path(path).stem + ".jsonl")
    out.parent.mkdir(exist_ok=True)
    rows = []
    with open(out, "w") as f:
        for i, p in enumerate(posts, 1):
            res = find_film(p["query"])
            row = {"id": p["id"], "group": p.get("group", ""), "answer": p["answer"],
                   "hit": is_hit(res, p["answer"]), "result": res}
            f.write(json.dumps(row) + "\n")
            f.flush()
            rows.append(row)
            mark = "HIT " if row["hit"] else res["verdict"].upper().ljust(4)
            print(f"[{i}/{len(posts)}] {mark} {p['answer']} <- {res.get('title')} ({res.get('year')})")
    summarize(rows)
    print(f"traces: {out}")


if __name__ == "__main__":
    selftest() if sys.argv[1] == "--selftest" else main(*sys.argv[1:])
