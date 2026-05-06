# 🧬 SoundDNA

**Every song has a fingerprint. Find yours.**

SoundDNA analyzes any Spotify or YouTube link and generates a unique musical DNA — the actual ingredients that make a song sound the way it does. Pin a moment you loved (e.g. "1:20") and it focuses the analysis on that exact section. Then it finds other songs built from the same ingredients.

---

## What it does

1. **Paste a link** — Spotify or YouTube
2. **Pin a moment** (optional) — the timestamp you loved
3. **Get a fingerprint** — radar chart + ingredient breakdown: key, BPM, instruments, production era, vocal style, genre blend
4. **Get recommendations** — songs that match the same musical DNA, not just the same genre

---

## Why it's different

Most music apps recommend based on genre or listening history. SoundDNA recommends based on *what a song is made of*. If you loved the acoustic guitar + 98 BPM + melancholic minor key of a moment in one song, it finds other songs with those same building blocks — regardless of artist, language, or era.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | React + Tailwind CSS + Recharts |
| Backend | FastAPI (Python) |
| Audio Analysis | Spotify Web API |
| Database | Supabase (PostgreSQL) |
| Frontend hosting | Vercel |
| Backend hosting | Railway |

---

## Local Development

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your keys (see Environment Variables below)

uvicorn main:app --reload
# Runs on http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

For production (Vercel), set `VITE_API_URL` to your Railway backend URL.

---

## Database Setup (Supabase)

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Run the contents of `supabase_schema.sql`
4. Copy your project URL and service role key to `.env`

---

## Deployment

### Backend → Railway

1. Push repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the `backend/` folder
4. Add environment variables in Railway dashboard
5. Railway auto-detects Python and deploys

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub
2. Set Root Directory to `frontend/`
3. Add `VITE_API_URL` environment variable pointing to your Railway URL
4. Deploy

---

## The bigger vision

Every song analyzed gets stored in our database with its full fingerprint. Over time this becomes a proprietary dataset of musical DNA. The roadmap:

- [ ] Deep audio analysis (waveform-level ML)
- [ ] Public API for developers
- [ ] User accounts + saved fingerprints
- [ ] Social sharing — compare your music DNA with friends
- [ ] Browser extension for Spotify Web Player

---

## Spotify API Setup

Get your credentials at [developer.spotify.com](https://developer.spotify.com):
1. Create an app
2. Copy Client ID and Client Secret
3. Add `http://localhost:8000` to Redirect URIs (for future OAuth)

---

Built with ❤️ by [reddynitish](https://github.com/reddynitish)
