import asyncio
from services.fingerprint import estimate_features_from_genres, get_era, detect_language
from services.deezer import DeezerService

deezer = DeezerService()

FEATURE_WEIGHTS = {
    "energy":           1.5,
    "danceability":     1.5,
    "valence":          1.3,
    "acousticness":     1.2,
    "instrumentalness": 1.0,
    "speechiness":      0.7,
    "liveness":         0.5,
}

INGREDIENT_CHECKS = [
    ("energy",           0.65, "High Energy"),
    ("danceability",     0.65, "Danceable"),
    ("valence",          0.65, "Uplifting"),
    ("acousticness",     0.55, "Acoustic"),
    ("instrumentalness", 0.50, "Instrumental"),
    ("speechiness",      0.25, "Rap/Spoken"),
    ("liveness",         0.40, "Live Feel"),
]


class RecommenderService:
    async def enrich_track_info_with_genres(self, track_info: dict) -> list:
        """
        Try to get genre strings for the source track via Deezer album lookup.
        Returns list of genre strings (may be empty).
        """
        dz = await deezer.find_track(track_info["name"], track_info["artist"].split(",")[0].strip())
        if not dz:
            return []
        genres = await deezer.get_album_genres(dz["album_id"])
        return genres, dz.get("artist_id")

    async def find_similar(self, fingerprint: dict, track_info: dict, spotify) -> list:
        source_af   = fingerprint.get("audio_features", {})
        source_era  = fingerprint.get("era")
        source_lang = fingerprint.get("language", "English")
        source_name = track_info.get("name", "")
        source_artist = track_info.get("artist", "")

        # 1. Find source on Deezer → get Deezer artist ID + album genres
        dz_info = await deezer.find_track(
            source_name,
            source_artist.split(",")[0].strip()
        )
        if not dz_info:
            return []

        dz_artist_id = dz_info["artist_id"]

        # 2. Get related artists from Deezer (real music-graph similarity)
        related = await deezer.get_related_artists(dz_artist_id, limit=20)
        if not related:
            return []

        # Take top 5 by fan count (fan count ≈ prominence, keeps results relevant)
        related.sort(key=lambda a: a["nb_fan"], reverse=True)
        top_artists = related[:5]

        # 3. Fetch top tracks for all 5 artists concurrently
        tasks = [deezer.get_artist_top_tracks(a["id"], limit=4) for a in top_artists]
        artist_tracks_list = await asyncio.gather(*tasks, return_exceptions=True)

        # 4. Collect all candidate (title, artist_name) pairs, filter source artist
        candidates_raw = []
        source_artist_lower = source_artist.lower()
        seen_queries = set()

        for i, artist_tracks in enumerate(artist_tracks_list):
            if isinstance(artist_tracks, Exception) or not artist_tracks:
                continue
            related_artist_name = top_artists[i]["name"]
            position_rank = i  # 0 = most similar by fan count

            for track in artist_tracks:
                title       = track["title"]
                artist_name = track["artist_name"]

                # Filter: skip if this track features the source artist
                if source_artist.split(",")[0].strip().lower() in title.lower():
                    continue
                if source_name.lower() in title.lower():
                    continue

                query_key = f"{title.lower()}::{artist_name.lower()}"
                if query_key in seen_queries:
                    continue
                seen_queries.add(query_key)

                candidates_raw.append({
                    "title":       title,
                    "artist_name": artist_name,
                    "position":    position_rank,
                })

        if not candidates_raw:
            return []

        # 5. Cross-reference all candidates to Spotify concurrently
        search_tasks = [
            spotify.search_track(f"{c['artist_name']} {c['title']}")
            for c in candidates_raw
        ]
        spotify_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # 6. Build scored results
        results = []
        seen_ids = {track_info["spotify_id"]}

        for raw, sp_result in zip(candidates_raw, spotify_results):
            if isinstance(sp_result, Exception) or not sp_result:
                continue

            sp_id = sp_result.get("spotify_id")
            if not sp_id or sp_id in seen_ids:
                continue
            seen_ids.add(sp_id)

            # Estimate rec features from its artist name (best we can do without API)
            # We use the Deezer position as primary quality signal
            match_score = self._compute_score(raw["position"], sp_result, source_af, source_era, source_lang)
            matching    = self._label_ingredients(source_af, raw["position"], fingerprint, sp_result)

            results.append({
                "id":                   sp_id,
                "title":                sp_result["name"],
                "artist":               sp_result["artist"],
                "image":                sp_result["image"],
                "year":                 sp_result["year"],
                "external_url":         sp_result["external_url"],
                "match_score":          match_score,
                "matching_ingredients": matching,
            })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:6]

    def _compute_score(
        self,
        deezer_position: int,
        sp_result: dict,
        source_af: dict,
        source_era: str,
        source_lang: str,
    ) -> float:
        """
        Score = Deezer similarity position (primary) + popularity blend.
        Position 0 = closest related artist, 4 = least similar of the 5 picked.
        """
        # Position weight: 0→0.88, 1→0.82, 2→0.76, 3→0.70, 4→0.64
        position_score = max(0.64, 0.88 - deezer_position * 0.06)

        # Popularity blend (don't surface only mega-hits, but weight them slightly)
        pop = (sp_result.get("popularity") or 50) / 100.0
        score = position_score * 0.80 + pop * 0.20

        # Era bonus
        if sp_result.get("year") and get_era(sp_result["year"]) == source_era:
            score = min(score + 0.03, 0.97)

        return round(min(max(score, 0.30), 0.97), 3)

    def _label_ingredients(
        self,
        source_af: dict,
        deezer_position: int,
        fingerprint: dict,
        sp_result: dict,
    ) -> list:
        labels = []

        # Surface dominant source characteristics as shared signals
        prominent = [
            ("energy",           0.70, "High Energy"),
            ("danceability",     0.70, "Danceable"),
            ("valence",          0.70, "Uplifting"),
            ("acousticness",     0.60, "Acoustic"),
            ("instrumentalness", 0.55, "Instrumental"),
            ("speechiness",      0.28, "Rap/Spoken"),
        ]
        for feat, threshold, label in prominent:
            if source_af.get(feat, 0) >= threshold:
                labels.append(label)
            if len(labels) >= 2:
                break

        # Era match
        if sp_result.get("year") and fingerprint.get("era") and get_era(sp_result["year"]) == fingerprint["era"]:
            labels.append(fingerprint["era"])

        # Language signal
        lang = fingerprint.get("language")
        if lang and lang != "English":
            labels.append(lang)

        # Similarity tier label
        if deezer_position == 0:
            labels.append("Closest Match")
        elif deezer_position <= 1:
            labels.append("Strong Match")

        return labels[:4]
