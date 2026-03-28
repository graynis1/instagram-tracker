function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K'
  return String(n)
}

export default function StatCard({ label, value, change }) {
  return (
    <div className="flex-1 bg-bg-page rounded-xl py-3 flex flex-col items-center gap-1">
      <span className="text-xl font-bold text-txt-primary">{fmt(value)}</span>
      <span className="text-[10px] font-semibold text-txt-secondary uppercase tracking-wide">{label}</span>
      {change !== undefined && change !== 0 && (
        <span className={change > 0 ? 'pill-green' : 'pill-red'}>
          {change > 0 ? '+' : ''}{change}
        </span>
      )}
    </div>
  )
}
