import React, { useState } from 'react';

const LEVEL_CONFIG = {
  HIGH: { label: 'HIGH', color: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' },
  MEDIUM: { label: 'MED', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' },
  LOW: { label: 'LOW', color: '#10b981', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)' },
};

function RiskBadge({ level }) {
  const cfg = LEVEL_CONFIG[level] || LEVEL_CONFIG.LOW;
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 7px',
      borderRadius: '999px',
      fontSize: '0.7rem',
      fontWeight: 700,
      letterSpacing: '0.04em',
      color: cfg.color,
      background: cfg.bg,
      border: `1px solid ${cfg.border}`,
      flexShrink: 0,
    }}>
      {cfg.label}
    </span>
  );
}

export default function HighRiskAccountsPanel({ accounts, selectedAccount, loading, error, onAccountSelect }) {
  const [showAll, setShowAll] = useState(false);

  const grouped = accounts.reduce((acc, a) => {
    const level = a.risk_level || 'LOW';
    (acc[level] = acc[level] || []).push(a);
    return acc;
  }, {});

  const highAccounts = grouped.HIGH || [];
  const medAccounts = grouped.MEDIUM || [];
  const lowAccounts = grouped.LOW || [];

  // By default show HIGH + MEDIUM; user can expand to see LOW
  const visibleAccounts = showAll ? accounts : [...highAccounts, ...medAccounts];

  return (
    <div>
      <div className="panel-title-block">
        <h2 className="panel-title">Risk Ranking</h2>
        <p className="panel-copy">All accounts ranked by risk signal strength.</p>
      </div>

      {/* Summary pills */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {highAccounts.length > 0 && (
          <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 700, color: '#ef4444', background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)' }}>
            {highAccounts.length} High
          </span>
        )}
        {medAccounts.length > 0 && (
          <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 700, color: '#f59e0b', background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.3)' }}>
            {medAccounts.length} Medium
          </span>
        )}
        {lowAccounts.length > 0 && (
          <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 700, color: '#10b981', background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.3)' }}>
            {lowAccounts.length} Low
          </span>
        )}
      </div>

      {loading ? (
        <div className="placeholder-block">Loading accounts…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : accounts.length === 0 ? (
        <div className="placeholder-block">No accounts available.</div>
      ) : (
        <>
          <div className="risk-list">
            {visibleAccounts.map((account) => (
              <button
                key={account.account_id}
                type="button"
                className={`risk-item ${selectedAccount === account.account_id ? 'selected' : ''}`}
                onClick={() => onAccountSelect(account.account_id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', width: '100%' }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="risk-id">{account.account_id}</div>
                    <div className="risk-detail">Score {account.risk_score} · {account.top_reasons?.[0] ?? 'No signal'}</div>
                  </div>
                  <RiskBadge level={account.risk_level} />
                </div>
              </button>
            ))}
          </div>

          {lowAccounts.length > 0 && (
            <button
              type="button"
              onClick={() => setShowAll(v => !v)}
              style={{
                marginTop: '10px',
                width: '100%',
                padding: '6px',
                background: 'transparent',
                border: '1px dashed rgba(148,163,184,0.4)',
                borderRadius: '8px',
                color: '#64748b',
                fontSize: '0.78rem',
                cursor: 'pointer',
              }}
            >
              {showAll ? `Hide ${lowAccounts.length} low-risk accounts ▲` : `Show ${lowAccounts.length} low-risk accounts ▼`}
            </button>
          )}
        </>
      )}
    </div>
  );
}
