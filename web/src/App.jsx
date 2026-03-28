import { Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom'
import AccountsList  from './pages/AccountsList'
import AddAccount    from './pages/AddAccount'
import AccountDetail from './pages/AccountDetail'
import History       from './pages/History'

function Navbar() {
  const tabs = [
    { to: '/',        label: 'Hesaplar',   icon: '👥' },
    { to: '/history', label: 'Bildirimler', icon: '🔔' },
  ]
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-black/[0.06] shadow-sm">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold bg-brand bg-clip-text text-transparent">
            Instagram Tracker
          </span>
        </div>
        {/* Tabs */}
        <div className="flex gap-1">
          {tabs.map(t => (
            <NavLink
              key={t.to}
              to={t.to}
              end={t.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-sm font-medium transition-all
                 ${isActive
                   ? 'bg-bg-purple text-brand-purple'
                   : 'text-txt-secondary hover:text-txt-primary hover:bg-bg-page'}`
              }
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-bg-page">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/"              element={<AccountsList />} />
          <Route path="/add"           element={<AddAccount />} />
          <Route path="/account/:id"   element={<AccountDetail />} />
          <Route path="/history"       element={<History />} />
        </Routes>
      </main>
    </div>
  )
}
