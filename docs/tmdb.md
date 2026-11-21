# TMDB API (trimmed)

Docs site (developer.themoviedb.org) could not be fetched from here on 2026-11-21. **Only `search/movie` has been verified live.** Mark the other endpoints verified once a call succeeds.

## Auth
`Authorization: Bearer $TMDB_TOKEN` (v4 read token from `.env`; strip quotes and whitespace). Base: `https://api.themoviedb.org/3`.

## search/movie (VERIFIED 2026-11-21)
`GET /search/movie?query=Memories&year=1995` returns `{page, results[], total_pages, total_results}`.
Result fields seen: `id, title, original_title, original_language, overview, release_date, genre_ids, popularity, vote_average, vote_count, poster_path, backdrop_path, adult, video`.
Params (not verified beyond query/year): `query`, `year`, `primary_release_year`, `language`, `include_adult`, `page`.

## Unverified: check before use
- `GET /movie/{id}` for details, `append_to_response=keywords,credits`
- `GET /movie/{id}/keywords`
- `GET /search/keyword?query=`
- `GET /discover/movie?with_keywords=&primary_release_date.gte=&with_original_language=`
- `GET /genre/movie/list`
