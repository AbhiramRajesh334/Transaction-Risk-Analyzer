// App.jsx - Main application wrapper
import React, { useState } from 'react';
import TopNav from './components/layout/TopNav';
import HomePage from './pages/HomePage';
import InvestigationDashboard from './pages/InvestigationDashboard';
import './styles/InvestigationDashboard.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <div className="app-shell">
      <TopNav currentPage={currentPage} onNavigate={setCurrentPage} />
      {currentPage === 'home' && <HomePage onNavigate={() => setCurrentPage('network')} />}
      {currentPage === 'network' && <InvestigationDashboard onBack={() => setCurrentPage('home')} />}
    </div>
  );
}
