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

load_dotenv()

app = FastAPI(title="SoundDNA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spotify = SpotifyService()
fingerprinter = FingerprintService()
recommender = RecommenderService()
db = DatabaseService()


class AnalyzeRequest(BaseModel):
    url: str
    timestamp: Optional[str] = None  # e.g. "1:20"


@app.get("/")
def root():
    return {"status": "SoundDNA API running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    """
    Main endpoint: takes a Spotify/YouTube URL + optional timestamp,
    returns fingerprint + recommendations.
    """
    url = req.url.strip()
    timestamp = req.timestamp

    # 1. Resolve track info from the URL
    try:
        if "spotify.com" in url:
            track_info = await spotify.get_track_info(url)
        elif "youtube.com" in url or "youtu.be" in url:
            track_info = await spotify.search_from_youtube(url)
        else:
            raise HTTPException(status_code=400, detail="Only Spotify and YouTube links are supported.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not identify track: {str(e)}")

    # 2. Get audio features from Spotify
    try:
        audio_features = await spotify.get_audio_features(track_info["spotify_id"])
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not fetch audio features: {str(e)}")

    # 3. Build fingerprint
    fingerprint = fingerprinter.build(track_info, audio_features, timestamp)

    # 4. Store in DB (fire and forget — builds our dataset over time)
    try:
        await db.upsert_fingerprint(fingerprint, track_info)
    except Exception:
        pass  # Never block on DB write

    # 5. Get recommendations
    recommendations = await recommender.find_similar(
        fingerprint=fingerprint,
        track_info=track_info,
        spotify=spotify,
    )

    return {
        "song": {
            "title": track_info.get("name"),
            "artist": track_info.get("artist"),
            "image": track_info.get("image"),
            "year": track_info.get("year"),
            "spotify_id": track_info.get("spotify_id"),
        },
        "fingerprint": fingerprint,
        "recommendations": recommendations,
    }
