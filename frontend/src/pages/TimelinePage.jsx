import React, { useState, useEffect } from 'react';
import AccountTimeline from '../components/timeline/AccountTimeline';
import { fetchHighRiskAccounts } from '../api/riskApi';

export default function TimelinePage() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHighRiskAccounts(16)
      .then((data) => {
        setAccounts(data);
        if (data.length > 0) setSelectedAccount(data[0].account_id);
      })
      .catch((err) => console.error('Failed to load accounts', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="investigation-shell" style={{ padding: '32px 40px' }}>
      <div className="page-header" style={{ marginBottom: '28px' }}>
        <div>
          <span className="eyebrow">Account Timeline</span>
          <h1 style={{ margin: '8px 0 4px' }}>Chronological Transaction History</h1>
          <p className="panel-copy">Select an account below to explore its full transaction timeline.</p>
        </div>
      </div>

      {/* Account selector */}
      <div className="panel-card" style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        <label style={{ fontWeight: 600, fontSize: '0.9rem', color: 'inherit', whiteSpace: 'nowrap' }}>
          Select Account:
        </label>
        {loading ? (
          <span className="panel-copy">Loading accounts…</span>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {accounts.map((account) => (
              <button
                key={account.account_id}
                type="button"
                onClick={() => setSelectedAccount(account.account_id)}
                className={`ghost-button ${selectedAccount === account.account_id ? 'active-live' : ''}`}
                style={{ padding: '6px 14px', fontSize: '0.85rem' }}
              >
                {account.account_id}
                <span style={{ marginLeft: '6px', opacity: 0.7, fontSize: '0.75rem' }}>
                  {account.risk_level}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Timeline panel */}
      <div className="panel-card">
        {selectedAccount ? (
          <>
            <div className="panel-title-block" style={{ marginBottom: '16px' }}>
              <h2 className="panel-title">Timeline for {selectedAccount}</h2>
              <p className="panel-copy">All recorded transactions, ordered chronologically.</p>
            </div>
            <AccountTimeline accountId={selectedAccount} />
          </>
        ) : (
          <div className="placeholder-block">Select an account above to view its timeline.</div>
        )}
      </div>
    </div>
  );
}
