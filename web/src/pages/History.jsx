import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import Spinner    from '../components/Spinner'
import EmptyState from '../components/EmptyState'

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

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000
  if (diff < 60)    return 'az önce'
  if (diff < 3600)  return `${Math.floor(diff / 60)} dk`
  if (diff < 86400) return `${Math.floor(diff / 3600)} sa`
  return `${Math.floor(diff / 86400)} gün`
}

function isToday(dateStr) {
  const d = new Date(dateStr)
  const now = new Date()
  return d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
}

export default function History() {
  const [entries, setEntries]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError]       = useState(null)
  const [page, setPage]         = useState(1)
  const [hasMore, setHasMore]   = useState(false)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await api.getHistory(1)
      setEntries(res.items || [])
      setHasMore(res.has_more)
      setPage(1)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  async function loadMore() {
    setLoadingMore(true)
    try {
      const nextPage = page + 1
      const res = await api.getHistory(nextPage)
      setEntries(prev => [...prev, ...(res.items || [])])
      setHasMore(res.has_more)
      setPage(nextPage)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoadingMore(false)
    }
  }

  useEffect(() => { load() }, [load])

  const todayCount = entries.filter(e => isToday(e.notification.sent_at)).length

  return (
    <div>
      {/* Başlık */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-txt-primary">Bildirimler</h1>
          {!loading && entries.length > 0 && (
            <p className="text-xs text-txt-secondary mt-0.5">Bugün {todayCount} yeni bildirim</p>
          )}
        </div>
        <button onClick={load}
          className="p-2 rounded-xl hover:bg-bg-purple text-txt-secondary hover:text-brand-purple transition-colors"
          title="Yenile">
          🔄
        </button>
      </div>

      {/* İçerik */}
      {loading && <div className="flex justify-center py-16"><Spinner size={32} /></div>}

      {!loading && error && (
        <div className="card p-4 bg-status-bgRed border border-status-red/20">
          <p className="text-status-red text-sm">⚠️ {error}</p>
          <button onClick={load} className="text-status-red text-xs underline mt-1">Tekrar dene</button>
        </div>
      )}

      {!loading && !error && entries.length === 0 && (
        <EmptyState
          emoji="🔔"
          title="Henüz bildirim yok"
          desc="Takip ettiğin hesaplarda bir değişiklik olduğunda burada görünecek"
        />
      )}

      {!loading && !error && entries.length > 0 && (
        <div className="flex flex-col gap-2.5">
          {entries.map(entry => {
            const meta = NOTIF_META[entry.notification.notification_type] || NOTIF_META.default
            return (
              <div key={entry.notification.id}
                className="card overflow-hidden flex"
              >
                {/* Sol gradient çizgi */}
                <div className="w-1 flex-shrink-0"
                  style={{ background: 'linear-gradient(180deg,#A78BFA,#F472B6)' }} />

                <div className="flex items-start gap-3 p-3.5 flex-1">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center text-lg flex-shrink-0"
                    style={{ background: meta.bg }}>
                    {meta.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-brand-purple truncate">@{entry.account_username}</p>
                    <p className="text-sm text-txt-primary leading-snug mt-0.5">{entry.notification.message}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <span className="text-[10px] text-txt-tertiary">{timeAgo(entry.notification.sent_at)}</span>
                    {entry.notification.was_delivered
                      ? <span className="text-[9px] text-status-green">✓ İletildi</span>
                      : <span className="text-[9px] text-txt-tertiary">—</span>
                    }
                  </div>
                </div>
              </div>
            )
          })}

          {/* Daha fazla yükle */}
          {hasMore && (
            <button
              onClick={loadMore}
              disabled={loadingMore}
              className="btn-brand mt-2"
            >
              {loadingMore
                ? <><Spinner size={18} color="white" /> Yükleniyor...</>
                : 'Daha Fazla Göster'
              }
            </button>
          )}
        </div>
      )}
    </div>
  )
}
