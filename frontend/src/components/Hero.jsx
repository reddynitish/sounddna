export default function Hero() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-6xl font-800 leading-[1.05] tracking-tight">
        Every song has
        <br />
        <span className="text-acid-glow">a fingerprint.</span>
      </h1>
      <p className="text-white/40 font-body text-lg max-w-md leading-relaxed">
        Drop a Spotify or YouTube link. Pin a moment you loved.
        We decode its musical DNA — and find songs built from the same ingredients.
      </p>
      <div className="flex items-center gap-6 pt-2">
        <Stat label="Instrument layers" value="8 axes" />
        <div className="w-px h-8 bg-white/10" />
        <Stat label="Timestamp precision" value="To the second" />
        <div className="w-px h-8 bg-white/10" />
        <Stat label="Match logic" value="Ingredient-based" />
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div>
      <div className="font-mono text-xs text-acid/60 mb-1 tracking-wider uppercase">{label}</div>
      <div className="font-display text-sm text-white/80 font-600">{value}</div>
    </div>
  )
}
