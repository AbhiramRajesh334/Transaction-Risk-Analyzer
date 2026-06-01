import React from 'react';

export default function HighRiskAccountsPanel({ accounts, selectedAccount, loading, error, onAccountSelect }) {
  return (
    <div>
      <div className="panel-title-block">
        <h2 className="panel-title">High Risk Accounts</h2>
        <p className="panel-copy">Investigation queue for the top accounts flagged by the risk engine.</p>
      </div>

      {loading ? (
        <div className="placeholder-block">Loading high-risk accounts…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : accounts.length === 0 ? (
        <div className="placeholder-block">No high-risk accounts available.</div>
      ) : (
        <div className="risk-list">
          {accounts.map((account) => (
            <button
              key={account.account_id}
              type="button"
              className={`risk-item ${selectedAccount === account.account_id ? 'selected' : ''}`}
              onClick={() => onAccountSelect(account.account_id)}
            >
              <div>
                <div className="risk-id">{account.account_id}</div>
                <div className="risk-detail">Risk {account.risk_score} · {account.risk_level}</div>
              </div>
              <div className="risk-meta">Top reason: {account.top_reasons?.[0] ?? 'Unknown'}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
