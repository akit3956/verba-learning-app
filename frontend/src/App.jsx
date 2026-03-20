import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { Home, PenTool, Wallet as WalletIcon, LogOut, LayoutDashboard } from 'lucide-react';
import Quiz from './pages/Quiz';
import MaterialGenerator from './pages/MaterialGenerator';
import Wallet from './pages/Wallet';
import Auth from './pages/Auth';
import ResetPassword from './pages/ResetPassword';
import AdminDashboard from './pages/AdminDashboard';
import './App.css';

// Simple Nav Component
function NavBar({ onLogout }) {
  const location = useLocation();
  const getLinkStyle = (path) => {
    return location.pathname === path ? 'nav-item active' : 'nav-item';
  };

  return (
    <nav className="nav-bar" style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px 24px',
      background: 'white',
      marginBottom: '20px',
      borderRadius: '16px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
    }}>
      <div style={{ display: 'flex', gap: '20px' }}>
        <Link to="/" className={getLinkStyle('/')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <Home size={20} /> JLPT Quiz
        </Link>
        <Link to="/generator" className={getLinkStyle('/generator')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <PenTool size={20} /> Teacher Tools
        </Link>
        <Link to="/wallet" className={getLinkStyle('/wallet')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <WalletIcon size={20} /> Wallet
        </Link>
        <Link to="/admin" className={getLinkStyle('/admin')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <LayoutDashboard size={20} /> Admin
        </Link>
      </div>

      <button
        onClick={onLogout}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          background: 'none',
          border: 'none',
          color: '#e53e3e',
          cursor: 'pointer',
          padding: '8px 16px',
          borderRadius: '8px',
          fontWeight: '500',
          transition: 'background 0.2s'
        }}
        className="logout-button"
      >
        <LogOut size={18} /> Logout
      </button>
    </nav>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <Router>
      <div className="container">
        {!token ? (
          <Routes>
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            <Route path="*" element={
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
                <Auth onLogin={handleLogin} />
              </div>
            } />
          </Routes>
        ) : (
          <>
            <NavBar onLogout={handleLogout} />
            <div className="content-wrapper">
              <Routes>
                <Route path="/" element={<Quiz />} />
                <Route path="/generator" element={<MaterialGenerator />} />
                <Route path="/wallet" element={<Wallet />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </>
        )}
      </div>
    </Router>
  );
}

export default App;
