import os
import re
import httpx
import base64
from typing import Optional


class SpotifyService:
    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        self.client_id     = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        creds = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self.AUTH_URL,
                headers={"Authorization": f"Basic {creds}"},
                data={"grant_type": "client_credentials"},
            )
            r.raise_for_status()
            self._token = r.json()["access_token"]
        return self._token

    async def _get(self, path: str, params: dict = None) -> dict:
        token = await self._get_token()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/{path}",
                headers={"Authorization": f"Bearer {token}"},
                params=params or {},
            )
            if r.status_code == 401:
                self._token = None
                token = await self._get_token()
                r = await client.get(
                    f"{self.BASE_URL}/{path}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params or {},
                )
            r.raise_for_status()
            return r.json()

    def _extract_spotify_id(self, url: str) -> str:
        match = re.search(r"track/([A-Za-z0-9]+)", url)
        if not match:
            raise ValueError("Could not extract Spotify track ID from URL.")
        return match.group(1)

    async def get_track_info(self, spotify_url: str) -> dict:
        track_id = self._extract_spotify_id(spotify_url)
        data = await self._get(f"tracks/{track_id}")
        return self._parse_track(data)

    async def get_track_by_id(self, track_id: str) -> dict:
        data = await self._get(f"tracks/{track_id}")
        return self._parse_track(data)

    def _parse_track(self, data: dict) -> dict:
        images  = data.get("album", {}).get("images", [])
        image   = images[0]["url"] if images else None
        release = data.get("album", {}).get("release_date", "")
        year    = release[:4] if release else None
        return {
            "spotify_id":   data["id"],
            "name":         data["name"],
            "artist":       ", ".join(a["name"] for a in data.get("artists", [])),
            "artist_ids":   [a["id"] for a in data.get("artists", [])],
            "album":        data.get("album", {}).get("name"),
            "image":        image,
            "year":         year,
            "duration_ms":  data.get("duration_ms"),
            "popularity":   data.get("popularity"),
            "external_url": data.get("external_urls", {}).get("spotify"),
        }

    async def get_audio_features(self, track_id: str) -> Optional[dict]:
        """
        Fetch Spotify audio features. Returns None if endpoint is unavailable
        (deprecated for apps without extended quota — fall through to genre estimation).
        """
        try:
            data = await self._get(f"audio-features/{track_id}")
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (403, 404):
                return None  # Caller will use genre-based estimation
            raise

    async def get_artist_genres(self, artist_id: str) -> list:
        try:
            data = await self._get(f"artists/{artist_id}")
            return data.get("genres", [])
        except Exception:
            return []

    async def get_related_artists(self, artist_id: str) -> list:
        """
        Returns up to 20 related artists with their genre lists.
        Each item: {id, name, genres, popularity, image}
        """
        try:
            data = await self._get(f"artists/{artist_id}/related-artists")
            artists = []
            for a in data.get("artists", []):
                images = a.get("images", [])
                artists.append({
                    "id":         a["id"],
                    "name":       a["name"],
                    "genres":     a.get("genres", []),
                    "popularity": a.get("popularity", 0),
                    "image":      images[0]["url"] if images else None,
                })
            return artists
        except Exception:
            return []

    async def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> list:
        """Returns up to 10 top tracks for an artist. Each item is a raw Spotify track dict."""
        try:
            data = await self._get(f"artists/{artist_id}/top-tracks", params={"market": market})
            return data.get("tracks", [])
        except Exception:
            return []

    async def search_from_youtube(self, youtube_url: str) -> dict:
        oembed_url = f"https://www.youtube.com/oembed?url={youtube_url}&format=json"
        async with httpx.AsyncClient() as client:
            r = await client.get(oembed_url, timeout=10)
            if r.status_code != 200:
                raise ValueError("Could not fetch YouTube video info.")
            title = r.json().get("title", "")
        return await self.search_track(title)

    async def search_track(self, query: str) -> dict:
        data  = await self._get("search", params={"q": query, "type": "track", "limit": 1})
        items = data.get("tracks", {}).get("items", [])
        if not items:
            raise ValueError(f"No Spotify results for: {query}")
        return self._parse_track(items[0])
