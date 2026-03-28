const GRADIENTS = [
  'linear-gradient(135deg,#A78BFA,#7C3AED)',
  'linear-gradient(135deg,#F472B6,#BE185D)',
  'linear-gradient(135deg,#67E8F9,#2563EB)',
  'linear-gradient(135deg,#A78BFA,#F472B6)',
]

function initials(username, fullName) {
  if (fullName) {
    const parts = fullName.trim().split(' ')
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
    return fullName.slice(0, 2).toUpperCase()
  }
  return username.slice(0, 2).toUpperCase()
}

function hashIndex(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) & 0xffffffff
  return Math.abs(h) % GRADIENTS.length
}

export default function GradientAvatar({ username, fullName, size = 38 }) {
  const bg = GRADIENTS[hashIndex(username)]
  const fontSize = Math.round(size * 0.35)
  return (
    <div
      style={{ width: size, height: size, background: bg, fontSize, flexShrink: 0 }}
      className="rounded-full flex items-center justify-center text-white font-bold select-none"
    >
      {initials(username, fullName)}
    </div>
  )
}
