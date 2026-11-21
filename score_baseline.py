import pandas as pd
f = "tomt_30_films.csv"
d = pd.read_csv(f, dtype=str).fillna("")
for i, r in d.iterrows():
    if r.google_correct and r.gemini_correct:
        continue
    print(f"\n[{i+1}/30]\n{r.query}\n")
    input("Paste it into Google + Gemini, then press Enter to see the answer...")
    print(f"ANSWER: {r.answer}")
    d.at[i, "google_correct"] = input("Google got it? (y/n): ").strip().lower()[:1]
    d.at[i, "gemini_correct"] = input("Gemini got it? (y/n): ").strip().lower()[:1]
    d.to_csv(f, index=False)
for col in ["google_correct", "gemini_correct"]:
    print(col, (d[col] == "y").sum(), "/ 30")
