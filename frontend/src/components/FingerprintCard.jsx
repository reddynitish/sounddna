import { motion } from 'framer-motion'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts'

const AXIS_LABELS = {
  energy:           'Energy',
  danceability:     'Dance',
  instrumentalness: 'Instru.',
  acousticness:     'Acoustic',
  valence:          'Positivity',
  speechiness:      'Vocal',
  tempo_norm:       'Tempo',
  liveness:         'Live',
}

const DNA_COLORS = ['#c8f53d', '#7b61ff', '#ff6b35', '#38bdf8', '#ff6b35', '#c8f53d']

const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07, delayChildren: 0.1 } },
}
const slideUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.16, 1, 0.3, 1] } },
}

export default function FingerprintCard({ fingerprint, song }) {
  const radarData = Object.entries(AXIS_LABELS).map(([key, label]) => ({
    axis:     label,
    value:    Math.round((fingerprint.audio_features?.[key] ?? 0) * 100),
    fullMark: 100,
  }))

  const isEstimated = fingerprint.features_source === 'estimated'

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="visible"
      className="space-y-5"
    >
      {/* Song identity */}
      <motion.div variants={slideUp} className="flex items-start gap-4">
        {song?.image && (
          <motion.img
            src={song.image}
            alt={song.title}
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="w-16 h-16 rounded-xl object-cover ring-1 ring-white/10"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="font-mono text-[10px] text-acid/60 tracking-[0.25em] uppercase mb-1">
            DNA Decoded
          </div>
          <h2 className="font-display text-xl font-700 text-white truncate">
            {song?.title || 'Unknown Track'}
          </h2>
          <div className="text-white/40 font-body text-sm">
            {song?.artist || 'Unknown Artist'}
            {song?.year && <span className="ml-2 text-white/20">· {song.year}</span>}
          </div>
        </div>
        <FingerprintHash hash={fingerprint.hash} />
      </motion.div>

      {/* Main grid */}
      <div className="grid grid-cols-5 gap-4">
        {/* Radar */}
        <motion.div
          variants={slideUp}
          className="col-span-3 bg-surface border border-border rounded-2xl p-4 animated-border"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
              Audio Profile
            </div>
            {isEstimated && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="font-mono text-[9px] px-2 py-0.5 rounded-full bg-plasma/10 border border-plasma/20 text-plasma/60"
              >
                genre-estimated
              </motion.span>
            )}
          </div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <PolarGrid />
                <PolarAngleAxis dataKey="axis" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Song"
                  dataKey="value"
                  stroke="#c8f53d"
                  fill="#c8f53d"
                  fillOpacity={0.12}
                  strokeWidth={1.5}
                  dot={{ fill: '#c8f53d', r: 2 }}
                  isAnimationActive={true}
                  animationDuration={900}
                  animationEasing="ease-out"
                />
                <Tooltip
                  contentStyle={{
                    background:   '#12121f',
                    border:       '1px solid #ffffff0f',
                    borderRadius: '10px',
                    fontFamily:   'JetBrains Mono',
                    fontSize:     '11px',
                    color:        '#c8f53d',
                  }}
                  formatter={(v) => [`${v}/100`, '']}
                />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>
        </motion.div>

        {/* Right panel */}
        <div className="col-span-2 space-y-3">
          {/* Core stats */}
          <motion.div variants={slideUp} className="bg-surface border border-border rounded-2xl p-4 space-y-3">
            <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase mb-1">
              Core Ingredients
            </div>
            {fingerprint.key     && <StatRow label="Key"      value={fingerprint.key}                                   color="acid"   delay={0.05} />}
            <StatRow               label="BPM"      value={fingerprint.tempo ? Math.round(fingerprint.tempo) : '—'}    color="plasma" delay={0.10} />
            <StatRow               label="Era"      value={fingerprint.era || '—'}                                      color="ember"  delay={0.15} />
            {fingerprint.mode    && <StatRow label="Mode"     value={fingerprint.mode}                                   color="ice"    delay={0.20} />}
            {fingerprint.language && <StatRow label="Language" value={fingerprint.language}                             color="plasma" delay={0.25} />}
            {fingerprint.vocal_style && <StatRow label="Vocals" value={fingerprint.vocal_style}                         color="acid"   delay={0.30} />}
          </motion.div>

          {/* Genre tags */}
          {fingerprint.genres?.length > 0 && (
            <motion.div variants={slideUp} className="bg-surface border border-border rounded-2xl p-4 space-y-3">
              <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
                Genre Blend
              </div>
              <div className="flex flex-wrap gap-1.5">
                {fingerprint.genres.map((g, i) => (
                  <motion.span
                    key={g}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + i * 0.07, type: 'spring', stiffness: 400, damping: 20 }}
                    className="font-mono text-[10px] px-2 py-0.5 rounded-full border cursor-default"
                    style={{
                      borderColor: DNA_COLORS[i % DNA_COLORS.length] + '44',
                      color:       DNA_COLORS[i % DNA_COLORS.length] + 'cc',
                      background:  DNA_COLORS[i % DNA_COLORS.length] + '0f',
                    }}
                  >
                    {g}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Timestamp highlight */}
      {fingerprint.timestamp_highlight && (
        <motion.div
          variants={slideUp}
          className="bg-surface border border-acid/20 rounded-2xl p-4 flex items-start gap-4"
        >
          <div className="w-10 h-10 rounded-xl bg-acid/10 border border-acid/20 flex items-center justify-center flex-shrink-0">
            <motion.span
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-acid text-sm"
            >
              ◎
            </motion.span>
          </div>
          <div>
            <div className="font-mono text-[10px] text-acid/60 tracking-wider uppercase mb-1">
              Pinned Moment · {fingerprint.timestamp_highlight.time}
            </div>
            <div className="font-body text-sm text-white/70">
              {fingerprint.timestamp_highlight.description}
            </div>
          </div>
        </motion.div>
      )}

      {/* Instruments */}
      {fingerprint.instruments?.length > 0 && (
        <motion.div variants={slideUp} className="space-y-2">
          <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
            Detected Instruments
          </div>
          <div className="flex flex-wrap gap-2">
            {fingerprint.instruments.map((inst, i) => (
              <motion.span
                key={inst}
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 + i * 0.06, type: 'spring', stiffness: 350, damping: 20 }}
                whileHover={{ borderColor: '#c8f53d44', color: '#ffffffcc', scale: 1.03 }}
                className="font-mono text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 cursor-default transition-colors"
              >
                {inst}
              </motion.span>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

function StatRow({ label, value, color, delay = 0 }) {
  const colorMap = { acid: 'text-acid', plasma: 'text-plasma', ember: 'text-ember', ice: 'text-ice' }
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      className="flex justify-between items-center"
    >
      <span className="font-mono text-[10px] text-white/30 tracking-wider uppercase">{label}</span>
      <span className={`font-mono text-xs font-500 ${colorMap[color] || 'text-white/60'} text-right max-w-[130px] truncate`}>
        {value}
      </span>
    </motion.div>
  )
}

function FingerprintHash({ hash }) {
  return (
    <div className="flex-shrink-0 text-right">
      <div className="font-mono text-[10px] text-white/20 tracking-wider uppercase mb-1">ID</div>
      <div className="font-mono text-[10px] text-white/25 break-all max-w-[80px]">
        {hash?.slice(0, 8)}...
      </div>
    </div>
  )
}
