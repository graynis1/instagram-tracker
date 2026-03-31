import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import GradientAvatar from '../components/GradientAvatar'
import StatCard       from '../components/StatCard'
import Spinner        from '../components/Spinner'

function fmt(n) {
  if (!n && n !== 0) return '—'
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K'
  return String(n)
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000
  if (diff < 60)    return 'az önce'
  if (diff < 3600)  return `${Math.floor(diff / 60)} dk önce`
  if (diff < 86400) return `${Math.floor(diff / 3600)} sa önce`
  return `${Math.floor(diff / 86400)} gün önce`
}

const NOTIF_META = {
  follower_gain:        { emoji: '📈', bg: '#F0FDF4' },
  follower_loss:        { emoji: '📉', bg: '#FFF1F2' },
  following_gain:       { emoji: '➕', bg: '#F0FDF4' },
  following_loss:       { emoji: '➖', bg: '#FFF1F2' },
  new_post:             { emoji: '📸', bg: '#F0FDF4' },
  went_private:         { emoji: '🔒', bg: '#FFF1F2' },
  went_public:          { emoji: '🔓', bg: '#F0FDF4' },
  bio_change:           { emoji: '✏️', bg: '#FAF5FF' },
  new_following_person: { emoji: '👤', bg: '#FAF5FF' },
  default:              { emoji: '🔔', bg: '#FAF5FF' },
}

export default function AccountDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [account, setAccount]     = useState(null)
  const [snap, setSnap]           = useState(null)
  const [history, setHistory]     = useState([])
  const [loading, setLoading]     = useState(true)
  const [checking, setChecking]   = useState(false)
  const [error, setError]         = useState(null)
  const [checkError, setCheckError] = useState(null)

  async function load() {
    setLoading(true); setError(null)
    try {
      const [accs, snapRes, histRes] = await Promise.allSettled([
        api.getAccounts(),
        api.getSnapshot(id),
        api.getAccountHistory(id),
      ])
      if (accs.status === 'fulfilled') {
        const found = accs.value.find(a => a.id === id)
        setAccount(found || null)
      }
      if (snapRes.status === 'fulfilled') setSnap(snapRes.value)
      if (histRes.status === 'fulfilled') setHistory(histRes.value.items || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  async function handleCheckNow() {
    setChecking(true)
    setCheckError(null)
    try {
      const result = await api.checkNow(id)
      if (result.ok) {
        // Başarılı — güncel snapshot'ı çek
        const [newSnap, newHist] = await Promise.allSettled([
          api.getSnapshot(id),
          api.getAccountHistory(id),
        ])
        if (newSnap.status === 'fulfilled') setSnap(newSnap.value)
        if (newHist.status === 'fulfilled') setHistory(newHist.value.items || [])
      } else {
        setCheckError(result.details || result.error || 'Kontrol başarısız')
      }
    } catch (e) {
      setCheckError(e.name === 'AbortError' ? 'İstek zaman aşımına uğradı (25 sn)' : e.message)
    } finally {
      setChecking(false)
    }
  }

  if (loading) return <div className="flex justify-center py-16"><Spinner size={32} /></div>
  if (error)   return <div className="card p-4 text-status-red text-sm">⚠️ {error}</div>

  const username = account?.instagram_username || id

  return (
    <div className="flex flex-col gap-4">
      {/* Başlık */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)}
          className="p-2 rounded-xl hover:bg-bg-purple text-txt-secondary hover:text-brand-purple transition-colors">
          ← Geri
        </button>
        <h1 className="text-xl font-bold text-txt-primary flex-1">@{username}</h1>
        <button
          onClick={handleCheckNow}
          disabled={checking}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold text-brand-purple bg-bg-purple hover:bg-brand-purple hover:text-white transition-all disabled:opacity-60"
        >
          {checking ? <Spinner size={14} /> : '🔄'}
          {checking ? 'Kontrol ediliyor...' : 'Şimdi Kontrol Et'}
        </button>
      </div>

      {/* Kontrol hatası */}
      {checkError && (
        <div className="card p-3.5 bg-status-bgRed border border-status-red/20 flex items-center justify-between">
          <span className="text-status-red text-sm">⚠️ {checkError}</span>
          <button onClick={() => setCheckError(null)} className="text-status-red text-xs ml-2">✕</button>
        </div>
      )}

      {/* Profil kartı */}
      <div className="card p-5 flex gap-4">
        <GradientAvatar username={username} fullName={snap?.full_name} size={56} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            {snap?.full_name && (
              <span className="font-bold text-txt-primary">{snap.full_name}</span>
            )}
            {snap?.is_verified && <span className="text-brand-purple text-sm">✔ Doğrulanmış</span>}
            {snap?.is_private
              ? <span className="pill-red">🔒 Gizli</span>
              : <span className="pill-green">🌐 Herkese Açık</span>
            }
          </div>
          <p className="text-brand-purple text-sm mt-0.5">@{username}</p>
          {snap?.biography && (
            <p className="text-txt-secondary text-sm mt-2 leading-relaxed">{snap.biography}</p>
          )}
          {snap?.external_url && (
            <a href={snap.external_url} target="_blank" rel="noopener noreferrer"
              className="text-brand-purple text-sm mt-1 block hover:underline truncate">
              🔗 {snap.external_url}
            </a>
          )}
          {snap?.snapshotted_at && (
            <p className="text-txt-tertiary text-xs mt-2">Son güncelleme: {timeAgo(snap.snapshotted_at)}</p>
          )}
        </div>
      </div>

      {/* İstatistik */}
      {snap ? (
        <div className="card p-4">
          <p className="section-label mb-3">İstatistikler</p>
          <div className="flex gap-2">
            <StatCard label="Takipçi" value={snap.followers_count} />
            <StatCard label="Takip"   value={snap.following_count} />
            <StatCard label="Gönderi" value={snap.posts_count} />
          </div>
        </div>
      ) : (
        <div className="card p-4 text-center text-txt-secondary text-sm">
          Henüz snapshot yok. "Şimdi Kontrol Et" butonuna tıkla.
        </div>
      )}

      {/* Değişim geçmişi */}
      <div className="card p-4">
        <p className="section-label mb-3">Son Değişiklikler</p>
        {history.length === 0 ? (
          <p className="text-txt-secondary text-sm text-center py-6">Henüz değişiklik kaydı yok</p>
        ) : (
          <div className="flex flex-col divide-y divide-black/[0.04]">
            {history.map(entry => {
              const meta = NOTIF_META[entry.notification.notification_type] || NOTIF_META.default
              return (
                <div key={entry.notification.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center text-lg flex-shrink-0"
                    style={{ background: meta.bg }}>
                    {meta.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-txt-primary leading-snug">{entry.notification.message}</p>
                    <p className="text-xs text-txt-tertiary mt-0.5">{timeAgo(entry.notification.sent_at)}</p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
