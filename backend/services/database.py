import os
import json
from typing import Optional


class DatabaseService:
    """
    Stores analyzed song fingerprints in Supabase.
    Every song we process builds our proprietary dataset.
    """

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY")
        self._client = None

    def _get_client(self):
        if not self.url or not self.key:
            return None
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self.url, self.key)
            except Exception:
                return None
        return self._client

    async def upsert_fingerprint(self, fingerprint: dict, track_info: dict) -> Optional[dict]:
        """
        Store or update a song's fingerprint. This is the core of our
        growing dataset — every analyzed song goes here.
        """
        client = self._get_client()
        if not client:
            return None

        try:
            record = {
                "spotify_id": track_info.get("spotify_id"),
                "title": track_info.get("name"),
                "artist": track_info.get("artist"),
                "year": track_info.get("year"),
                "image_url": track_info.get("image"),
                "external_url": track_info.get("external_url"),
                "fingerprint_hash": fingerprint.get("hash"),
                "key": fingerprint.get("key"),
                "tempo": fingerprint.get("tempo"),
                "era": fingerprint.get("era"),
                "mode": fingerprint.get("mode"),
                "genres": fingerprint.get("genres", []),
                "instruments": fingerprint.get("instruments", []),
                "vocal_style": fingerprint.get("vocal_style"),
                "audio_features": fingerprint.get("audio_features", {}),
            }
            result = client.table("song_fingerprints").upsert(
                record,
                on_conflict="spotify_id"
            ).execute()
            return result.data
        except Exception as e:
            print(f"[DB] upsert failed: {e}")
            return None
