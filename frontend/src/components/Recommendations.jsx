import { motion, AnimatePresence } from 'framer-motion'
import { useRef } from 'react'

const MATCH_COLORS = ['#c8f53d', '#7b61ff', '#38bdf8', '#ff6b35', '#c8f53d', '#7b61ff']

const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09, delayChildren: 0.05 } },
}
const cardVariant = {
  hidden: { opacity: 0, y: 28, scale: 0.97 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.55, ease: [0.16, 1, 0.3, 1] } },
}

export default function Recommendations({ recommendations }) {
  if (!recommendations?.length) return null

  return (
    <div className="space-y-4">
      <motion.div
        initial={{ opacity: 0, x: -16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="flex items-center gap-4"
      >
        <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
          Ingredient Matches
        </div>
        <div className="flex-1 h-px bg-white/5" />
        <div className="font-mono text-[10px] text-white/20">
          {recommendations.length} found
        </div>
      </motion.div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="visible"
        className="space-y-3"
      >
        {recommendations.map((rec, i) => (
          <motion.div key={rec.id || i} variants={cardVariant}>
            <RecommendationRow rec={rec} rank={i + 1} color={MATCH_COLORS[i % MATCH_COLORS.length]} />
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

function RecommendationRow({ rec, rank, color }) {
  const matchPct = Math.round(rec.match_score * 100)
  const barRef = useRef(null)

  return (
    <motion.a
      href={rec.external_url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      whileHover={{
        y: -2,
        boxShadow: `0 8px 32px #00000055, 0 0 0 1px ${color}18`,
        transition: { type: 'spring', stiffness: 400, damping: 25 },
      }}
      whileTap={{ scale: 0.99 }}
      className="flex items-center gap-4 p-4 bg-surface border border-border rounded-2xl group block"
      style={{ cursor: 'pointer' }}
    >
      {/* Rank */}
      <div className="w-6 text-center font-mono text-xs text-white/20 flex-shrink-0 group-hover:text-white/40 transition-colors">
        {rank}
      </div>

      {/* Album art */}
      {rec.image ? (
        <motion.img
          src={rec.image}
          alt={rec.title}
          className="w-12 h-12 rounded-xl object-cover ring-1 ring-white/10 flex-shrink-0"
          whileHover={{ scale: 1.05 }}
          transition={{ type: 'spring', stiffness: 400, damping: 20 }}
        />
      ) : (
        <div className="w-12 h-12 rounded-xl bg-panel flex items-center justify-center flex-shrink-0">
          <span className="text-white/20 text-lg">♪</span>
        </div>
      )}

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="font-display text-sm font-600 text-white/90 truncate group-hover:text-white transition-colors duration-200">
          {rec.title}
        </div>
        <div className="font-body text-xs text-white/40 truncate mt-0.5">
          {rec.artist}
          {rec.year && <span className="ml-2 text-white/20">· {rec.year}</span>}
        </div>

        {/* Ingredient badges */}
        {rec.matching_ingredients?.length > 0 && (
          <div className="flex gap-1.5 mt-2 flex-wrap">
            {rec.matching_ingredients.slice(0, 4).map((ing, idx) => (
              <motion.span
                key={ing}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + idx * 0.05, type: 'spring', stiffness: 400, damping: 20 }}
                className="font-mono text-[10px] px-1.5 py-0.5 rounded-md"
                style={{
                  background: color + '12',
                  color:      color + 'aa',
                  border:     `1px solid ${color}22`,
                }}
              >
                {ing}
              </motion.span>
            ))}
          </div>
        )}
      </div>

      {/* Score */}
      <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 350, damping: 20 }}
          className="font-display text-sm font-700"
          style={{ color }}
        >
          {matchPct}%
        </motion.div>

        {/* Animated progress bar */}
        <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${matchPct}%` }}
            transition={{ duration: 0.9, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            style={{ background: color }}
          />
        </div>

        <div className="font-mono text-[10px] text-white/20">match</div>
      </div>
    </motion.a>
  )
}
