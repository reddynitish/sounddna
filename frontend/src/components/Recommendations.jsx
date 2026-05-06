const MATCH_COLORS = ['#c8f53d', '#7b61ff', '#38bdf8', '#ff6b35', '#c8f53d']

export default function Recommendations({ recommendations }) {
  if (!recommendations?.length) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="font-mono text-[10px] text-white/30 tracking-wider uppercase">
          Ingredient Matches
        </div>
        <div className="flex-1 h-px bg-white/5" />
        <div className="font-mono text-[10px] text-white/20">
          {recommendations.length} found
        </div>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, i) => (
          <RecommendationRow key={rec.id || i} rec={rec} rank={i + 1} color={MATCH_COLORS[i % MATCH_COLORS.length]} />
        ))}
      </div>
    </div>
  )
}

function RecommendationRow({ rec, rank, color }) {
  const matchPct = Math.round(rec.match_score * 100)

  return (
    <a
      href={rec.external_url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-4 p-4 bg-surface border border-border rounded-2xl hover:border-white/20 card-hover group block transition-all duration-200"
    >
      {/* Rank */}
      <div className="w-6 text-center font-mono text-xs text-white/20 flex-shrink-0">
        {rank}
      </div>

      {/* Album art */}
      {rec.image ? (
        <img src={rec.image} alt={rec.title} className="w-12 h-12 rounded-xl object-cover ring-1 ring-white/10 flex-shrink-0" />
      ) : (
        <div className="w-12 h-12 rounded-xl bg-panel flex items-center justify-center flex-shrink-0">
          <span className="text-white/20 text-lg">♪</span>
        </div>
      )}

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="font-display text-sm font-600 text-white/90 truncate group-hover:text-white transition-colors">
          {rec.title}
        </div>
        <div className="font-body text-xs text-white/40 truncate mt-0.5">
          {rec.artist}
        </div>

        {/* Matching ingredients */}
        {rec.matching_ingredients?.length > 0 && (
          <div className="flex gap-1.5 mt-2 flex-wrap">
            {rec.matching_ingredients.slice(0, 4).map(ing => (
              <span
                key={ing}
                className="font-mono text-[10px] px-1.5 py-0.5 rounded-md"
                style={{
                  background: color + '12',
                  color: color + 'aa',
                  border: `1px solid ${color}22`,
                }}
              >
                {ing}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Match score */}
      <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
        <div className="font-display text-sm font-700" style={{ color }}>
          {matchPct}%
        </div>
        <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${matchPct}%`, background: color }}
          />
        </div>
        <div className="font-mono text-[10px] text-white/20">match</div>
      </div>
    </a>
  )
}
