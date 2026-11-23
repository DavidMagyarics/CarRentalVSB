import type { ReactNode } from 'react';
import { Navigate, NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import type { Role } from './api/client';
import { SupportWidget } from './components/SupportWidget';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import { CarsPage } from './pages/CarsPage';
import { FleetPage } from './pages/FleetPage';
import { AllReservationsPage, MyReservationsPage } from './pages/ReservationsPages';
import { useAuth } from './state/auth';

function RequireRole({ role, children }: { role?: Role; children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="muted">Načítám…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const link = ({ isActive }: { isActive: boolean }) => (isActive ? 'active' : undefined);

  return (
    <header className="topbar">
      <NavLink to="/" className="brand">
        <span className="brand-mark" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 11l1.6-4.2A2 2 0 0 1 8.5 5.5h7a2 2 0 0 1 1.9 1.3L19 11h.5A1.5 1.5 0 0 1 21 12.5V17h-2a2 2 0 0 1-4 0H9a2 2 0 0 1-4 0H3v-4.5A1.5 1.5 0 0 1 4.5 11H5zm2.2 0h9.6l-1.2-3.3a.5.5 0 0 0-.5-.2H8.9a.5.5 0 0 0-.5.2L7.2 11z" />
          </svg>
        </span>
        <span className="brand-name">
          CarRental<span>VSB</span>
        </span>
      </NavLink>
      <nav>
        <NavLink to="/" end className={link}>
          Auta
        </NavLink>
        {/* u.role decides which tabs are shown */}
        {user?.role === 'CUSTOMER' && (
          <NavLink to="/my-reservations" className={link}>
            Moje rezervace
          </NavLink>
        )}
        {user?.role === 'ADMIN' && (
          <>
            <NavLink to="/admin/reservations" className={link}>
              Všechny rezervace
            </NavLink>
            <NavLink to="/admin/fleet" className={link}>
              Vozový park
            </NavLink>
          </>
        )}
      </nav>
      <div className="user-box">
        {user ? (
          <>
            <span className="muted small">
              {user.name} {user.role === 'ADMIN' && '(admin)'}
            </span>
            <button
              className="secondary"
              onClick={() => {
                logout();
                navigate('/');
              }}
            >
              Odhlásit
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={link}>
              Přihlásit
            </NavLink>
            <NavLink to="/register" className={link}>
              Vytvořit účet
            </NavLink>
          </>
        )}
      </div>
    </header>
  );
}

export default function App() {
  return (
    <>
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<CarsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/my-reservations"
            element={
              <RequireRole>
                <MyReservationsPage />
              </RequireRole>
            }
          />
          <Route
            path="/admin/reservations"
            element={
              <RequireRole role="ADMIN">
                <AllReservationsPage />
              </RequireRole>
            }
          />
          <Route
            path="/admin/fleet"
            element={
              <RequireRole role="ADMIN">
                <FleetPage />
              </RequireRole>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <SupportWidget />
    </>
  );
}
