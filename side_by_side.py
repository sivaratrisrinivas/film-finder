"""Speed race: the same Kimi K3.1 Pro verify prompt on Cerebras vs GPU providers (via HF).

  python side_by_side.py [dev_row_index]     (default 2 = Into the Wild)

Builds the verify input once (clues + search, not timed), then streams the same request
to all three backends at once and shows a live race. The bot itself only uses Cerebras.
"""
import csv
import json
import statistics
import sys
import threading
import time
import urllib.request
from pathlib import Path

import find_film as ff

ROOT = Path(__file__).parent
HF_URL = "https://router.huggingface.co/v1/chat/completions"
RACERS = [  # (label, url, model, env key)
    ("Cerebras", ff.URL, ff.MODEL, "CEREBRAS_API_KEY"),
    ("Nebius (GPU)", HF_URL, "moonshotai/Kimi-K3.1-Pro:nebius", "HF_TOKEN"),
    ("Together (GPU)", HF_URL, "moonshotai/Kimi-K3.1-Pro:together", "HF_TOKEN"),
]
PLAIN = ff.VERIFY_PROMPT + "\nReply in 3 short lines: verdict, title (year), and why."


def env(name):
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip("\"'").strip()
    sys.exit(f"{name} missing from .env")


def verify_input(description):
    stats = {"kimi_seconds": 0.0, "tokens": 0}
    clues = ff.kimi(ff.CLUES_PROMPT, description, ff.CLUES_SCHEMA, "clues", "low", stats)
    cands = ff.search(clues)
    listing = "\n\n".join(
        f"[{i}] {c['title']} ({c['year']}) lang={c.get('language', '?')} genres={c.get('genres', '?')}\n{c['summary']}"
        for i, c in enumerate(cands))
    return f"Description:\n{description}\n\nExtracted clues:\n{json.dumps(clues)}\n\nCandidates:\n{listing or '(none)'}"


def race(label, url, model, key, user, st):
    body = json.dumps({
        "model": model, "stream": True, "stream_options": {"include_usage": True},
        "reasoning_effort": "medium", "max_completion_tokens": 8000,
        "messages": [{"role": "system", "content": PLAIN}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            for raw in r:
                line = raw.decode().strip()
                if not line.startswith("data:") or line == "data: [DONE]":
                    continue
                chunk = json.loads(line[5:])
                if chunk.get("usage"):
                    st["usage"] = chunk["usage"]
                for ch in chunk.get("choices") or []:
                    d = ch.get("delta") or {}
                    piece = (d.get("reasoning") or "") + (d.get("reasoning_content") or "")
                    if piece or d.get("content"):
                        st.setdefault("first", time.time() - t0)
                        st["chunks"] += 1
                        st["answer"] += d.get("content") or ""
    except Exception as e:
        st["error"] = f"{type(e).__name__}: {getattr(e, 'code', '')} {e}"[:120]
    st["done"] = time.time() - t0


def show(states, t0):
    lines = []
    for (label, *_), st in zip(RACERS, states):
        el = st.get("done") or (time.time() - t0)
        toks = (st.get("usage") or {}).get("completion_tokens") or st["chunks"]
        gen = el - st.get("first", el)
        rate = f"{toks / gen:6.0f} tok/s" if gen > 0.2 else "     - tok/s"
        first = f"first token {st['first']:5.2f}s" if "first" in st else "first token   ...  "
        status = st.get("error") or (f"DONE {st['done']:6.2f}s" if "done" in st else f"{el:6.1f}s ...")
        lines.append(f"{label:<15} {first} | {toks:5d} tok | {rate} | {status}")
    return lines


def main(idx=2, runs=1):
    row = list(csv.DictReader(open(ROOT / "tomt_dev_100.csv")))[int(idx)]
    print(f"Post: {row['query'][:200]}...\n(building candidates: clues + search, not timed)")
    cache = ROOT / ".cache" / f"side_by_side_{idx}.json"
    if cache.exists():
        user = json.loads(cache.read_text())
    else:
        user = verify_input(row["query"])
        cache.write_text(json.dumps(user))
    print("\nSame model (Kimi K3.1 Pro), same prompt, three providers:\n")
    rounds = []
    for _ in range(int(runs)):
        states = [{"chunks": 0, "answer": ""} for _ in RACERS]
        t0 = time.time()
        threads = [threading.Thread(target=race, args=(lbl, url, model, env(k), user, st))
                   for (lbl, url, model, k), st in zip(RACERS, states)]
        for t in threads:
            t.start()
        print("\n" * (len(RACERS) - 1))
        while any(t.is_alive() for t in threads):
            print(f"\033[{len(RACERS)}F" + "\n".join(l + "\033[K" for l in show(states, t0)), flush=True)
            time.sleep(0.1)
        print(f"\033[{len(RACERS)}F" + "\n".join(l + "\033[K" for l in show(states, t0)) + "\n")
        rounds.append(states)
    for (label, *_), st in zip(RACERS, rounds[-1]):
        print(f"\n--- {label} ---\n{st['answer'].strip()[:400]}")
    if len(rounds) > 1:
        print(f"\nMedians over {len(rounds)} runs (errors excluded):")
        for i, (label, *_) in enumerate(RACERS):
            ok = [r[i] for r in rounds if "error" not in r[i] and "first" in r[i]]
            toks = [(st.get("usage") or {}).get("completion_tokens") or st["chunks"] for st in ok]
            rate = [t / (st["done"] - st["first"]) for t, st in zip(toks, ok) if st["done"] - st["first"] > 0]
            med = lambda xs: statistics.median(xs) if xs else float("nan")
            print(f"{label:<15} first token {med([s['first'] for s in ok]):5.2f}s | {med(rate):6.0f} tok/s | "
                  f"total {med([s['done'] for s in ok]):6.2f}s | {len(ok)}/{len(rounds)} ok")


if __name__ == "__main__":
    main(*sys.argv[1:])
