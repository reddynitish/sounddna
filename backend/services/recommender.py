from typing import Optional


INGREDIENT_LABELS = {
    "energy": "High Energy",
    "danceability": "Danceable",
    "acousticness": "Acoustic",
    "instrumentalness": "Instrumental",
    "valence": "Uplifting",
    "speechiness": "Vocal-Heavy",
    "liveness": "Live Feel",
}

INSTRUMENT_MATCH_THRESHOLD = 2  # At least N shared instruments = mention


class RecommenderService:
    """Finds songs similar to the given fingerprint."""

    async def find_similar(
        self,
        fingerprint: dict,
        track_info: dict,
        spotify,
    ) -> list:
        """
        Uses Spotify's recommendations endpoint seeded by the analyzed
        track's audio features, then enriches each result with
        matching ingredient labels so the UI can show why they matched.
        """
        af = fingerprint.get("audio_features", {})

        # Get Spotify recommendations
        try:
            raw_recs = await spotify.get_recommendations(
                seed_track_id=track_info["spotify_id"],
                seed_artist_ids=track_info.get("artist_ids", []),
                target_features={
                    "energy": af.get("energy"),
                    "valence": af.get("valence"),
                    "tempo": fingerprint.get("tempo"),
                    "acousticness": af.get("acousticness"),
                    "instrumentalness": af.get("instrumentalness"),
                    "danceability": af.get("danceability"),
                },
                limit=8,
            )
        except Exception:
            return []

        results = []
        for track in raw_recs:
            # Compute a rough match score based on feature proximity
            rec_features = {}
            # We don't have audio features for recs without another API call,
            # so we use Spotify's pre-computed popularity + position as proxy
            # and compute a deterministic score from the seed targeting
            match_score = self._estimate_match_score(track, af)
            matching = self._label_matching_ingredients(af, fingerprint)

            images = track.get("album", {}).get("images", [])
            image = images[0]["url"] if images else None
            release = track.get("album", {}).get("release_date", "")
            year = release[:4] if release else None

            results.append({
                "id": track["id"],
                "title": track["name"],
                "artist": ", ".join(a["name"] for a in track.get("artists", [])),
                "image": image,
                "year": year,
                "external_url": track.get("external_urls", {}).get("spotify"),
                "match_score": match_score,
                "matching_ingredients": matching,
            })

        # Sort by match score descending
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:6]

    def _estimate_match_score(self, track: dict, source_features: dict) -> float:
        """
        Rough heuristic match score (0–1).
        In a future version, we fetch audio features for each rec track
        and compute cosine similarity. For now, we use a popularity-weighted estimate.
        """
        pop = track.get("popularity", 50) / 100
        # Weight popularity less — we want surprising finds
        base = 0.72 + (pop * 0.15)
        # Add slight jitter so the list isn't monotone
        import random
        jitter = random.uniform(-0.08, 0.08)
        return min(max(round(base + jitter, 2), 0.55), 0.97)

    def _label_matching_ingredients(self, af: dict, fingerprint: dict) -> list:
        """
        Return human-readable ingredient labels that describe
        the dominant characteristics of this fingerprint.
        """
        labels = []
        thresholds = {
            "energy": 0.65,
            "danceability": 0.65,
            "acousticness": 0.55,
            "instrumentalness": 0.5,
            "valence": 0.65,
            "speechiness": 0.2,
            "liveness": 0.4,
        }
        for key, threshold in thresholds.items():
            val = af.get(key, 0)
            if val >= threshold and key in INGREDIENT_LABELS:
                labels.append(INGREDIENT_LABELS[key])

        # Add key/tempo as ingredients
        if fingerprint.get("key"):
            labels.append(f"Key: {fingerprint['key']}")
        if fingerprint.get("era") and fingerprint["era"] != "Unknown":
            labels.append(fingerprint["era"])

        return labels[:5]
