import { useState } from 'react'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import FingerprintCard from './components/FingerprintCard'
import Recommendations from './components/Recommendations'
import LoadingDNA from './components/LoadingDNA'
import { analyzeSong } from './utils/api'

export default function App() {
  const [phase, setPhase] = useState('idle') // idle | loading | result
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async ({ url, timestamp }) => {
    setPhase('loading')
    setError(null)
    setResult(null)
    try {
      const data = await analyzeSong(url, timestamp)
      setResult(data)
      setPhase('result')
    } catch (err) {
      setError(err.message || 'Failed to analyze song. Check the URL and try again.')
      setPhase('idle')
    }
  }

  const handleReset = () => {
    setPhase('idle')
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-obsidian relative">
      {/* Background ambient blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-plasma/5 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-acid/5 blur-[100px]" />
        <div className="absolute top-[40%] left-[50%] w-[300px] h-[300px] rounded-full bg-ember/4 blur-[80px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <header className="mb-16">
          <div className="flex items-center gap-3 mb-8">
            <DNAIcon />
            <span className="font-mono text-xs text-acid/70 tracking-[0.3em] uppercase">Sound DNA</span>
          </div>
          {phase === 'idle' && <Hero />}
        </header>

        {/* Search */}
        {phase !== 'loading' && (
          <SearchBar
            onAnalyze={handleAnalyze}
            onReset={handleReset}
            hasResult={phase === 'result'}
          />
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 p-4 rounded-xl border border-ember/20 bg-ember/5 text-ember/80 font-mono text-sm">
            ⚠ {error}
          </div>
        )}

        {/* Loading */}
        {phase === 'loading' && <LoadingDNA />}

        {/* Results */}
        {phase === 'result' && result && (
          <div className="mt-12 space-y-8">
            <FingerprintCard fingerprint={result.fingerprint} song={result.song} />
            <Recommendations recommendations={result.recommendations} />
          </div>
        )}
      </div>
    </div>
  )
}

function DNAIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <path d="M9 4C9 4 10.5 7 14 7C17.5 7 19 4 19 4" stroke="#c8f53d" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M9 24C9 24 10.5 21 14 21C17.5 21 19 24 19 24" stroke="#c8f53d" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M9 4C7 8 7 11 9 14C11 17 11 20 9 24" stroke="#7b61ff" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M19 4C21 8 21 11 19 14C17 17 17 20 19 24" stroke="#7b61ff" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="9.5" y1="10" x2="18.5" y2="10" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
      <line x1="8.5" y1="14" x2="19.5" y2="14" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
      <line x1="9.5" y1="18" x2="18.5" y2="18" stroke="#c8f53d44" strokeWidth="1" strokeLinecap="round"/>
    </svg>
  )
}
