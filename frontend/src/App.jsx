import API_BASE_URL from "./api_config";
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { Home, PenTool, Wallet as WalletIcon, LogOut, LayoutDashboard, MessageCircle } from 'lucide-react';
import Quiz from './pages/Quiz';
import MaterialGenerator from './pages/MaterialGenerator';
import Wallet from './pages/Wallet';
import Auth from './pages/Auth';
import ResetPassword from './pages/ResetPassword';
import AdminDashboard from './pages/AdminDashboard';
import Tutor from './pages/Tutor';
import Landing from './pages/Landing';
import Inquiry from './pages/Inquiry';
import './App.css';

// Simple Nav Component
function NavBar({ onLogout, userPlan, usage }) {
  const location = useLocation();
  const getLinkStyle = (path) => {
    return location.pathname === path ? 'nav-item active' : 'nav-item';
  };

  const isStandard = userPlan?.toLowerCase() === 'standard';

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
        {!isStandard && (
          <Link to="/generator" className={getLinkStyle('/generator')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
            <PenTool size={20} /> Teacher Tools
          </Link>
        )}
        {!isStandard && (
          <Link to="/tutor" className={getLinkStyle('/tutor')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
            <MessageCircle size={20} /> AI Tutor
          </Link>
        )}
        <Link to="/wallet" className={getLinkStyle('/wallet')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <WalletIcon size={20} /> Wallet
        </Link>
        {!isStandard && (
          <Link to="/admin" className={getLinkStyle('/admin')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
            <LayoutDashboard size={20} /> Admin
          </Link>
        )}
        <Link to="/inquiry" className={getLinkStyle('/inquiry')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
          <MessageCircle size={20} /> Contact
        </Link>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        {usage && userPlan === 'standard' && (
          <div style={{ fontSize: '12px', color: '#718096', fontWeight: 'bold' }}>
            Daily Rounds: {usage.count} / {usage.limit}
          </div>
        )}
        <span style={{ fontSize: '12px', color: '#a0aec0', background: '#f8fafc', padding: '4px 8px', borderRadius: '4px' }}>
          Plan: {userPlan}
        </span>
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
      </div>
    </nav>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userPlan, setUserPlan] = useState('standard');
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) return;
      try {
        const res = await fetch(API_BASE_URL + '/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUserPlan(data.plan_type || 'standard');
        }
      } catch (err) {
        console.error("Failed to fetch plan:", err);
      }
    };
    const fetchUsage = async () => {
      if (!token) return;
      try {
        const res = await fetch(API_BASE_URL + '/auth/usage', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setUsage(data);
        }
      } catch (err) {
        console.error("Failed to fetch usage:", err);
      }
    };
    fetchUser();
    fetchUsage();
    
    // Refresh usage occasionally
    const interval = setInterval(fetchUsage, 60000); 
    return () => clearInterval(interval);
  }, [token]);

  const handleLogin = (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUserPlan('standard');
  };

  return (
    <Router>
      {!token ? (
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/inquiry" element={<Inquiry />} />
          <Route path="/auth" element={
            <div className="min-h-screen bg-[#0f172a] flex justify-center items-center p-6 relative overflow-hidden">
              <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/10 blur-[120px] rounded-full"></div>
              <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full"></div>
              <div className="relative z-10 w-full max-w-md">
                <Auth onLogin={handleLogin} />
              </div>
            </div>
          } />
          <Route path="/reset-password/:token" element={<ResetPassword />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      ) : (
        <div className="container">
          <NavBar onLogout={handleLogout} userPlan={userPlan} usage={usage} />
          <div className="content-wrapper">
            <Routes>
              <Route path="/" element={<Quiz userPlan={userPlan} />} />
              <Route path="/generator" element={<MaterialGenerator userPlan={userPlan} />} />
              <Route path="/wallet" element={<Wallet />} />
              <Route path="/tutor" element={<Tutor userPlan={userPlan} />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      )}
    </Router>
  );
}

export default App;
