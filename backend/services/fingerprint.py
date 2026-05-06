import hashlib
import json
from typing import Optional


# Spotify key numbers → note names
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Era mapping based on release year
def get_era(year: Optional[str]) -> str:
    if not year:
        return "Unknown"
    try:
        y = int(year)
        if y < 1970: return "Pre-70s"
        if y < 1980: return "70s"
        if y < 1990: return "80s"
        if y < 2000: return "90s"
        if y < 2010: return "2000s"
        if y < 2015: return "Early 2010s"
        if y < 2020: return "Late 2010s"
        return "2020s"
    except ValueError:
        return "Unknown"


def infer_instruments(features: dict, genres: list) -> list:
    """
    Infer likely instruments from audio features + genres.
    This is a heuristic model — in a deeper version this would use
    actual ML spectral analysis.
    """
    instruments = []
    energy = features.get("energy", 0)
    acoustic = features.get("acousticness", 0)
    instrumental = features.get("instrumentalness", 0)
    dance = features.get("danceability", 0)
    speech = features.get("speechiness", 0)
    tempo = features.get("tempo", 0)
    valence = features.get("valence", 0)
    liveness = features.get("liveness", 0)

    genre_str = " ".join(genres).lower()

    # Drums / percussion
    if dance > 0.5 or energy > 0.5:
        instruments.append("Drums")
    if dance > 0.7 and tempo > 100:
        instruments.append("Hi-hats")

    # Bass
    if energy > 0.4 or dance > 0.5:
        instruments.append("Bass")

    # Guitar
    if acoustic > 0.4 or any(g in genre_str for g in ["rock", "folk", "country", "indie", "alternative"]):
        instruments.append("Acoustic Guitar")
    if energy > 0.6 and acoustic < 0.4 and any(g in genre_str for g in ["rock", "metal", "punk", "grunge"]):
        instruments.append("Electric Guitar")

    # Piano / keys
    if any(g in genre_str for g in ["pop", "soul", "r&b", "jazz", "classical", "blues"]):
        instruments.append("Piano/Keys")

    # Synth / electronic
    if any(g in genre_str for g in ["electronic", "edm", "house", "techno", "synth", "pop", "hip hop", "trap"]):
        instruments.append("Synthesizer")

    # Strings
    if any(g in genre_str for g in ["classical", "orchestral", "film", "cinematic", "ambient"]):
        instruments.append("Strings")

    # Vocals
    if speech < 0.33 and instrumental < 0.5:
        instruments.append("Lead Vocals")
    if speech > 0.33 and speech < 0.66:
        instruments.append("Rap/Spoken Word")
    if liveness > 0.6:
        instruments.append("Live Audience")

    # 808 / trap
    if any(g in genre_str for g in ["trap", "hip hop", "rap"]) and dance > 0.6:
        instruments.append("808 Bass")

    return list(dict.fromkeys(instruments))  # deduplicate, preserve order


def infer_vocal_style(features: dict, genres: list) -> str:
    """Heuristically classify vocal style."""
    speech = features.get("speechiness", 0)
    energy = features.get("energy", 0)
    instrumental = features.get("instrumentalness", 0)
    genre_str = " ".join(genres).lower()

    if instrumental > 0.8:
        return "Instrumental"
    if speech > 0.66:
        return "Rap / Spoken Word"
    if speech > 0.33:
        return "Melodic Rap"
    if energy > 0.8:
        return "Powerful / Belting"
    if any(g in genre_str for g in ["r&b", "soul"]):
        return "Soulful / R&B"
    if any(g in genre_str for g in ["jazz"]):
        return "Jazz Phrasing"
    if any(g in genre_str for g in ["classical", "opera"]):
        return "Operatic"
    if features.get("acousticness", 0) > 0.6:
        return "Intimate / Soft"
    return "Pop / Melodic"


def parse_timestamp(ts: str) -> Optional[int]:
    """Convert 'm:ss' or 'mm:ss' to total seconds."""
    if not ts:
        return None
    try:
        parts = ts.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        return None
    return None


def describe_timestamp(ts_seconds: int, features: dict, song_name: str) -> dict:
    """Generate a human-readable description of a pinned moment."""
    energy = features.get("energy", 0)
    dance = features.get("danceability", 0)
    valence = features.get("valence", 0)

    minutes = ts_seconds // 60
    seconds = ts_seconds % 60
    time_str = f"{minutes}:{seconds:02d}"

    # Guess what's likely happening at this point in the song
    duration_ms = features.get("duration_ms", 240000)
    duration_s = duration_ms / 1000
    position_ratio = ts_seconds / duration_s if duration_s > 0 else 0.5

    if position_ratio < 0.15:
        section = "intro"
    elif position_ratio < 0.35:
        section = "first verse / pre-chorus"
    elif position_ratio < 0.55:
        section = "chorus / hook"
    elif position_ratio < 0.75:
        section = "bridge / second chorus"
    else:
        section = "outro"

    energy_desc = "high energy" if energy > 0.7 else ("moderate energy" if energy > 0.4 else "low energy")
    mood_desc = "uplifting" if valence > 0.6 else ("melancholic" if valence < 0.35 else "neutral")

    return {
        "time": time_str,
        "description": f"Pinned at {time_str} — likely the {section} section. "
                       f"This moment has {energy_desc} with a {mood_desc} emotional tone. "
                       f"The fingerprint weighs ingredients from this part of the track more heavily.",
    }


class FingerprintService:
    """Builds the musical DNA fingerprint for a track."""

    def build(self, track_info: dict, audio_features: dict, timestamp: Optional[str]) -> dict:
        genres = track_info.get("_genres", [])
        year = track_info.get("year")
        key_num = audio_features.get("key", -1)
        mode_num = audio_features.get("mode", 1)  # 1 = major, 0 = minor
        tempo = audio_features.get("tempo", 0)

        key_name = KEY_NAMES[key_num] if 0 <= key_num <= 11 else "Unknown"
        mode_name = "Major" if mode_num == 1 else "Minor"

        instruments = infer_instruments(audio_features, genres)
        vocal_style = infer_vocal_style(audio_features, genres)

        # Normalize tempo to 0–1 for radar (120 BPM = 0.5, max ~200)
        tempo_norm = min(tempo / 200, 1.0)

        # Build the fingerprint dict
        fp = {
            "spotify_id": track_info.get("spotify_id"),
            "key": f"{key_name} {mode_name}",
            "tempo": round(tempo, 1),
            "era": get_era(year),
            "mode": mode_name,
            "genres": genres[:6],
            "instruments": instruments,
            "vocal_style": vocal_style,
            "audio_features": {
                "energy": round(audio_features.get("energy", 0), 3),
                "danceability": round(audio_features.get("danceability", 0), 3),
                "valence": round(audio_features.get("valence", 0), 3),
                "acousticness": round(audio_features.get("acousticness", 0), 3),
                "instrumentalness": round(audio_features.get("instrumentalness", 0), 3),
                "speechiness": round(audio_features.get("speechiness", 0), 3),
                "liveness": round(audio_features.get("liveness", 0), 3),
                "tempo_norm": round(tempo_norm, 3),
            },
        }

        # Timestamp highlight
        if timestamp:
            ts_seconds = parse_timestamp(timestamp)
            if ts_seconds is not None:
                fp["timestamp_highlight"] = describe_timestamp(
                    ts_seconds, audio_features, track_info.get("name", "")
                )

        # Generate a deterministic hash for this fingerprint
        fp_str = json.dumps({
            "id": track_info.get("spotify_id"),
            "ts": timestamp or "none",
        }, sort_keys=True)
        fp["hash"] = hashlib.sha256(fp_str.encode()).hexdigest()

        return fp
