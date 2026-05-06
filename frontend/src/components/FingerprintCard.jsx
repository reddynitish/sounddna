import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts'

const AXIS_LABELS = {
  energy: 'Energy',
  danceability: 'Dance',
  instrumentalness: 'Instrumental',
  acousticness: 'Acoustic',
  valence: 'Positivity',
  speechiness: 'Vocal',
  tempo_norm: 'Tempo',
  liveness: 'Live Feel',
}

const DNA_COLORS = ['#c8f53d', '#7b61ff', '#ff6b35', '#38bdf8', '#ff6b35', '#c8f53d']

export default function FingerprintCard({ fingerprint, song }) {
  const radarData = Object.entries(AXIS_LABELS).map(([key, label]) => ({
    axis: label,
    value: Math.round((fingerprint.audio_features?.[key] ?? 0) * 100),
    fullMark: 100,
  }))

  return (
    <div className="space-y-6">
      {/* Song identity row */}
      <div className="flex items-start gap-4">
        {song?.image && (
          <img
            src={song.image}
            alt={song.title}
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
      </div>

      {/* Main grid: radar + tags */}
      <div className="grid grid-cols-5 gap-4">
        {/* Radar */}
        <div className="col-span-3 bg-surface border border-border rounded-2xl p-4 animated-border">
          <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase mb-4">
            Audio Profile
          </div>
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
              />
              <Tooltip
                contentStyle={{
                  background: '#1a1a2e',
                  border: '1px solid #ffffff0f',
                  borderRadius: '8px',
                  fontFamily: 'JetBrains Mono',
                  fontSize: '11px',
                  color: '#c8f53d',
                }}
                formatter={(v) => [`${v}/100`, '']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Right panel: ingredients */}
        <div className="col-span-2 space-y-3">
          {/* Key stats */}
          <div className="bg-surface border border-border rounded-2xl p-4 space-y-3">
            <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
              Core Ingredients
            </div>
            <StatRow label="Key" value={fingerprint.key || '—'} color="acid" />
            <StatRow label="BPM" value={fingerprint.tempo ? Math.round(fingerprint.tempo) : '—'} color="plasma" />
            <StatRow label="Era" value={fingerprint.era || '—'} color="ember" />
            <StatRow label="Mode" value={fingerprint.mode || '—'} color="ice" />
          </div>

          {/* Genre tags */}
          {fingerprint.genres?.length > 0 && (
            <div className="bg-surface border border-border rounded-2xl p-4 space-y-3">
              <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
                Genre Blend
              </div>
              <div className="flex flex-wrap gap-1.5">
                {fingerprint.genres.map((g, i) => (
                  <span
                    key={g}
                    className="font-mono text-[10px] px-2 py-0.5 rounded-full border"
                    style={{
                      borderColor: DNA_COLORS[i % DNA_COLORS.length] + '44',
                      color: DNA_COLORS[i % DNA_COLORS.length] + 'cc',
                      background: DNA_COLORS[i % DNA_COLORS.length] + '0f',
                    }}
                  >
                    {g}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Timestamp highlight */}
      {fingerprint.timestamp_highlight && (
        <div className="bg-surface border border-acid/20 rounded-2xl p-4 flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-acid/10 border border-acid/20 flex items-center justify-center flex-shrink-0">
            <span className="text-acid text-sm">◎</span>
          </div>
          <div>
            <div className="font-mono text-[10px] text-acid/60 tracking-wider uppercase mb-1">
              Pinned Moment · {fingerprint.timestamp_highlight.time}
            </div>
            <div className="font-body text-sm text-white/70">
              {fingerprint.timestamp_highlight.description}
            </div>
          </div>
        </div>
      )}

      {/* Instrument tags */}
      {fingerprint.instruments?.length > 0 && (
        <div className="space-y-2">
          <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
            Detected Instruments
          </div>
          <div className="flex flex-wrap gap-2">
            {fingerprint.instruments.map(inst => (
              <span
                key={inst}
                className="font-mono text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 hover:border-acid/30 hover:text-white/70 transition-colors"
              >
                {inst}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatRow({ label, value, color }) {
  const colorMap = {
    acid: 'text-acid',
    plasma: 'text-plasma',
    ember: 'text-ember',
    ice: 'text-ice',
  }
  return (
    <div className="flex justify-between items-center">
      <span className="font-mono text-[10px] text-white/30 tracking-wider uppercase">{label}</span>
      <span className={`font-mono text-xs font-500 ${colorMap[color]}`}>{value}</span>
    </div>
  )
}

function FingerprintHash({ hash }) {
  return (
    <div className="flex-shrink-0 text-right">
      <div className="font-mono text-[10px] text-white/20 tracking-wider uppercase mb-1">ID</div>
      <div className="font-mono text-[10px] text-white/30 break-all max-w-[80px]">
        {hash?.slice(0, 8)}...
      </div>
    </div>
  )
}
