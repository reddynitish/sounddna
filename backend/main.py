from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from services.spotify import SpotifyService
from services.fingerprint import FingerprintService
from services.recommender import RecommenderService
from services.database import DatabaseService
from services.deezer import DeezerService

load_dotenv()

app = FastAPI(title="SoundDNA API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spotify       = SpotifyService()
fingerprinter = FingerprintService()
recommender   = RecommenderService()
db            = DatabaseService()
deezer        = DeezerService()


class AnalyzeRequest(BaseModel):
    url:       str
    timestamp: Optional[str] = None


@app.get("/")
def root():
    return {"status": "SoundDNA API v2 running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    url       = req.url.strip()
    timestamp = req.timestamp

    # 1. Resolve track from Spotify/YouTube
    try:
        if "spotify.com" in url:
            track_info = await spotify.get_track_info(url)
        elif "youtube.com" in url or "youtu.be" in url:
            track_info = await spotify.search_from_youtube(url)
        else:
            raise HTTPException(status_code=400, detail="Only Spotify and YouTube links are supported.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not identify track: {str(e)}")

    # 2. Get genres — try Spotify first, fall back to Deezer album lookup
    #    (Spotify artist genres often blocked or empty; Deezer album genres are reliable)
    genres = []

    # 2a. Spotify artist genres
    if track_info.get("artist_ids"):
        try:
            spotify_genres = await spotify.get_artist_genres(track_info["artist_ids"][0])
            genres = spotify_genres
        except Exception:
            pass

    # 2b. If Spotify gave nothing, try Deezer album genres
    if not genres:
        try:
            artist_first = track_info["artist"].split(",")[0].strip()
            dz_info = await deezer.find_track(track_info["name"], artist_first)
            if dz_info:
                dz_genres = await deezer.get_album_genres(dz_info["album_id"])
                genres = dz_genres
                # Stash deezer artist id so recommender can reuse it
                track_info["_deezer_artist_id"] = dz_info["artist_id"]
        except Exception:
            pass

    track_info["_genres"] = genres

    # 3. Spotify audio features — returns None if deprecated for this app
    audio_features = await spotify.get_audio_features(track_info["spotify_id"])

    # 4. Build fingerprint (uses genre estimation if audio_features is None)
    fingerprint = fingerprinter.build(track_info, audio_features, timestamp)

    # 5. Store in DB (fire and forget)
    try:
        await db.upsert_fingerprint(fingerprint, track_info)
    except Exception:
        pass

    # 6. Get recommendations via Deezer music graph + Spotify cross-reference
    recommendations = await recommender.find_similar(
        fingerprint=fingerprint,
        track_info=track_info,
        spotify=spotify,
    )

    return {
        "song": {
            "title":      track_info.get("name"),
            "artist":     track_info.get("artist"),
            "image":      track_info.get("image"),
            "year":       track_info.get("year"),
            "spotify_id": track_info.get("spotify_id"),
        },
        "fingerprint":     fingerprint,
        "recommendations": recommendations,
    }
