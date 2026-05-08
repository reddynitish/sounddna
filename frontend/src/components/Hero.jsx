import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const WORDS = ['fingerprint.', 'signature.', 'blueprint.', 'identity.']

const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08, delayChildren: 0.3 } },
}
const word = {
  hidden: { opacity: 0, y: 24, filter: 'blur(8px)' },
  visible: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } },
}
const fadeUp = (delay = 0) => ({
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1], delay } },
})

export default function Hero() {
  const [wordIdx, setWordIdx] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setWordIdx(i => (i + 1) % WORDS.length), 2800)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="space-y-8">
      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-acid/20 bg-acid/5"
      >
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-acid opacity-75" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-acid" />
        </span>
        <span className="font-mono text-[10px] text-acid/70 tracking-[0.2em] uppercase">
          Musical DNA decoder
        </span>
      </motion.div>

      {/* Headline — word stagger */}
      <motion.h1
        variants={container}
        initial="hidden"
        animate="visible"
        className="font-display text-[clamp(2.8rem,6vw,5rem)] font-800 leading-[1.05] tracking-tight"
      >
        {['Every', 'song', 'has', 'a'].map((w, i) => (
          <motion.span key={i} variants={word} className="inline-block mr-[0.22em]">
            {w}
          </motion.span>
        ))}
        <br />
        <motion.span
          key={wordIdx}
          initial={{ opacity: 0, y: 20, filter: 'blur(6px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="text-acid-glow inline-block"
        >
          {WORDS[wordIdx]}
        </motion.span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        variants={fadeUp(0.55)}
        initial="hidden"
        animate="visible"
        className="text-white/40 font-body text-lg max-w-lg leading-relaxed"
      >
        Drop a Spotify or YouTube link. Pin a moment you loved.
        We decode its musical DNA — and find songs built from the same ingredients.
      </motion.p>

      {/* Stats row */}
      <motion.div
        variants={fadeUp(0.75)}
        initial="hidden"
        animate="visible"
        className="flex items-center gap-6 pt-2"
      >
        <StatPill label="Ingredient axes" value="8" />
        <Divider />
        <StatPill label="Precision" value="To the second" />
        <Divider />
        <StatPill label="Match logic" value="Ingredient-based" />
      </motion.div>

      {/* Waveform visual */}
      <motion.div
        variants={fadeUp(0.9)}
        initial="hidden"
        animate="visible"
        className="flex items-end gap-[3px] h-8 pt-2 opacity-30"
      >
        {Array.from({ length: 32 }).map((_, i) => (
          <WaveBar key={i} delay={i * 0.04} />
        ))}
      </motion.div>
    </div>
  )
}

function WaveBar({ delay }) {
  return (
    <motion.div
      className="w-[3px] rounded-full bg-acid"
      animate={{ scaleY: [0.2, 1, 0.3, 0.8, 0.15, 1, 0.4] }}
      transition={{
        duration: 2.4,
        repeat: Infinity,
        repeatType: 'mirror',
        ease: 'easeInOut',
        delay,
      }}
      style={{ height: '100%', transformOrigin: 'bottom' }}
    />
  )
}

function StatPill({ label, value }) {
  return (
    <div>
      <div className="font-mono text-[10px] text-acid/50 mb-1 tracking-wider uppercase">{label}</div>
      <div className="font-display text-sm text-white/80 font-600">{value}</div>
    </div>
  )
}

function Divider() {
  return <div className="w-px h-8 bg-white/10" />
}
