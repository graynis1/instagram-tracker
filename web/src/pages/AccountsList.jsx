import { useState, useEffect, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../api'
import GradientAvatar from '../components/GradientAvatar'
import Spinner        from '../components/Spinner'
import EmptyState     from '../components/EmptyState'

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

function AccountCard({ account, onDelete }) {
  const navigate = useNavigate()
  const snap = account.latest_snapshot
  const [deleting, setDeleting] = useState(false)

  async function handleDelete(e) {
    e.stopPropagation()
    if (!confirm(`@${account.instagram_username} takip listesinden kaldırılsın mı?`)) return
    setDeleting(true)
    try { await api.deleteAccount(account.id); onDelete(account.id) }
    catch (err) { alert(err.message); setDeleting(false) }
  }

  return (
    <div
      className="card p-4 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => navigate(`/account/${account.id}`)}
    >
      {/* Üst satır */}
      <div className="flex items-center gap-3 mb-3">
        <GradientAvatar username={account.instagram_username} fullName={snap?.full_name} size={42} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-sm text-txt-primary truncate">
              @{account.instagram_username}
            </span>
            {snap?.is_verified && <span className="text-brand-purple text-xs">✔</span>}
          </div>
          <span className="text-xs text-txt-tertiary">
            {snap ? timeAgo(snap.snapshotted_at) : 'henüz kontrol edilmedi'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {account.is_active
            ? <span className="pill-green">Aktif</span>
            : <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-gray-100 text-txt-secondary">Pasif</span>
          }
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="text-status-red hover:bg-status-bgRed p-1.5 rounded-lg transition-colors text-xs disabled:opacity-50"
          >
            {deleting ? <Spinner size={14} color="#BE123C" /> : '🗑'}
          </button>
        </div>
      </div>

      {/* Ayırıcı */}
      <div className="border-t border-black/[0.05] mb-3" />

      {/* İstatistik satırı */}
      <div className="flex gap-2">
        {[
          { label: 'TAKİPÇİ', val: snap?.followers_count },
          { label: 'TAKİP',   val: snap?.following_count },
          { label: 'GÖNDERİ', val: snap?.posts_count },
        ].map(s => (
          <div key={s.label} className="flex-1 bg-bg-page rounded-xl py-2.5 flex flex-col items-center gap-0.5">
            <span className="text-sm font-bold text-txt-primary">{fmt(s.val)}</span>
            <span className="text-[9px] font-semibold text-txt-secondary tracking-wide">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function AccountsList() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [apiStatus, setApiStatus] = useState(null)
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const [accs, health] = await Promise.allSettled([api.getAccounts(), api.health()])
      if (accs.status === 'fulfilled') setAccounts(accs.value)
      else throw accs.reason
      setApiStatus(health.status === 'fulfilled' ? 'ok' : 'error')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <div>
      {/* Başlık */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-txt-primary">Takip Listesi</h1>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className={`w-1.5 h-1.5 rounded-full ${apiStatus === 'ok' ? 'bg-status-green' : apiStatus === 'error' ? 'bg-status-red' : 'bg-gray-300'}`} />
            <span className="text-xs text-txt-secondary">
              {apiStatus === 'ok' ? 'API bağlı' : apiStatus === 'error' ? 'API bağlantı hatası' : 'kontrol ediliyor...'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className="p-2 rounded-xl hover:bg-bg-purple text-txt-secondary hover:text-brand-purple transition-colors"
            title="Yenile"
          >
            🔄
          </button>
          <Link to="/add">
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-white font-semibold text-sm"
              style={{ background: 'linear-gradient(135deg,#A78BFA,#F472B6)' }}>
              <span className="text-base leading-none">+</span>
              Hesap Ekle
            </button>
          </Link>
        </div>
      </div>

      {/* İçerik */}
      {loading && (
        <div className="flex justify-center py-16"><Spinner size={32} /></div>
      )}
      {!loading && error && (
        <div className="card p-4 bg-status-bgRed border-status-red/20">
          <p className="text-status-red text-sm font-medium">⚠️ {error}</p>
          <button onClick={load} className="text-status-red text-xs underline mt-1">Tekrar dene</button>
        </div>
      )}
      {!loading && !error && accounts.length === 0 && (
        <EmptyState
          emoji="👥"
          title="Henüz hesap eklenmedi"
          desc="Takip etmek istediğin Instagram hesabını eklemek için 'Hesap Ekle' butonuna tıkla"
        />
      )}
      {!loading && !error && accounts.length > 0 && (
        <div className="flex flex-col gap-3">
          {accounts.map(acc => (
            <AccountCard
              key={acc.id}
              account={acc}
              onDelete={id => setAccounts(prev => prev.filter(a => a.id !== id))}
            />
          ))}
        </div>
      )}
    </div>
  )
}
