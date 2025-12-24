import React, { useState } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Home, Upload, LogOut } from 'lucide-react';
import Login from './components/Login';
import Feed from './components/Feed';
import UploadPage from './components/UploadPage';

export default function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = (userData, token) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <h3 style={{ marginBottom: '30px' }}>👋 Hi {user.email.split('@')[0]}!</h3>
        <nav>
          <div className={`nav-link ${location.pathname === '/' ? 'active' : ''}`} onClick={() => navigate('/')} style={{cursor: 'pointer'}}>
            <Home size={20} /> Feed
          </div>
          <div className={`nav-link ${location.pathname === '/upload' ? 'active' : ''}`} onClick={() => navigate('/upload')} style={{cursor: 'pointer'}}>
            <Upload size={20} /> Upload
          </div>
        </nav>
        <div className="sidebar-footer">
          <button className="nav-link logout-button" onClick={handleLogout}>
            <LogOut size={20} /> Logout
          </button>
        </div>
      </div>
      
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Feed user={user} />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  );
}