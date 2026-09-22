import { useAuth } from '../auth/AuthContext'
import type { Tab } from '../App'

interface Props {
  tab: Tab
  onTabChange: (tab: Tab) => void
  onAuthOpen: () => void
}

export default function Navbar({ tab, onTabChange, onAuthOpen }: Props) {
  const { user, logout } = useAuth()

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <button type="button" className="navbar-brand" onClick={() => onTabChange('cars')}>
          <span className="navbar-logo" aria-hidden="true">
            <svg viewBox="0 0 32 20" width="28" height="18">
              <path
                d="M2,17 L2,13 Q2,10 5,10 L8,10 L12,4 Q14,1 18,1 L22,1 Q26,1 28,4 L30,10 Q30,17 27,17 Z"
                fill="currentColor"
              />
              <circle cx="9" cy="17" r="2.6" fill="#0b0b0d" stroke="currentColor" strokeWidth="1.4" />
              <circle cx="23" cy="17" r="2.6" fill="#0b0b0d" stroke="currentColor" strokeWidth="1.4" />
            </svg>
          </span>
          CarRental<span className="navbar-brand-accent">VSB</span>
        </button>

        <nav className="navbar-tabs">
          <button
            type="button"
            className={tab === 'cars' ? 'active' : ''}
            onClick={() => onTabChange('cars')}
          >
            Vozový park
          </button>
          {user && (
            <button
              type="button"
              className={tab === 'my-reservations' ? 'active' : ''}
              onClick={() => onTabChange('my-reservations')}
            >
              Moje rezervace
            </button>
          )}
          {user?.role === 'ADMIN' && (
            <>
              <button
                type="button"
                className={tab === 'admin-cars' ? 'active' : ''}
                onClick={() => onTabChange('admin-cars')}
              >
                Administrace aut
              </button>
              <button
                type="button"
                className={tab === 'admin-reservations' ? 'active' : ''}
                onClick={() => onTabChange('admin-reservations')}
              >
                Všechny rezervace
              </button>
            </>
          )}
        </nav>

        <div className="navbar-user">
          {user ? (
            <>
              <span className="navbar-username">
                {user.name}
                {user.role === 'ADMIN' && <span className="role-badge">Admin</span>}
              </span>
              <button type="button" className="secondary" onClick={logout}>
                Odhlásit
              </button>
            </>
          ) : (
            <button type="button" onClick={onAuthOpen}>
              Přihlásit se
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
