import { Outlet, Link, useNavigate } from 'react-router-dom'
import { isAuthenticated, logout } from './api/auth'

export default function App() {
  const navigate = useNavigate()
  const authed = isAuthenticated()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/dashboard" className="brand">
          Darukaa.Earth
        </Link>
        {authed && (
          <button onClick={handleLogout} className="btn-link">
            Log out
          </button>
        )}
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
