import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const STEPS = [
  { label: 'Identifying track...', sub: 'Matching audio signature' },
  { label: 'Scanning genre profile...', sub: 'Tempo · Key · Energy · Valence' },
  { label: 'Detecting instruments...', sub: 'Running spectral analysis' },
  { label: 'Profiling production style...', sub: 'Era · Genre · Vocal character' },
  { label: 'Building fingerprint...', sub: 'Encoding DNA sequence' },
  { label: 'Finding matches...', sub: 'Scanning ingredient database' },
]

export default function LoadingDNA() {
  const [step, setStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const stepInterval = setInterval(() => setStep(s => Math.min(s + 1, STEPS.length - 1)), 1800)
    const progressInterval = setInterval(() => setProgress(p => Math.min(p + 1, 95)), 100)
    return () => { clearInterval(stepInterval); clearInterval(progressInterval) }
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-16 flex flex-col items-center gap-10"
    >
      {/* DNA Helix */}
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="relative w-28 h-44"
      >
        <HelixAnimation />
      </motion.div>

      {/* Step text with AnimatePresence */}
      <div className="text-center space-y-2 min-h-[56px] flex flex-col items-center justify-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 10, filter: 'blur(4px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -10, filter: 'blur(4px)' }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="font-display text-white/90 text-lg font-600">
              {STEPS[step]?.label}
            </div>
            <div className="font-mono text-xs text-white/30 tracking-wider mt-1">
              {STEPS[step]?.sub}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Progress bar */}
      <div className="w-64 space-y-2">
        <div className="w-full h-px bg-white/5 rounded-full overflow-hidden relative">
          <motion.div
            className="h-full bg-gradient-to-r from-acid/60 to-acid rounded-full"
            style={{ width: `${progress}%` }}
            transition={{ ease: 'easeOut' }}
          />
          <div className="absolute inset-0 loading-bar" />
        </div>
        <div className="flex justify-between font-mono text-[10px] text-white/20">
          <span>analyzing</span>
          <motion.span
            key={progress}
            initial={{ opacity: 0.5 }}
            animate={{ opacity: 1 }}
          >
            {progress}%
          </motion.span>
        </div>
      </div>

      {/* Step dots */}
      <div className="flex gap-2">
        {STEPS.map((_, i) => (
          <motion.div
            key={i}
            animate={i <= step
              ? { backgroundColor: '#c8f53d', scale: i === step ? 1.4 : 1 }
              : { backgroundColor: '#ffffff1a', scale: 1 }
            }
            transition={{ duration: 0.4, type: 'spring', stiffness: 400, damping: 20 }}
            className="w-1.5 h-1.5 rounded-full"
          />
        ))}
      </div>
    </motion.div>
  )
}

function HelixAnimation() {
  return (
    <svg viewBox="0 0 80 160" className="w-full h-full" style={{ filter: 'drop-shadow(0 0 16px #c8f53d55)' }}>
      {/* Left strand */}
      <path
        d="M20 10 C20 10, 60 30, 60 50 C60 70, 20 90, 20 110 C20 130, 60 150, 60 150"
        stroke="#c8f53d"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      >
        <animate attributeName="stroke-dashoffset" values="0;-200" dur="2s" repeatCount="indefinite" />
        <animate attributeName="stroke-dasharray" values="10 5" dur="2s" repeatCount="indefinite" />
      </path>

      {/* Right strand */}
      <path
        d="M60 10 C60 10, 20 30, 20 50 C20 70, 60 90, 60 110 C60 130, 20 150, 20 150"
        stroke="#7b61ff"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
      >
        <animate attributeName="stroke-dashoffset" values="0;-200" dur="2s" repeatCount="indefinite" />
        <animate attributeName="stroke-dasharray" values="10 5" dur="2s" repeatCount="indefinite" />
      </path>

      {/* Cross links */}
      {[30, 50, 70, 90, 110, 130].map((y, i) => {
        const xLeft  = i % 2 === 0 ? 20 : 60
        const xRight = i % 2 === 0 ? 60 : 20
        const colors = ['#c8f53d', '#7b61ff', '#ff6b35', '#38bdf8', '#c8f53d', '#7b61ff']
        return (
          <line key={y} x1={xLeft} y1={y} x2={xRight} y2={y}
            stroke={colors[i]} strokeWidth="1.2" strokeLinecap="round" opacity="0.5">
            <animate attributeName="opacity" values="0.2;0.9;0.2" dur={`${1.5 + i * 0.2}s`} repeatCount="indefinite" />
          </line>
        )
      })}

      {/* Pulsing nodes */}
      {[30, 70, 110].map((y, i) => (
        <circle key={y} cx={20} cy={y} r="3" fill="#c8f53d">
          <animate attributeName="r" values="2;4.5;2" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;1;0.6" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
        </circle>
      ))}
      {[50, 90, 130].map((y, i) => (
        <circle key={y} cx={60} cy={y} r="3" fill="#7b61ff">
          <animate attributeName="r" values="2;4.5;2" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;1;0.6" dur={`${2 + i * 0.3}s`} repeatCount="indefinite" />
        </circle>
      ))}
    </svg>
  )
}
