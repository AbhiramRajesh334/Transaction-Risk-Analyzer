import React from 'react';

export default function DashboardHeader({ totals, stats, systemStatus }) {
  return (
    <header className="dashboard-header panel-card">
      <div className="header-copy">
        <span className="eyebrow">Investigation Console</span>
        <h1>Explainable Transaction Behavior and Relationship Risk Analyzer</h1>
        <p>Structured analyst workspace for reviewing suspicious accounts, understanding risk signals, and vetting evidence.</p>
      </div>

      <div className="header-cards">
        <div className="header-card">
          <span className="header-card-label">Total Accounts</span>
          <div className="header-card-value">{totals.totalAccounts.toLocaleString()}</div>
        </div>
        <div className="header-card">
          <span className="header-card-label">Total Transactions</span>
          <div className="header-card-value">{totals.totalTransactions.toLocaleString()}</div>
        </div>
        <div className="header-card">
          <span className="header-card-label">System Status</span>
          <div className="header-card-value">{systemStatus?.status ?? 'Unknown'}</div>
          <p className="status-detail">{systemStatus?.detail}</p>
        </div>
      </div>

      <div className="header-stats">
        <span className="header-stats-title">Graph Statistics</span>
        <ul>
          {stats.map((item) => (
            <li key={item.label}>
              <strong>{item.label}:</strong> {item.value}
            </li>
          ))}
        </ul>
      </div>
    </header>
  );
}
