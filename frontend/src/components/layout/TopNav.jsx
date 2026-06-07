import React from 'react';

export default function TopNav({ currentPage, onNavigate }) {
  return (
    <header className="top-nav">
      <div className="top-nav-brand">
        <strong>Investigation Console</strong>
        <span>Explainability + relationship risk</span>
      </div>
      <nav className="top-nav-links">
        <button
          type="button"
          className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
          onClick={() => onNavigate('home')}
        >
          Overview
        </button>
        <button
          type="button"
          className={`nav-link ${currentPage === 'network' ? 'active' : ''}`}
          onClick={() => onNavigate('network')}
        >
          Network Graph
        </button>
        <button
          type="button"
          className={`nav-link ${currentPage === 'evaluation' ? 'active' : ''}`}
          onClick={() => onNavigate('evaluation')}
        >
          Evaluation
        </button>
      </nav>
    </header>
  );
}
