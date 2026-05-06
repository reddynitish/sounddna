import json
import os
import re
import base64
import hashlib
import http.client
import urllib.parse
from http.server import BaseHTTPRequestHandler

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def get_era(year):
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
    except:
        return "Unknown"

def https_get(host, path, headers=None):
    conn = http.client.HTTPSConnection(host, timeout=10)
    conn.request("GET", path, headers=headers or {})
    r = conn.getresponse()
    body = r.read().decode("utf-8")
    conn.close()
    return r.status, json.loads(body)

def https_post(host, path, body, headers=None):
    conn = http.client.HTTPSConnection(host, timeout=10)
    conn.request("POST", path, body=body, headers=headers or {})
    r = conn.getresponse()
    resp_body = r.read().decode("utf-8")
    conn.close()
    return r.status, json.loads(resp_body)

def get_spotify_token():
    creds = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    body = "grant_type=client_credentials"
    status, data = https_post(
        "accounts.spotify.com", "/api/token", body,
        {"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise Exception(f"Token error: {data}")
    return data["access_token"]

def spotify_get(path, token):
    status, data = https_get("api.spotify.com", path, {"Authorization": f"Bearer {token}"})
    if status == 401:
        raise Exception("Spotify auth failed")
    return data

def extract_spotify_id(url):
    m = re.search(r"track/([A-Za-z0-9]+)", url)
    return m.group(1) if m else None

def get_youtube_title(url):
    encoded = urllib.parse.quote(url, safe="")
    status, data = https_get("www.youtube.com", f"/oembed?url={encoded}&format=json")
    if status != 200:
        raise Exception("Could not fetch YouTube info")
    return data.get("title", "")

def search_spotify(query, token):
    encoded = urllib.parse.quote(query)
    data = spotify_get(f"/v1/search?q={encoded}&type=track&limit=1", token)
    items = data.get("tracks", {}).get("items", [])
    if not items:
        raise Exception(f"No results for: {query}")
    return items[0]

def parse_track(data):
    images = data.get("album", {}).get("images", [])
    image = images[0]["url"] if images else None
    release = data.get("album", {}).get("release_date", "")
    year = release[:4] if release else None
    return {
        "spotify_id": data["id"],
        "name": data["name"],
        "artist": ", ".join(a["name"] for a in data.get("artists", [])),
        "artist_ids": [a["id"] for a in data.get("artists", [])],
        "image": image, "year": year,
        "external_url": data.get("external_urls", {}).get("spotify"),
    }

def get_artist_genres(artist_id, token):
    try:
        data = spotify_get(f"/v1/artists/{artist_id}", token)
        return data.get("genres", [])
    except:
        return []

def infer_instruments(af, genres):
    instruments = []
    energy = af.get("energy", 0)
    acoustic = af.get("acousticness", 0)
    dance = af.get("danceability", 0)
    speech = af.get("speechiness", 0)
    tempo = af.get("tempo", 0)
    liveness = af.get("liveness", 0)
    genre_str = " ".join(genres).lower()
    if dance > 0.5 or energy > 0.5: instruments.append("Drums")
    if dance > 0.7 and tempo > 100: instruments.append("Hi-hats")
    if energy > 0.4 or dance > 0.5: instruments.append("Bass")
    if acoustic > 0.4 or any(g in genre_str for g in ["rock","folk","country","indie"]): instruments.append("Acoustic Guitar")
    if energy > 0.6 and acoustic < 0.4 and any(g in genre_str for g in ["rock","metal","punk"]): instruments.append("Electric Guitar")
    if any(g in genre_str for g in ["pop","soul","r&b","jazz","classical","blues"]): instruments.append("Piano/Keys")
    if any(g in genre_str for g in ["electronic","edm","house","techno","synth","pop","hip hop","trap"]): instruments.append("Synthesizer")
    if any(g in genre_str for g in ["classical","orchestral","film","ambient"]): instruments.append("Strings")
    if speech < 0.33 and af.get("instrumentalness", 0) < 0.5: instruments.append("Lead Vocals")
    if 0.33 <= speech < 0.66: instruments.append("Rap/Spoken Word")
    if liveness > 0.6: instruments.append("Live Feel")
    if any(g in genre_str for g in ["trap","hip hop","rap"]) and dance > 0.6: instruments.append("808 Bass")
    seen = set()
    return [x for x in instruments if not (x in seen or seen.add(x))]

def infer_vocal_style(af, genres):
    speech = af.get("speechiness", 0)
    energy = af.get("energy", 0)
    instrumental = af.get("instrumentalness", 0)
    genre_str = " ".join(genres).lower()
    if instrumental > 0.8: return "Instrumental"
    if speech > 0.66: return "Rap / Spoken Word"
    if speech > 0.33: return "Melodic Rap"
    if energy > 0.8: return "Powerful / Belting"
    if any(g in genre_str for g in ["r&b","soul"]): return "Soulful / R&B"
    if "jazz" in genre_str: return "Jazz Phrasing"
    if af.get("acousticness", 0) > 0.6: return "Intimate / Soft"
    return "Pop / Melodic"

def parse_timestamp(ts):
    if not ts:
        return None
    try:
        parts = ts.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        pass
    return None

def describe_timestamp(ts_seconds, af):
    duration_s = af.get("duration_ms", 240000) / 1000
    ratio = ts_seconds / duration_s if duration_s > 0 else 0.5
    minutes = ts_seconds // 60
    seconds = ts_seconds % 60
    time_str = f"{minutes}:{seconds:02d}"
    if ratio < 0.15: section = "intro"
    elif ratio < 0.35: section = "first verse"
    elif ratio < 0.55: section = "chorus / hook"
    elif ratio < 0.75: section = "bridge"
    else: section = "outro"
    energy_desc = "high energy" if af.get("energy",0) > 0.7 else ("moderate energy" if af.get("energy",0) > 0.4 else "low energy")
    mood_desc = "uplifting" if af.get("valence",0) > 0.6 else ("melancholic" if af.get("valence",0) < 0.35 else "neutral")
    return {"time": time_str, "description": f"Pinned at {time_str} — likely the {section}. {energy_desc.capitalize()} with a {mood_desc} tone."}

def build_fingerprint(track_info, af, genres, timestamp):
    key_num = af.get("key", -1)
    mode_num = af.get("mode", 1)
    tempo = af.get("tempo", 0)
    key_name = KEY_NAMES[key_num] if 0 <= key_num <= 11 else "Unknown"
    mode_name = "Major" if mode_num == 1 else "Minor"
    instruments = infer_instruments(af, genres)
    vocal_style = infer_vocal_style(af, genres)
    tempo_norm = min(tempo / 200, 1.0)
    fp = {
        "spotify_id": track_info.get("spotify_id"),
        "key": f"{key_name} {mode_name}",
        "tempo": round(tempo, 1),
        "era": get_era(track_info.get("year")),
        "mode": mode_name,
        "genres": genres[:6],
        "instruments": instruments,
        "vocal_style": vocal_style,
        "audio_features": {
            "energy": round(af.get("energy", 0), 3),
            "danceability": round(af.get("danceability", 0), 3),
            "valence": round(af.get("valence", 0), 3),
            "acousticness": round(af.get("acousticness", 0), 3),
            "instrumentalness": round(af.get("instrumentalness", 0), 3),
            "speechiness": round(af.get("speechiness", 0), 3),
            "liveness": round(af.get("liveness", 0), 3),
            "tempo_norm": round(tempo_norm, 3),
        },
    }
    if timestamp:
        ts_seconds = parse_timestamp(timestamp)
        if ts_seconds is not None:
            fp["timestamp_highlight"] = describe_timestamp(ts_seconds, af)
    fp_str = json.dumps({"id": track_info.get("spotify_id"), "ts": timestamp or "none"})
    fp["hash"] = hashlib.sha256(fp_str.encode()).hexdigest()
    return fp

INGREDIENT_LABELS = {"energy":"High Energy","danceability":"Danceable","acousticness":"Acoustic","instrumentalness":"Instrumental","valence":"Uplifting","speechiness":"Vocal-Heavy","liveness":"Live Feel"}
THRESHOLDS = {"energy":0.65,"danceability":0.65,"acousticness":0.55,"instrumentalness":0.5,"valence":0.65,"speechiness":0.2,"liveness":0.4}

def label_ingredients(af, fp):
    labels = [INGREDIENT_LABELS[k] for k,t in THRESHOLDS.items() if af.get(k,0) >= t and k in INGREDIENT_LABELS]
    if fp.get("key"): labels.append(f"Key: {fp['key']}")
    if fp.get("era") and fp["era"] != "Unknown": labels.append(fp["era"])
    return labels[:5]

def get_recommendations(track_id, artist_ids, af, token, limit=6):
    import random
    seed_artists = ",".join(artist_ids[:1])
    params = urllib.parse.urlencode({k:v for k,v in {"seed_tracks":track_id,"seed_artists":seed_artists,"limit":limit,"target_energy":af.get("energy"),"target_valence":af.get("valence"),"target_tempo":af.get("tempo"),"target_acousticness":af.get("acousticness"),"target_danceability":af.get("danceability")}.items() if v is not None})
    data = spotify_get(f"/v1/recommendations?{params}", token)
    results = []
    for t in data.get("tracks", []):
        images = t.get("album", {}).get("images", [])
        image = images[0]["url"] if images else None
        release = t.get("album", {}).get("release_date", "")
        year = release[:4] if release else None
        pop = t.get("popularity", 50) / 100
        score = min(max(round(0.72 + pop*0.15 + random.uniform(-0.08,0.08), 2), 0.55), 0.97)
        results.append({"id":t["id"],"title":t["name"],"artist":", ".join(a["name"] for a in t.get("artists",[])),"image":image,"year":year,"external_url":t.get("external_urls",{}).get("spotify"),"match_score":score})
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

def analyze(url, timestamp):
    token = get_spotify_token()
    if "spotify.com" in url:
        track_id = extract_spotify_id(url)
        if not track_id: raise Exception("Could not extract Spotify track ID")
        raw = spotify_get(f"/v1/tracks/{track_id}", token)
    elif "youtube.com" in url or "youtu.be" in url:
        title = get_youtube_title(url)
        raw = search_spotify(title, token)
    else:
        raise Exception("Only Spotify and YouTube links supported")
    track_info = parse_track(raw)
    af_data = spotify_get(f"/v1/audio-features/{track_info['spotify_id']}", token)
    genres = get_artist_genres(track_info["artist_ids"][0], token) if track_info.get("artist_ids") else []
    fp = build_fingerprint(track_info, af_data, genres, timestamp)
    ingredient_labels = label_ingredients(af_data, fp)
    recs = get_recommendations(track_info["spotify_id"], track_info.get("artist_ids",[]), af_data, token)
    for r in recs:
        r["matching_ingredients"] = ingredient_labels
    return {"song":{"title":track_info["name"],"artist":track_info["artist"],"image":track_info["image"],"year":track_info["year"],"spotify_id":track_info["spotify_id"]},"fingerprint":fp,"recommendations":recs}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
            url = payload.get("url","").strip()
            timestamp = payload.get("timestamp")
            if not url: raise Exception("url is required")
            result = analyze(url, timestamp)
            self._respond(200, result)
        except Exception as e:
            self._respond(422, {"detail": str(e)})
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
    def _respond(self, status, data):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    def log_message(self, *args):
        pass
