"""Pull solved r/tipofmytongue FILM posts with confirmed answers.
Source: webis/tip-of-my-tongue-known-item-search-triplets (Hugging Face).
  python get_30_film_posts.py                        # 30 for the manual Google check
  python get_30_film_posts.py --general 80 --non-english 20 --out tomt_dev_100.csv
"""
import argparse
import re

import pandas as pd
from datasets import load_dataset

SEED = 7
NON_ENGLISH_HINTS = re.compile(
    r"\b(indian|bollywood|tollywood|telugu|tamil|malayalam|kannada|hindi|korean|"
    r"japanese|chinese|hong kong|thai|iranian|persian|turkish|russian|soviet|"
    r"french|italian|spanish|german|polish|czech|mexican|brazilian|subtitle[sd]?|dubbed)\b",
    re.IGNORECASE,
)
FILM_TITLE = re.compile(r"\((?:\d{4} )?film\)$")


def answer_title(url):
    return url.rsplit("/wiki/", 1)[-1].replace("_", " ")


def leaks_title(query, title):
    name = re.sub(r"\s*\(.*?\)\s*$", "", title).lower()
    return len(name) > 3 and name in query.lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--general", type=int, default=20)
    ap.add_argument("--non-english", type=int, default=10)
    ap.add_argument("--out", default="tomt_30_films.csv")
    args = ap.parse_args()

    ds = load_dataset("webis/tip-of-my-tongue-known-item-search-triplets", split="train")
    df = ds.select_columns(["qid", "query", "url_wikipedia_positive"]).to_pandas()
    df["answer"] = df["url_wikipedia_positive"].map(answer_title)
    df = df[df["answer"].str.contains(FILM_TITLE)]
    df = df[df["query"].str.len().between(150, 1500)]
    df = df[~df.apply(lambda r: leaks_title(r["query"], r["answer"]), axis=1)]
    df = df.drop_duplicates("answer")

    non_eng = df[df["query"].str.contains(NON_ENGLISH_HINTS)]
    general = df.drop(non_eng.index)
    pick = pd.concat([
        general.sample(min(args.general, len(general)), random_state=SEED).assign(group="general"),
        non_eng.sample(min(args.non_english, len(non_eng)), random_state=SEED).assign(group="non_english_hint"),
    ]).sample(frac=1, random_state=SEED)

    out = pd.DataFrame({
        "id": pick["qid"],
        "group": pick["group"],
        "query": pick["query"].str.replace(r"\s+", " ", regex=True).str.strip(),
        "answer": pick["answer"],
        "wikipedia_url": pick["url_wikipedia_positive"].str.replace(" ", "_"),
        "reddit_url": "https://www.reddit.com/r/tipofmytongue/comments/" + pick["qid"],
        "google_correct": "",
        "gemini_correct": "",
    })
    out.to_csv(args.out, index=False)
    print(f"{len(df):,} solved film posts available. Wrote {len(out)} to {args.out}")
    print(out.groupby("group").size().to_string())


if __name__ == "__main__":
    main()
