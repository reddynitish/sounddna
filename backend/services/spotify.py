import os
import re
import httpx
import base64
from typing import Optional


class SpotifyService:
    """Handles all Spotify API interactions."""

    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        """Fetch or return cached client credentials token."""
        if self._token:
            return self._token
        creds = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
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
                # Token expired — refresh once
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
        """Pull track ID from Spotify URL."""
        match = re.search(r"track/([A-Za-z0-9]+)", url)
        if not match:
            raise ValueError("Could not extract Spotify track ID from URL.")
        return match.group(1)

    async def get_track_info(self, spotify_url: str) -> dict:
        """Fetch full track metadata from Spotify track URL."""
        track_id = self._extract_spotify_id(spotify_url)
        data = await self._get(f"tracks/{track_id}")
        return self._parse_track(data)

    async def get_track_by_id(self, track_id: str) -> dict:
        data = await self._get(f"tracks/{track_id}")
        return self._parse_track(data)

    def _parse_track(self, data: dict) -> dict:
        images = data.get("album", {}).get("images", [])
        image = images[0]["url"] if images else None
        release = data.get("album", {}).get("release_date", "")
        year = release[:4] if release else None
        return {
            "spotify_id": data["id"],
            "name": data["name"],
            "artist": ", ".join(a["name"] for a in data.get("artists", [])),
            "artist_ids": [a["id"] for a in data.get("artists", [])],
            "album": data.get("album", {}).get("name"),
            "image": image,
            "year": year,
            "duration_ms": data.get("duration_ms"),
            "popularity": data.get("popularity"),
            "external_url": data.get("external_urls", {}).get("spotify"),
        }

    async def get_audio_features(self, track_id: str) -> dict:
        """Fetch Spotify audio features (tempo, energy, key, etc.)."""
        data = await self._get(f"audio-features/{track_id}")
        return data

    async def search_from_youtube(self, youtube_url: str) -> dict:
        """
        Try to identify the song from a YouTube URL by extracting
        the video title via oEmbed, then searching Spotify.
        """
        # Get video title from YouTube oEmbed
        oembed_url = f"https://www.youtube.com/oembed?url={youtube_url}&format=json"
        async with httpx.AsyncClient() as client:
            r = await client.get(oembed_url, timeout=10)
            if r.status_code != 200:
                raise ValueError("Could not fetch YouTube video info.")
            title = r.json().get("title", "")

        # Search Spotify for that title
        return await self.search_track(title)

    async def search_track(self, query: str) -> dict:
        data = await self._get("search", params={"q": query, "type": "track", "limit": 1})
        items = data.get("tracks", {}).get("items", [])
        if not items:
            raise ValueError(f"No Spotify results for: {query}")
        return self._parse_track(items[0])

    async def get_recommendations(
        self,
        seed_track_id: str,
        seed_artist_ids: list,
        target_features: dict,
        limit: int = 8,
    ) -> list:
        """Get Spotify recommendations seeded by track + audio targets."""
        params = {
            "seed_tracks": seed_track_id,
            "seed_artists": ",".join(seed_artist_ids[:1]),  # max 5 seeds total
            "limit": limit,
            "target_energy": target_features.get("energy"),
            "target_valence": target_features.get("valence"),
            "target_tempo": target_features.get("tempo"),
            "target_acousticness": target_features.get("acousticness"),
            "target_instrumentalness": target_features.get("instrumentalness"),
            "target_danceability": target_features.get("danceability"),
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        data = await self._get("recommendations", params=params)
        return data.get("tracks", [])

    async def get_artist_genres(self, artist_id: str) -> list:
        """Get genres associated with an artist."""
        try:
            data = await self._get(f"artists/{artist_id}")
            return data.get("genres", [])
        except Exception:
            return []
