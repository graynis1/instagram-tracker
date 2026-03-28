export default function EmptyState({ emoji, title, desc }) {
  return (
    <div className="flex flex-col items-center py-16 gap-4">
      <div
        className="w-16 h-16 rounded-full flex items-center justify-center text-2xl"
        style={{ background: 'linear-gradient(135deg,#A78BFA,#F472B6)' }}
      >
        {emoji}
      </div>
      <p className="text-txt-primary font-bold text-base">{title}</p>
      <p className="text-txt-secondary text-sm text-center max-w-xs">{desc}</p>
    </div>
  )
}
