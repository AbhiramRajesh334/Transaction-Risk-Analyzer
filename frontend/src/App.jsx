// App.jsx - Main application wrapper
import React, { useState } from 'react';
import TopNav from './components/layout/TopNav';
import HomePage from './pages/HomePage';
import InvestigationDashboard from './pages/InvestigationDashboard';
import TimelinePage from './pages/TimelinePage';
import './styles/InvestigationDashboard.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  };

  return (
    <div className={`app-shell ${isDarkMode ? 'dark-mode' : ''}`}>
      <TopNav 
        currentPage={currentPage} 
        onNavigate={setCurrentPage} 
        isDarkMode={isDarkMode} 
        toggleDarkMode={toggleDarkMode} 
      />
      {currentPage === 'home' && <HomePage onNavigate={() => setCurrentPage('network')} />}
      {currentPage === 'network' && <InvestigationDashboard onBack={() => setCurrentPage('home')} />}
      {currentPage === 'timeline' && <TimelinePage />}
    </div>
  );
}
