import { NavLink, useNavigate } from 'react-router-dom'
import { BoxIcon, HomeIcon, LogoutIcon, SwapIcon } from './icons'

const NAV_ITEMS = [
  { to: '/', label: 'Ana Sayfa', end: true, icon: HomeIcon },
  { to: '/hareketler', label: 'Stok Hareketleri', icon: SwapIcon },
]

export default function Sidebar() {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-title">
        <div className="sidebar-logo"><BoxIcon width={20} height={20} /></div>
        <div>
          <div className="sidebar-title-main">Envanter Sistemi</div>
          <div className="sidebar-title-sub">Erdemir ERP Staj Projesi</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon />
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      <button className="sidebar-logout" onClick={handleLogout}>
        <LogoutIcon />
        Çıkış Yap
      </button>
    </aside>
  )
}
