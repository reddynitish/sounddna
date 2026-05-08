import { useState, useEffect } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import FingerprintCard from './components/FingerprintCard'
import Recommendations from './components/Recommendations'
import LoadingDNA from './components/LoadingDNA'
import { analyzeSong } from './utils/api'

export default function App() {
  const [phase, setPhase] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Mouse aurora blob
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const smoothX = useSpring(mouseX, { stiffness: 60, damping: 20 })
  const smoothY = useSpring(mouseY, { stiffness: 60, damping: 20 })

  useEffect(() => {
    const move = (e) => { mouseX.set(e.clientX); mouseY.set(e.clientY) }
    window.addEventListener('mousemove', move)
    return () => window.removeEventListener('mousemove', move)
  }, [mouseX, mouseY])

  const handleAnalyze = async ({ url, timestamp }) => {
    setPhase('loading')
    setError(null)
    setResult(null)
    try {
      const data = await analyzeSong(url, timestamp)
      setResult(data)
      setPhase('result')
    } catch (err) {
      setError(err.message || 'Failed to analyze. Check the URL and try again.')
      setPhase('idle')
    }
  }

  const handleReset = () => {
    setPhase('idle')
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-obsidian relative overflow-x-hidden">
      {/* Mouse-following aurora blob */}
      <motion.div
        className="fixed pointer-events-none z-0"
        style={{
          left: smoothX,
          top: smoothY,
          x: '-50%',
          y: '-50%',
          width: 600,
          height: 600,
          background: 'radial-gradient(circle, #c8f53d0a 0%, #7b61ff06 40%, transparent 70%)',
          borderRadius: '50%',
          filter: 'blur(40px)',
        }}
      />

      {/* Static ambient blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.4, 0.6, 0.4] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-[-20%] left-[-10%] w-[700px] h-[700px] rounded-full bg-plasma/5 blur-[140px]"
        />
        <motion.div
          animate={{ scale: [1, 1.08, 1], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
          className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-acid/4 blur-[120px]"
        />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <div className="flex items-center gap-3 mb-10">
            <DNAIcon />
            <span className="font-mono text-xs text-acid/60 tracking-[0.3em] uppercase">Sound DNA</span>
          </div>

          <AnimatePresence mode="wait">
            {phase === 'idle' && (
              <motion.div
                key="hero"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                <Hero />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.header>

        {/* Search bar */}
        <AnimatePresence>
          {phase !== 'loading' && (
            <motion.div
              key="search"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            >
              <SearchBar
                onAnalyze={handleAnalyze}
                onReset={handleReset}
                hasResult={phase === 'result'}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0 }}
              className="mt-6 p-4 rounded-xl border border-ember/20 bg-ember/5 text-ember/80 font-mono text-sm"
            >
              ⚠ {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading */}
        <AnimatePresence>
          {phase === 'loading' && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <LoadingDNA />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {phase === 'result' && result && (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="mt-12 space-y-8"
            >
              <FingerprintCard fingerprint={result.fingerprint} song={result.song} />
              <Recommendations recommendations={result.recommendations} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

function DNAIcon() {
  return (
    <motion.svg
      width="28" height="28" viewBox="0 0 28 28" fill="none"
      animate={{ rotate: [0, 5, -5, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
    >
      <path d="M9 4C9 4 10.5 7 14 7C17.5 7 19 4 19 4" stroke="#c8f53d" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M9 24C9 24 10.5 21 14 21C17.5 21 19 24 19 24" stroke="#c8f53d" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M9 4C7 8 7 11 9 14C11 17 11 20 9 24" stroke="#7b61ff" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M19 4C21 8 21 11 19 14C17 17 17 20 19 24" stroke="#7b61ff" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="9.5" y1="10" x2="18.5" y2="10" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
      <line x1="8.5" y1="14" x2="19.5" y2="14" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
      <line x1="9.5" y1="18" x2="18.5" y2="18" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
    </motion.svg>
  )
}
