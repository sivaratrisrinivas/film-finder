# TMDB API (trimmed)

Docs site (developer.themoviedb.org) could not be fetched from here on 2026-11-21. **Verified live: `search/movie`, `/movie/{id}` with keywords.** Mark the other endpoints verified once a call succeeds.

## Auth
`Authorization: Bearer $TMDB_TOKEN` (v4 read token from `.env`; strip quotes and whitespace). Base: `https://api.themoviedb.org/3`.

## search/movie (VERIFIED 2026-11-21)
`GET /search/movie?query=Memories&year=1995` returns `{page, results[], total_pages, total_results}`.
Result fields seen: `id, title, original_title, original_language, overview, release_date, genre_ids, popularity, vote_average, vote_count, poster_path, backdrop_path, adult, video`.
Params (not verified beyond query/year): `query`, `year`, `primary_release_year`, `language`, `include_adult`, `page`.

## Details (VERIFIED 2026-11-22)
`GET /movie/{id}?append_to_response=keywords` returns details plus `keywords.keywords[] {id, name}`. Fields used: `origin_country, genres, runtime, poster_path` (poster at `https://image.tmdb.org/t/p/w500{poster_path}`).

**Network:** the home connection resets about half of TLS handshakes to api.themoviedb.org (the hotspot works). `tools.py` retries 5 times.

## Unverified: check before use
- `append_to_response=credits`
- `GET /movie/{id}/keywords`
- `GET /search/keyword?query=`
- `GET /discover/movie?with_keywords=&primary_release_date.gte=&with_original_language=`
- `GET /genre/movie/list`
