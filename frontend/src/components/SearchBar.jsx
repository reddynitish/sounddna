import { useState } from 'react'

export default function SearchBar({ onAnalyze, onReset, hasResult }) {
  const [url, setUrl] = useState('')
  const [timestamp, setTimestamp] = useState('')
  const [showTimestamp, setShowTimestamp] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!url.trim()) return
    onAnalyze({ url: url.trim(), timestamp: timestamp.trim() || null })
  }

  const handleReset = () => {
    setUrl('')
    setTimestamp('')
    setShowTimestamp(false)
    onReset()
  }

  // Validate rough URL format
  const isValidUrl = url.trim().length > 0 && (
    url.includes('spotify.com') ||
    url.includes('youtube.com') ||
    url.includes('youtu.be') ||
    url.includes('music.apple.com')
  )

  return (
    <div className="space-y-3">
      {/* Main input row */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20">
            <LinkIcon />
          </div>
          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
            placeholder="Paste a Spotify or YouTube link..."
            className="w-full bg-surface border border-border rounded-2xl py-4 pl-12 pr-4 text-white/80 font-body placeholder:text-white/20 focus:outline-none focus:border-acid/40 input-glow transition-all duration-200 text-sm"
          />
          {/* Platform pill */}
          {url.includes('spotify') && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <span className="text-xs font-mono text-green-400/60 bg-green-400/10 px-2 py-0.5 rounded-full">Spotify</span>
            </div>
          )}
          {(url.includes('youtube') || url.includes('youtu.be')) && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <span className="text-xs font-mono text-red-400/60 bg-red-400/10 px-2 py-0.5 rounded-full">YouTube</span>
            </div>
          )}
        </div>

        {/* Analyze / Reset button */}
        {!hasResult ? (
          <button
            onClick={handleSubmit}
            disabled={!isValidUrl}
            className="px-6 py-4 bg-acid text-obsidian font-display font-700 text-sm rounded-2xl hover:bg-acid/90 active:scale-95 transition-all duration-150 disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap"
          >
            Decode DNA
          </button>
        ) : (
          <button
            onClick={handleReset}
            className="px-6 py-4 bg-surface border border-border text-white/60 font-display font-600 text-sm rounded-2xl hover:border-acid/30 hover:text-white/80 active:scale-95 transition-all duration-150 whitespace-nowrap"
          >
            New Song
          </button>
        )}
      </div>

      {/* Timestamp toggle + input */}
      {!hasResult && (
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowTimestamp(!showTimestamp)}
            className="flex items-center gap-2 text-xs font-mono text-white/30 hover:text-acid/60 transition-colors duration-150"
          >
            <span className={`w-4 h-4 rounded border flex items-center justify-center transition-all duration-150 ${showTimestamp ? 'border-acid/60 bg-acid/20' : 'border-white/20'}`}>
              {showTimestamp && <span className="text-acid text-[10px]">✓</span>}
            </span>
            Pin a moment (optional)
          </button>

          {showTimestamp && (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={timestamp}
                onChange={e => setTimestamp(e.target.value)}
                placeholder="e.g. 1:20"
                className="w-24 bg-surface border border-border rounded-xl py-1.5 px-3 text-white/70 font-mono text-xs placeholder:text-white/20 focus:outline-none focus:border-acid/40 transition-all"
              />
              <span className="text-white/20 font-mono text-xs">mm:ss</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function LinkIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M6.5 9.5L9.5 6.5M7 4H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9M10 2h4m0 0v4m0-4L7 9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
