import hashlib
import json
from typing import Optional


KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Language detection from genre signals
LANGUAGE_GENRE_SIGNALS = [
    ("Korean",     ["k-pop", "korean", "k-indie", "k-r&b", "k-hip hop", "trot"]),
    ("Spanish",    ["latin", "reggaeton", "latin pop", "bachata", "salsa", "cumbia", "trap latino", "urbano", "corrido", "banda", "ranchera"]),
    ("Japanese",   ["j-pop", "j-rock", "japanese", "city pop", "j-indie", "enka", "shibuya-kei", "anime"]),
    ("Portuguese", ["sertanejo", "forro", "pagode", "mpb", "bossa nova", "funk carioca", "baile funk", "axe"]),
    ("French",     ["french pop", "chanson", "variété"]),
    ("Hindi",      ["bollywood", "filmi", "desi pop", "hindi pop"]),
    ("Mandarin",   ["mandopop", "c-pop", "cantopop", "taiwanese pop"]),
    ("Arabic",     ["arabic", "khaleeji", "shaabi", "rai"]),
    ("Afro",       ["afrobeats", "afropop", "amapiano", "highlife", "afro pop"]),
]

# Comprehensive genre → audio feature profiles
# Each entry: {energy, danceability, valence, acousticness, instrumentalness, speechiness, liveness, tempo}
GENRE_PROFILES = {
    # Electronic
    "edm":              {"energy": 0.90, "danceability": 0.85, "valence": 0.65, "acousticness": 0.03, "instrumentalness": 0.70, "speechiness": 0.05, "liveness": 0.14, "tempo": 128},
    "house":            {"energy": 0.82, "danceability": 0.88, "valence": 0.70, "acousticness": 0.03, "instrumentalness": 0.85, "speechiness": 0.04, "liveness": 0.12, "tempo": 124},
    "deep house":       {"energy": 0.70, "danceability": 0.86, "valence": 0.62, "acousticness": 0.05, "instrumentalness": 0.88, "speechiness": 0.04, "liveness": 0.10, "tempo": 120},
    "tech house":       {"energy": 0.82, "danceability": 0.87, "valence": 0.55, "acousticness": 0.03, "instrumentalness": 0.90, "speechiness": 0.04, "liveness": 0.10, "tempo": 128},
    "techno":           {"energy": 0.92, "danceability": 0.82, "valence": 0.38, "acousticness": 0.02, "instrumentalness": 0.95, "speechiness": 0.04, "liveness": 0.10, "tempo": 135},
    "trance":           {"energy": 0.88, "danceability": 0.78, "valence": 0.58, "acousticness": 0.02, "instrumentalness": 0.90, "speechiness": 0.04, "liveness": 0.10, "tempo": 138},
    "dubstep":          {"energy": 0.93, "danceability": 0.70, "valence": 0.42, "acousticness": 0.02, "instrumentalness": 0.80, "speechiness": 0.05, "liveness": 0.10, "tempo": 140},
    "drum and bass":    {"energy": 0.92, "danceability": 0.78, "valence": 0.50, "acousticness": 0.02, "instrumentalness": 0.85, "speechiness": 0.04, "liveness": 0.10, "tempo": 174},
    "dnb":              {"energy": 0.92, "danceability": 0.78, "valence": 0.50, "acousticness": 0.02, "instrumentalness": 0.85, "speechiness": 0.04, "liveness": 0.10, "tempo": 174},
    "ambient":          {"energy": 0.20, "danceability": 0.28, "valence": 0.42, "acousticness": 0.72, "instrumentalness": 0.92, "speechiness": 0.03, "liveness": 0.08, "tempo": 85},
    "synthwave":        {"energy": 0.72, "danceability": 0.72, "valence": 0.60, "acousticness": 0.05, "instrumentalness": 0.60, "speechiness": 0.04, "liveness": 0.10, "tempo": 112},
    "electronic":       {"energy": 0.78, "danceability": 0.78, "valence": 0.58, "acousticness": 0.05, "instrumentalness": 0.65, "speechiness": 0.05, "liveness": 0.10, "tempo": 120},
    "lo-fi":            {"energy": 0.32, "danceability": 0.65, "valence": 0.50, "acousticness": 0.55, "instrumentalness": 0.70, "speechiness": 0.04, "liveness": 0.10, "tempo": 85},
    "chillout":         {"energy": 0.38, "danceability": 0.60, "valence": 0.55, "acousticness": 0.40, "instrumentalness": 0.65, "speechiness": 0.04, "liveness": 0.10, "tempo": 90},

    # Hip-hop / Rap
    "hip hop":          {"energy": 0.68, "danceability": 0.80, "valence": 0.52, "acousticness": 0.15, "instrumentalness": 0.08, "speechiness": 0.22, "liveness": 0.14, "tempo": 92},
    "rap":              {"energy": 0.72, "danceability": 0.78, "valence": 0.48, "acousticness": 0.10, "instrumentalness": 0.05, "speechiness": 0.28, "liveness": 0.14, "tempo": 95},
    "trap":             {"energy": 0.72, "danceability": 0.80, "valence": 0.40, "acousticness": 0.05, "instrumentalness": 0.10, "speechiness": 0.20, "liveness": 0.12, "tempo": 140},
    "drill":            {"energy": 0.78, "danceability": 0.75, "valence": 0.30, "acousticness": 0.03, "instrumentalness": 0.08, "speechiness": 0.25, "liveness": 0.12, "tempo": 145},
    "cloud rap":        {"energy": 0.50, "danceability": 0.72, "valence": 0.38, "acousticness": 0.08, "instrumentalness": 0.10, "speechiness": 0.22, "liveness": 0.10, "tempo": 82},
    "boom bap":         {"energy": 0.65, "danceability": 0.78, "valence": 0.45, "acousticness": 0.22, "instrumentalness": 0.10, "speechiness": 0.30, "liveness": 0.15, "tempo": 90},
    "gangsta rap":      {"energy": 0.75, "danceability": 0.78, "valence": 0.42, "acousticness": 0.08, "instrumentalness": 0.08, "speechiness": 0.28, "liveness": 0.14, "tempo": 95},

    # Rock
    "rock":             {"energy": 0.78, "danceability": 0.55, "valence": 0.55, "acousticness": 0.12, "instrumentalness": 0.15, "speechiness": 0.06, "liveness": 0.20, "tempo": 120},
    "indie rock":       {"energy": 0.70, "danceability": 0.55, "valence": 0.55, "acousticness": 0.22, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.18, "tempo": 115},
    "alternative rock": {"energy": 0.72, "danceability": 0.52, "valence": 0.48, "acousticness": 0.18, "instrumentalness": 0.18, "speechiness": 0.05, "liveness": 0.18, "tempo": 118},
    "alternative":      {"energy": 0.72, "danceability": 0.52, "valence": 0.48, "acousticness": 0.18, "instrumentalness": 0.18, "speechiness": 0.05, "liveness": 0.18, "tempo": 118},
    "metal":            {"energy": 0.95, "danceability": 0.42, "valence": 0.30, "acousticness": 0.02, "instrumentalness": 0.40, "speechiness": 0.07, "liveness": 0.22, "tempo": 155},
    "heavy metal":      {"energy": 0.96, "danceability": 0.40, "valence": 0.28, "acousticness": 0.02, "instrumentalness": 0.45, "speechiness": 0.07, "liveness": 0.22, "tempo": 158},
    "punk":             {"energy": 0.90, "danceability": 0.52, "valence": 0.60, "acousticness": 0.05, "instrumentalness": 0.10, "speechiness": 0.08, "liveness": 0.25, "tempo": 160},
    "post-punk":        {"energy": 0.78, "danceability": 0.55, "valence": 0.40, "acousticness": 0.10, "instrumentalness": 0.20, "speechiness": 0.06, "liveness": 0.18, "tempo": 125},
    "grunge":           {"energy": 0.85, "danceability": 0.45, "valence": 0.35, "acousticness": 0.12, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.22, "tempo": 110},
    "classic rock":     {"energy": 0.75, "danceability": 0.55, "valence": 0.60, "acousticness": 0.15, "instrumentalness": 0.25, "speechiness": 0.05, "liveness": 0.25, "tempo": 120},
    "hard rock":        {"energy": 0.88, "danceability": 0.50, "valence": 0.50, "acousticness": 0.05, "instrumentalness": 0.25, "speechiness": 0.06, "liveness": 0.22, "tempo": 135},
    "shoegaze":         {"energy": 0.72, "danceability": 0.45, "valence": 0.38, "acousticness": 0.15, "instrumentalness": 0.55, "speechiness": 0.04, "liveness": 0.12, "tempo": 112},
    "psychedelic":      {"energy": 0.65, "danceability": 0.52, "valence": 0.55, "acousticness": 0.30, "instrumentalness": 0.50, "speechiness": 0.04, "liveness": 0.22, "tempo": 105},

    # Pop
    "pop":              {"energy": 0.68, "danceability": 0.72, "valence": 0.62, "acousticness": 0.20, "instrumentalness": 0.04, "speechiness": 0.06, "liveness": 0.14, "tempo": 118},
    "dance pop":        {"energy": 0.78, "danceability": 0.82, "valence": 0.68, "acousticness": 0.08, "instrumentalness": 0.05, "speechiness": 0.06, "liveness": 0.12, "tempo": 125},
    "electropop":       {"energy": 0.75, "danceability": 0.80, "valence": 0.62, "acousticness": 0.05, "instrumentalness": 0.25, "speechiness": 0.06, "liveness": 0.10, "tempo": 122},
    "indie pop":        {"energy": 0.62, "danceability": 0.65, "valence": 0.65, "acousticness": 0.30, "instrumentalness": 0.15, "speechiness": 0.05, "liveness": 0.15, "tempo": 112},
    "synth-pop":        {"energy": 0.72, "danceability": 0.78, "valence": 0.60, "acousticness": 0.05, "instrumentalness": 0.30, "speechiness": 0.05, "liveness": 0.10, "tempo": 122},
    "teen pop":         {"energy": 0.72, "danceability": 0.78, "valence": 0.72, "acousticness": 0.12, "instrumentalness": 0.05, "speechiness": 0.07, "liveness": 0.12, "tempo": 122},
    "art pop":          {"energy": 0.60, "danceability": 0.65, "valence": 0.52, "acousticness": 0.25, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.12, "tempo": 108},
    "k-pop":            {"energy": 0.78, "danceability": 0.82, "valence": 0.68, "acousticness": 0.08, "instrumentalness": 0.08, "speechiness": 0.10, "liveness": 0.10, "tempo": 130},
    "k-indie":          {"energy": 0.60, "danceability": 0.65, "valence": 0.60, "acousticness": 0.30, "instrumentalness": 0.18, "speechiness": 0.05, "liveness": 0.14, "tempo": 112},
    "j-pop":            {"energy": 0.72, "danceability": 0.75, "valence": 0.70, "acousticness": 0.15, "instrumentalness": 0.10, "speechiness": 0.06, "liveness": 0.12, "tempo": 128},
    "j-rock":           {"energy": 0.80, "danceability": 0.60, "valence": 0.58, "acousticness": 0.10, "instrumentalness": 0.20, "speechiness": 0.06, "liveness": 0.18, "tempo": 125},
    "city pop":         {"energy": 0.60, "danceability": 0.72, "valence": 0.68, "acousticness": 0.25, "instrumentalness": 0.25, "speechiness": 0.05, "liveness": 0.14, "tempo": 108},
    "mandopop":         {"energy": 0.65, "danceability": 0.72, "valence": 0.65, "acousticness": 0.22, "instrumentalness": 0.10, "speechiness": 0.06, "liveness": 0.14, "tempo": 118},
    "c-pop":            {"energy": 0.68, "danceability": 0.74, "valence": 0.67, "acousticness": 0.18, "instrumentalness": 0.09, "speechiness": 0.07, "liveness": 0.13, "tempo": 120},
    "cantopop":         {"energy": 0.65, "danceability": 0.72, "valence": 0.65, "acousticness": 0.22, "instrumentalness": 0.10, "speechiness": 0.06, "liveness": 0.14, "tempo": 118},

    # R&B / Soul
    "r&b":              {"energy": 0.62, "danceability": 0.75, "valence": 0.58, "acousticness": 0.25, "instrumentalness": 0.05, "speechiness": 0.08, "liveness": 0.14, "tempo": 95},
    "soul":             {"energy": 0.60, "danceability": 0.68, "valence": 0.65, "acousticness": 0.35, "instrumentalness": 0.08, "speechiness": 0.06, "liveness": 0.20, "tempo": 92},
    "neo soul":         {"energy": 0.55, "danceability": 0.70, "valence": 0.58, "acousticness": 0.40, "instrumentalness": 0.12, "speechiness": 0.07, "liveness": 0.18, "tempo": 88},
    "funk":             {"energy": 0.78, "danceability": 0.88, "valence": 0.78, "acousticness": 0.15, "instrumentalness": 0.25, "speechiness": 0.06, "liveness": 0.22, "tempo": 108},
    "motown":           {"energy": 0.68, "danceability": 0.78, "valence": 0.78, "acousticness": 0.30, "instrumentalness": 0.10, "speechiness": 0.06, "liveness": 0.20, "tempo": 118},

    # Jazz / Classical / Blues
    "jazz":             {"energy": 0.45, "danceability": 0.60, "valence": 0.62, "acousticness": 0.75, "instrumentalness": 0.60, "speechiness": 0.04, "liveness": 0.25, "tempo": 120},
    "smooth jazz":      {"energy": 0.38, "danceability": 0.60, "valence": 0.65, "acousticness": 0.72, "instrumentalness": 0.75, "speechiness": 0.04, "liveness": 0.15, "tempo": 100},
    "bebop":            {"energy": 0.55, "danceability": 0.55, "valence": 0.55, "acousticness": 0.80, "instrumentalness": 0.85, "speechiness": 0.04, "liveness": 0.30, "tempo": 200},
    "classical":        {"energy": 0.28, "danceability": 0.32, "valence": 0.42, "acousticness": 0.95, "instrumentalness": 0.96, "speechiness": 0.03, "liveness": 0.12, "tempo": 100},
    "blues":            {"energy": 0.55, "danceability": 0.55, "valence": 0.45, "acousticness": 0.55, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.25, "tempo": 90},

    # Country / Folk
    "country":          {"energy": 0.65, "danceability": 0.62, "valence": 0.65, "acousticness": 0.50, "instrumentalness": 0.10, "speechiness": 0.05, "liveness": 0.20, "tempo": 110},
    "folk":             {"energy": 0.45, "danceability": 0.52, "valence": 0.60, "acousticness": 0.72, "instrumentalness": 0.15, "speechiness": 0.05, "liveness": 0.18, "tempo": 100},
    "folk rock":        {"energy": 0.60, "danceability": 0.55, "valence": 0.60, "acousticness": 0.50, "instrumentalness": 0.18, "speechiness": 0.05, "liveness": 0.20, "tempo": 108},
    "acoustic":         {"energy": 0.38, "danceability": 0.50, "valence": 0.58, "acousticness": 0.85, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.15, "tempo": 98},
    "bluegrass":        {"energy": 0.72, "danceability": 0.65, "valence": 0.70, "acousticness": 0.78, "instrumentalness": 0.30, "speechiness": 0.06, "liveness": 0.28, "tempo": 140},

    # Latin
    "latin":            {"energy": 0.78, "danceability": 0.88, "valence": 0.78, "acousticness": 0.20, "instrumentalness": 0.08, "speechiness": 0.08, "liveness": 0.20, "tempo": 118},
    "reggaeton":        {"energy": 0.78, "danceability": 0.90, "valence": 0.70, "acousticness": 0.08, "instrumentalness": 0.10, "speechiness": 0.12, "liveness": 0.12, "tempo": 96},
    "latin pop":        {"energy": 0.72, "danceability": 0.82, "valence": 0.74, "acousticness": 0.18, "instrumentalness": 0.06, "speechiness": 0.07, "liveness": 0.16, "tempo": 116},
    "salsa":            {"energy": 0.82, "danceability": 0.90, "valence": 0.82, "acousticness": 0.25, "instrumentalness": 0.15, "speechiness": 0.07, "liveness": 0.28, "tempo": 178},
    "bachata":          {"energy": 0.68, "danceability": 0.85, "valence": 0.72, "acousticness": 0.35, "instrumentalness": 0.10, "speechiness": 0.06, "liveness": 0.22, "tempo": 130},
    "bossa nova":       {"energy": 0.35, "danceability": 0.72, "valence": 0.72, "acousticness": 0.78, "instrumentalness": 0.25, "speechiness": 0.05, "liveness": 0.15, "tempo": 100},
    "mpb":              {"energy": 0.48, "danceability": 0.70, "valence": 0.65, "acousticness": 0.65, "instrumentalness": 0.20, "speechiness": 0.05, "liveness": 0.18, "tempo": 105},
    "sertanejo":        {"energy": 0.70, "danceability": 0.78, "valence": 0.72, "acousticness": 0.30, "instrumentalness": 0.08, "speechiness": 0.06, "liveness": 0.22, "tempo": 115},
    "cumbia":           {"energy": 0.75, "danceability": 0.88, "valence": 0.78, "acousticness": 0.25, "instrumentalness": 0.12, "speechiness": 0.07, "liveness": 0.25, "tempo": 110},
    "corrido":          {"energy": 0.70, "danceability": 0.72, "valence": 0.60, "acousticness": 0.35, "instrumentalness": 0.08, "speechiness": 0.07, "liveness": 0.22, "tempo": 130},
    "corridos":         {"energy": 0.70, "danceability": 0.72, "valence": 0.60, "acousticness": 0.35, "instrumentalness": 0.08, "speechiness": 0.07, "liveness": 0.22, "tempo": 130},
    "urbano":           {"energy": 0.80, "danceability": 0.88, "valence": 0.65, "acousticness": 0.05, "instrumentalness": 0.08, "speechiness": 0.15, "liveness": 0.12, "tempo": 100},
    "trap latino":      {"energy": 0.80, "danceability": 0.85, "valence": 0.58, "acousticness": 0.05, "instrumentalness": 0.10, "speechiness": 0.18, "liveness": 0.12, "tempo": 140},

    # Indian
    "bollywood":        {"energy": 0.72, "danceability": 0.80, "valence": 0.75, "acousticness": 0.25, "instrumentalness": 0.10, "speechiness": 0.07, "liveness": 0.18, "tempo": 120},
    "filmi":            {"energy": 0.70, "danceability": 0.78, "valence": 0.72, "acousticness": 0.28, "instrumentalness": 0.12, "speechiness": 0.07, "liveness": 0.18, "tempo": 115},
    "desi pop":         {"energy": 0.72, "danceability": 0.80, "valence": 0.72, "acousticness": 0.20, "instrumentalness": 0.10, "speechiness": 0.08, "liveness": 0.16, "tempo": 118},

    # Afro
    "afrobeats":        {"energy": 0.78, "danceability": 0.88, "valence": 0.82, "acousticness": 0.15, "instrumentalness": 0.08, "speechiness": 0.10, "liveness": 0.18, "tempo": 108},
    "afropop":          {"energy": 0.75, "danceability": 0.85, "valence": 0.80, "acousticness": 0.18, "instrumentalness": 0.10, "speechiness": 0.09, "liveness": 0.16, "tempo": 105},
    "amapiano":         {"energy": 0.72, "danceability": 0.90, "valence": 0.75, "acousticness": 0.08, "instrumentalness": 0.55, "speechiness": 0.08, "liveness": 0.15, "tempo": 112},
    "highlife":         {"energy": 0.68, "danceability": 0.82, "valence": 0.80, "acousticness": 0.30, "instrumentalness": 0.20, "speechiness": 0.07, "liveness": 0.25, "tempo": 110},

    # Reggae
    "reggae":           {"energy": 0.62, "danceability": 0.82, "valence": 0.75, "acousticness": 0.30, "instrumentalness": 0.10, "speechiness": 0.08, "liveness": 0.20, "tempo": 88},
    "dancehall":        {"energy": 0.78, "danceability": 0.88, "valence": 0.72, "acousticness": 0.08, "instrumentalness": 0.10, "speechiness": 0.15, "liveness": 0.15, "tempo": 95},
    "dub":              {"energy": 0.58, "danceability": 0.75, "valence": 0.60, "acousticness": 0.20, "instrumentalness": 0.70, "speechiness": 0.05, "liveness": 0.15, "tempo": 88},

    # Gospel / Christian
    "gospel":           {"energy": 0.72, "danceability": 0.65, "valence": 0.82, "acousticness": 0.35, "instrumentalness": 0.05, "speechiness": 0.08, "liveness": 0.28, "tempo": 105},
    "christian":        {"energy": 0.65, "danceability": 0.60, "valence": 0.78, "acousticness": 0.30, "instrumentalness": 0.08, "speechiness": 0.06, "liveness": 0.20, "tempo": 108},

    # Arabic / Middle Eastern
    "arabic":           {"energy": 0.62, "danceability": 0.72, "valence": 0.62, "acousticness": 0.30, "instrumentalness": 0.15, "speechiness": 0.07, "liveness": 0.20, "tempo": 110},
    "khaleeji":         {"energy": 0.65, "danceability": 0.75, "valence": 0.68, "acousticness": 0.28, "instrumentalness": 0.15, "speechiness": 0.07, "liveness": 0.20, "tempo": 112},
}

DEFAULT_FEATURES = {
    "energy": 0.60, "danceability": 0.62, "valence": 0.55,
    "acousticness": 0.30, "instrumentalness": 0.10,
    "speechiness": 0.07, "liveness": 0.15, "tempo": 110,
}


def estimate_features_from_genres(genres: list) -> dict:
    """
    Estimate audio features from genre strings via weighted profile averaging.
    More specific (longer) genre names get higher weight.
    """
    if not genres:
        return DEFAULT_FEATURES.copy()

    matched = []
    genre_lower = [g.lower() for g in genres]

    for g in genre_lower:
        if g in GENRE_PROFILES:
            matched.append((GENRE_PROFILES[g], len(g) + 2))  # +2 for exact match bonus
            continue
        for key, profile in GENRE_PROFILES.items():
            if key in g or g in key:
                matched.append((profile, len(key)))
                break

    if not matched:
        return DEFAULT_FEATURES.copy()

    result = {}
    for feature in DEFAULT_FEATURES:
        total_w = sum(w for _, w in matched if feature in _)
        if total_w == 0:
            result[feature] = DEFAULT_FEATURES[feature]
        else:
            result[feature] = round(
                sum(p[feature] * w for p, w in matched if feature in p) / total_w, 3
            )
    return result


def detect_language(genres: list) -> str:
    if not genres:
        return "English"
    genre_str = " ".join(genres).lower()
    for lang, signals in LANGUAGE_GENRE_SIGNALS:
        for signal in signals:
            if signal in genre_str:
                return lang
    return "English"


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
    instruments = []
    energy        = features.get("energy", 0)
    acoustic      = features.get("acousticness", 0)
    instrumental  = features.get("instrumentalness", 0)
    dance         = features.get("danceability", 0)
    speech        = features.get("speechiness", 0)
    tempo         = features.get("tempo", 0)
    liveness      = features.get("liveness", 0)
    genre_str     = " ".join(genres).lower()

    if dance > 0.5 or energy > 0.5:
        instruments.append("Drums")
    if dance > 0.7 and tempo > 100:
        instruments.append("Hi-hats")
    if energy > 0.4 or dance > 0.5:
        instruments.append("Bass")
    if acoustic > 0.4 or any(g in genre_str for g in ["rock", "folk", "country", "indie", "alternative"]):
        instruments.append("Acoustic Guitar")
    if energy > 0.6 and acoustic < 0.4 and any(g in genre_str for g in ["rock", "metal", "punk", "grunge"]):
        instruments.append("Electric Guitar")
    if any(g in genre_str for g in ["pop", "soul", "r&b", "jazz", "classical", "blues", "gospel"]):
        instruments.append("Piano/Keys")
    if any(g in genre_str for g in ["electronic", "edm", "house", "techno", "synth", "pop", "hip hop", "trap"]):
        instruments.append("Synthesizer")
    if any(g in genre_str for g in ["classical", "orchestral", "film", "cinematic", "ambient", "orchestra"]):
        instruments.append("Strings")
    if speech < 0.33 and instrumental < 0.5:
        instruments.append("Lead Vocals")
    if speech > 0.33 and speech < 0.66:
        instruments.append("Rap/Spoken Word")
    if liveness > 0.6:
        instruments.append("Live Audience")
    if any(g in genre_str for g in ["trap", "hip hop", "rap"]) and dance > 0.6:
        instruments.append("808 Bass")

    return list(dict.fromkeys(instruments))


def infer_vocal_style(features: dict, genres: list) -> str:
    speech       = features.get("speechiness", 0)
    energy       = features.get("energy", 0)
    instrumental = features.get("instrumentalness", 0)
    acoustic     = features.get("acousticness", 0)
    genre_str    = " ".join(genres).lower()

    if instrumental > 0.8:
        return "Instrumental"
    if speech > 0.66:
        return "Rap / Spoken Word"
    if speech > 0.33:
        return "Melodic Rap"
    if energy > 0.8:
        return "Powerful / Belting"
    if any(g in genre_str for g in ["r&b", "soul", "neo soul"]):
        return "Soulful / R&B"
    if any(g in genre_str for g in ["jazz"]):
        return "Jazz Phrasing"
    if any(g in genre_str for g in ["classical", "opera"]):
        return "Operatic"
    if acoustic > 0.6:
        return "Intimate / Soft"
    return "Pop / Melodic"


def parse_timestamp(ts: str) -> Optional[int]:
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
    energy   = features.get("energy", 0)
    valence  = features.get("valence", 0)
    minutes  = ts_seconds // 60
    seconds  = ts_seconds % 60
    time_str = f"{minutes}:{seconds:02d}"

    duration_ms    = features.get("duration_ms", 240000)
    duration_s     = duration_ms / 1000
    position_ratio = ts_seconds / duration_s if duration_s > 0 else 0.5

    if position_ratio < 0.15:     section = "intro"
    elif position_ratio < 0.35:   section = "first verse / pre-chorus"
    elif position_ratio < 0.55:   section = "chorus / hook"
    elif position_ratio < 0.75:   section = "bridge / second chorus"
    else:                         section = "outro"

    energy_desc = "high energy" if energy > 0.7 else ("moderate energy" if energy > 0.4 else "low energy")
    mood_desc   = "uplifting" if valence > 0.6 else ("melancholic" if valence < 0.35 else "neutral")

    return {
        "time": time_str,
        "description": (
            f"Pinned at {time_str} — likely the {section} section. "
            f"This moment has {energy_desc} with a {mood_desc} emotional tone."
        ),
    }


class FingerprintService:
    def build(
        self,
        track_info: dict,
        audio_features: Optional[dict],
        timestamp: Optional[str],
    ) -> dict:
        genres   = track_info.get("_genres", [])
        year     = track_info.get("year")
        language = detect_language(genres)

        # Use real Spotify audio features if available, else estimate from genres
        if audio_features and audio_features.get("energy") is not None:
            af = audio_features
            features_source = "measured"
        else:
            af = estimate_features_from_genres(genres)
            # Inject duration_ms from track_info so timestamp logic works
            af["duration_ms"] = track_info.get("duration_ms", 240000)
            features_source = "estimated"

        key_num   = af.get("key", -1) if features_source == "measured" else -1
        mode_num  = af.get("mode", 1) if features_source == "measured" else None
        tempo     = af.get("tempo", 110)

        key_name  = KEY_NAMES[key_num] if 0 <= key_num <= 11 else None
        mode_name = ("Major" if mode_num == 1 else "Minor") if mode_num is not None else None

        instruments  = infer_instruments(af, genres)
        vocal_style  = infer_vocal_style(af, genres)
        tempo_norm   = min(tempo / 200, 1.0)

        fp = {
            "spotify_id":      track_info.get("spotify_id"),
            "key":             f"{key_name} {mode_name}" if key_name and mode_name else None,
            "tempo":           round(tempo, 1),
            "era":             get_era(year),
            "mode":            mode_name,
            "language":        language,
            "genres":          genres[:6],
            "instruments":     instruments,
            "vocal_style":     vocal_style,
            "features_source": features_source,
            "audio_features":  {
                "energy":           round(af.get("energy", 0), 3),
                "danceability":     round(af.get("danceability", 0), 3),
                "valence":          round(af.get("valence", 0), 3),
                "acousticness":     round(af.get("acousticness", 0), 3),
                "instrumentalness": round(af.get("instrumentalness", 0), 3),
                "speechiness":      round(af.get("speechiness", 0), 3),
                "liveness":         round(af.get("liveness", 0), 3),
                "tempo_norm":       round(tempo_norm, 3),
            },
        }

        if timestamp:
            ts_seconds = parse_timestamp(timestamp)
            if ts_seconds is not None:
                fp["timestamp_highlight"] = describe_timestamp(
                    ts_seconds, af, track_info.get("name", "")
                )

        fp_str = json.dumps({"id": track_info.get("spotify_id"), "ts": timestamp or "none"}, sort_keys=True)
        fp["hash"] = hashlib.sha256(fp_str.encode()).hexdigest()

        return fp
