import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Spinner from '../components/Spinner'

const INTERVALS = [
  { hours: 1,  label: '1 Saat' },
  { hours: 2,  label: '2 Saat' },
  { hours: 3,  label: '3 Saat' },
  { hours: 6,  label: '6 Saat' },
  { hours: 12, label: '12 Saat' },
]

export default function AddAccount() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [interval, setInterval] = useState(6)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = username.trim().replace(/^@/, '')
    if (!trimmed) { setError('Kullanıcı adı boş olamaz'); return }
    setLoading(true); setError(null)
    try {
      await api.addAccount(trimmed, interval)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      {/* Başlık */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(-1)}
          className="p-2 rounded-xl hover:bg-bg-purple text-txt-secondary hover:text-brand-purple transition-colors">
          ← Geri
        </button>
        <h1 className="text-2xl font-bold text-txt-primary">Hesap Ekle</h1>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Hata banner */}
        {error && (
          <div className="card p-3.5 bg-status-bgRed border border-status-red/20 flex items-center justify-between">
            <span className="text-status-red text-sm">⚠️ {error}</span>
            <button type="button" onClick={() => setError(null)} className="text-status-red text-xs ml-2">✕</button>
          </div>
        )}

        {/* Kullanıcı adı */}
        <div>
          <p className="section-label mb-2">Kullanıcı Adı</p>
          <div className="card flex items-center gap-3 px-4 py-3.5 focus-within:ring-2 ring-brand-purple/30 transition-shadow">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
              style={{ background: 'linear-gradient(135deg,#A78BFA,#F472B6)' }}>
              @
            </div>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="instagram_kullanici_adi"
              autoComplete="off"
              autoCapitalize="none"
              className="flex-1 outline-none text-sm text-txt-primary placeholder:text-txt-tertiary bg-transparent"
            />
          </div>
        </div>

        {/* Kontrol sıklığı */}
        <div>
          <p className="section-label mb-2">Kontrol Sıklığı</p>
          <div className="grid grid-cols-2 gap-2">
            {INTERVALS.map(({ hours, label }) => (
              <button
                key={hours}
                type="button"
                onClick={() => setInterval(hours)}
                className={`py-3 rounded-xl text-sm font-medium transition-all border
                  ${interval === hours
                    ? 'bg-bg-purple text-brand-purple border-brand-purple font-bold'
                    : 'bg-white text-txt-secondary border-transparent hover:border-gray-200'
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Submit */}
        <button type="submit" disabled={loading} className="btn-brand mt-2">
          {loading
            ? <><Spinner size={18} color="white" /> Ekleniyor...</>
            : '✨ Takibe Başla'
          }
        </button>
      </form>
    </div>
  )
}
