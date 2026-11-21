# Wikipedia / MediaWiki API (trimmed)

Base: `https://en.wikipedia.org/w/api.php`. No auth. Send a descriptive `User-Agent` (e.g. `film-finder-hackathon/0.1`). Fetched and verified 2026-11-21.

## Full-text search (VERIFIED)
`GET ?action=query&list=search&srsearch=Magnetic+Rose+anime&format=json&srlimit=5`
returns `query.search[]` with `{ns, title, pageid, size, wordcount, snippet, timestamp}`. `snippet` contains `<span class="searchmatch">` HTML, so strip tags. The verified call returned "Memories (1995 film)" as the top hit.

## Unverified: check before use
- Plot/intro text: `?action=query&prop=extracts&explaintext=1&exintro=1&titles=<title>&format=json`
- Full plain text: `prop=extracts&explaintext=1` (no `exintro`)
