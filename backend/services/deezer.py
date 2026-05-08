import httpx
from typing import Optional

BASE = "https://api.deezer.com"

# Deezer genre_id → genre strings for our GENRE_PROFILES lookup
DEEZER_GENRE_MAP = {
    0:   [],
    132: ["pop"],
    116: ["hip hop", "rap"],
    122: ["reggaeton", "latin"],
    152: ["rock"],
    113: ["electronic", "edm", "dance pop"],
    165: ["r&b", "soul"],
    85:  ["alternative"],
    186: ["christian", "gospel"],
    106: ["electronic", "electropop"],
    466: ["folk"],
    144: ["reggae"],
    129: ["jazz"],
    84:  ["country"],
    67:  ["salsa", "latin"],
    169: ["classical"],
    75:  ["blues"],
    174: ["metal"],
    464: ["k-pop"],
    463: ["j-pop"],
    98:  ["afrobeats", "afropop"],
    197: ["bollywood", "hindi"],
}


class DeezerService:
    async def _get(self, path: str, params: dict = None) -> dict:
        url = path if path.startswith("http") else f"{BASE}/{path}"
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, params=params or {})
            r.raise_for_status()
            return r.json()

    async def find_track(self, title: str, artist: str) -> Optional[dict]:
        """
        Search Deezer for a track. Returns {track_id, artist_id, album_id, genre_id, genres}.
        Falls back to name-only search if structured search returns nothing.
        """
        for query in [f'artist:"{artist}" track:"{title}"', f"{artist} {title}"]:
            try:
                data = await self._get("search", params={"q": query, "limit": 1})
                items = data.get("data", [])
                if items:
                    t = items[0]
                    return {
                        "track_id":  t["id"],
                        "artist_id": t["artist"]["id"],
                        "album_id":  t["album"]["id"],
                        "genre_id":  None,
                        "genres":    [],
                    }
            except Exception:
                continue
        return None

    async def get_album_genres(self, album_id: int) -> list:
        """Fetch genre strings for a Deezer album."""
        try:
            data  = await self._get(f"album/{album_id}")
            names = [g["name"] for g in data.get("genres", {}).get("data", [])]
            gid   = data.get("genre_id")
            # Add genre_id mapped genres if not already covered
            if gid and gid in DEEZER_GENRE_MAP:
                for g in DEEZER_GENRE_MAP[gid]:
                    if g not in [n.lower() for n in names]:
                        names.append(g)
            return [n.lower() for n in names if n]
        except Exception:
            return []

    async def get_related_artists(self, deezer_artist_id: int, limit: int = 20) -> list:
        """
        Returns up to `limit` related artists.
        Each: {id, name, nb_fan}
        """
        try:
            data = await self._get(f"artist/{deezer_artist_id}/related", params={"limit": limit})
            return [
                {"id": a["id"], "name": a["name"], "nb_fan": a.get("nb_fan", 0)}
                for a in data.get("data", [])
            ]
        except Exception:
            return []

    async def get_artist_top_tracks(self, deezer_artist_id: int, limit: int = 4) -> list:
        """
        Returns top tracks for a Deezer artist.
        Each: {title, artist_name}
        """
        try:
            data = await self._get(f"artist/{deezer_artist_id}/top", params={"limit": limit})
            return [
                {"title": t["title"], "artist_name": t["artist"]["name"]}
                for t in data.get("data", [])
            ]
        except Exception:
            return []
