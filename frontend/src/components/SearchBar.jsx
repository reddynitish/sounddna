import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function SearchBar({ onAnalyze, onReset, hasResult }) {
  const [url, setUrl] = useState('')
  const [timestamp, setTimestamp] = useState('')
  const [showTimestamp, setShowTimestamp] = useState(false)
  const [focused, setFocused] = useState(false)

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

  const isSpotify = url.includes('spotify.com')
  const isYouTube = url.includes('youtube.com') || url.includes('youtu.be')
  const isValidUrl = url.trim().length > 0 && (isSpotify || isYouTube || url.includes('music.apple.com'))

  return (
    <div className="space-y-3">
      {/* Input row */}
      <div className="flex gap-3">
        <motion.div
          className="flex-1 relative"
          animate={{ scale: focused ? 1.005 : 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        >
          {/* Glow ring */}
          <AnimatePresence>
            {focused && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 rounded-2xl pointer-events-none"
                style={{ boxShadow: '0 0 0 1px #c8f53d22, 0 0 30px #c8f53d10' }}
              />
            )}
          </AnimatePresence>

          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20">
            <LinkIcon />
          </div>

          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Paste a Spotify or YouTube link..."
            className="w-full bg-surface border border-border rounded-2xl py-4 pl-12 pr-4 text-white/80 font-body placeholder:text-white/20 focus:outline-none focus:border-acid/30 transition-colors duration-200 text-sm"
          />

          {/* Platform pill */}
          <AnimatePresence>
            {(isSpotify || isYouTube) && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, x: 8 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                className="absolute right-4 top-1/2 -translate-y-1/2"
              >
                {isSpotify && (
                  <span className="text-xs font-mono text-green-400/70 bg-green-400/10 px-2 py-0.5 rounded-full border border-green-400/20">
                    Spotify
                  </span>
                )}
                {isYouTube && (
                  <span className="text-xs font-mono text-red-400/70 bg-red-400/10 px-2 py-0.5 rounded-full border border-red-400/20">
                    YouTube
                  </span>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Button */}
        <AnimatePresence mode="wait">
          {!hasResult ? (
            <motion.button
              key="analyze"
              onClick={handleSubmit}
              disabled={!isValidUrl}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              whileHover={isValidUrl ? { scale: 1.03, boxShadow: '0 0 24px #c8f53d33' } : {}}
              whileTap={isValidUrl ? { scale: 0.96 } : {}}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className="px-6 py-4 bg-acid text-obsidian font-display font-700 text-sm rounded-2xl disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap cursor-pointer"
            >
              Decode DNA
            </motion.button>
          ) : (
            <motion.button
              key="reset"
              onClick={handleReset}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              whileHover={{ scale: 1.03, borderColor: '#c8f53d44' }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className="px-6 py-4 bg-surface border border-border text-white/60 font-display font-600 text-sm rounded-2xl whitespace-nowrap cursor-pointer"
            >
              New Song
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Timestamp toggle */}
      <AnimatePresence>
        {!hasResult && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center gap-4 overflow-hidden"
          >
            <button
              onClick={() => setShowTimestamp(!showTimestamp)}
              className="flex items-center gap-2 text-xs font-mono text-white/30 hover:text-acid/60 transition-colors duration-150 cursor-pointer"
            >
              <motion.span
                animate={showTimestamp ? { borderColor: '#c8f53d99', backgroundColor: '#c8f53d1a' } : {}}
                className="w-4 h-4 rounded border border-white/20 flex items-center justify-center transition-all duration-150"
              >
                <AnimatePresence>
                  {showTimestamp && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      className="text-acid text-[10px]"
                    >
                      ✓
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.span>
              Pin a moment (optional)
            </button>

            <AnimatePresence>
              {showTimestamp && (
                <motion.div
                  initial={{ opacity: 0, x: -10, width: 0 }}
                  animate={{ opacity: 1, x: 0, width: 'auto' }}
                  exit={{ opacity: 0, x: -10, width: 0 }}
                  className="flex items-center gap-2 overflow-hidden"
                >
                  <input
                    type="text"
                    value={timestamp}
                    onChange={e => setTimestamp(e.target.value)}
                    placeholder="1:20"
                    className="w-24 bg-surface border border-border rounded-xl py-1.5 px-3 text-white/70 font-mono text-xs placeholder:text-white/20 focus:outline-none focus:border-acid/40 transition-all"
                  />
                  <span className="text-white/20 font-mono text-xs whitespace-nowrap">mm:ss</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
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
