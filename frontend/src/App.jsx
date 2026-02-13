import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, PenTool, Wallet as WalletIcon } from 'lucide-react';
import Quiz from './pages/Quiz';
import MaterialGenerator from './pages/MaterialGenerator';
import Wallet from './pages/Wallet';
import './App.css';

// Simple Nav Component
function NavBar() {
  const location = useLocation();
  const getLinkStyle = (path) => {
    return location.pathname === path ? 'nav-item active' : 'nav-item';
  };

  return (
    <nav className="nav-bar" style={{
      display: 'flex',
      justifyContent: 'center',
      gap: '20px',
      padding: '20px',
      background: 'white',
      marginBottom: '20px',
      borderRadius: '16px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
    }}>
      <Link to="/" className={getLinkStyle('/')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
        <Home size={20} /> JLPT Quiz
      </Link>
      <Link to="/generator" className={getLinkStyle('/generator')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
        <PenTool size={20} /> Teacher Tools
      </Link>
      <Link to="/wallet" className={getLinkStyle('/wallet')} style={{ textDecoration: 'none', color: '#4a5568', display: 'flex', alignItems: 'center', gap: 5, padding: '8px 16px', borderRadius: 8 }}>
        <WalletIcon size={20} /> Wallet
      </Link>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="container">
        <NavBar />
        <div className="content-wrapper">
          <Routes>
            <Route path="/" element={<Quiz />} />
            <Route path="/generator" element={<MaterialGenerator />} />
            <Route path="/wallet" element={<Wallet />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
