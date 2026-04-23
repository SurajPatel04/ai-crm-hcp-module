import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logoutUser } from './features/auth/authSlice';

// Route guards
import PrivateRoute from './components/PrivateRoute';
import PublicRoute from './components/PublicRoute';

// Auth screens
import Login from './features/auth/Login';
import SignUp from './features/auth/SignUp';

// Protected screens
import LogInteractionScreen from './features/interactions/LogInteractionScreen';
import InteractionList from './features/interactions/InteractionList';
import EditInteraction from './features/interactions/EditInteraction';

// ─── Navbar (only shown when authenticated) ───────────────────────────────────
const Navigation = () => {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);

  if (!isAuthenticated) return null;

  return (
    <nav className="navbar">
      <div style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-primary)' }}>
        HCP CRM
      </div>
      <div className="nav-links">
        <Link to="/log-interaction">Log Interaction</Link>
        <Link to="/interactions">History</Link>
        <button
          onClick={() => dispatch(logoutUser())}
          style={{ color: 'var(--text-secondary)', fontWeight: 500 }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />

        <main className="main-content">
          <Routes>

            {/* ── Public routes — redirect to /log-interaction if already logged in ── */}
            <Route element={<PublicRoute />}>
              <Route path="/login"  element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
            </Route>

            {/* ── Protected routes — redirect to /login if not logged in ── */}
            <Route element={<PrivateRoute />}>
              <Route path="/log-interaction"       element={<LogInteractionScreen />} />
              <Route path="/interactions"           element={<InteractionList />} />
              <Route path="/interactions/:id/edit" element={<EditInteraction />} />
            </Route>

            {/* ── Default: send to /login if nothing matches ── */}
            <Route path="*" element={<Navigate to="/login" replace />} />

          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
