import React, { useState, useEffect } from 'react';
import { fetchTopTypologyAccounts } from '../../api/riskApi';

const TYPOLOGIES = [
  { id: 'activity_spike', name: 'Activity Spike' },
  { id: 'amount_anomaly', name: 'Amount Anomaly' },
  { id: 'pass_through', name: 'Pass-Through' },
  { id: 'counterparty_explosion', name: 'Counterparty Explosion' },
  { id: 'round_tripping', name: 'Round Tripping' },
  { id: 'structuring', name: 'Structuring' },
  { id: 'circular_flow', name: 'Circular Flow' },
  { id: 'suspicious_exposure', name: 'Suspicious Exposure' },
];

export default function TypologyScanner({ selectedAccount, onAccountSelect }) {
  const [selectedTypology, setSelectedTypology] = useState(TYPOLOGIES[0].id);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    fetchTopTypologyAccounts(selectedTypology, 16)
      .then((data) => {
        if (!active) return;
        setAccounts(data);
      })
      .catch((err) => {
        if (!active) return;
        console.error('Failed to load typology accounts', err);
        setError('Failed to load accounts for this typology.');
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedTypology]);

  return (
    <div className="typology-scanner">
      <div className="panel-title-block" style={{ marginBottom: '16px' }}>
        <h2 className="panel-title" style={{ fontSize: '1.1rem', margin: '0 0 4px' }}>Typology Scanner</h2>
        <p className="panel-copy" style={{ margin: 0, fontSize: '0.85rem' }}>Scan the network for specific fraud patterns.</p>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <select 
          value={selectedTypology} 
          onChange={(e) => setSelectedTypology(e.target.value)}
          style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--panel-border, #cbd5e1)', background: 'transparent', color: 'inherit', fontWeight: 500 }}
        >
          {TYPOLOGIES.map(typ => (
            <option key={typ.id} value={typ.id} style={{ color: '#000' }}>{typ.name}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="placeholder-block">Scanning network for {TYPOLOGIES.find(t => t.id === selectedTypology)?.name}…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : accounts.length === 0 ? (
        <div className="placeholder-block">No accounts detected for this typology.</div>
      ) : (
        <div className="risk-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '12px' }}>
          {accounts.map((account) => (
            <button
              key={account.account_id}
              type="button"
              className={`risk-item ${selectedAccount === account.account_id ? 'selected' : ''}`}
              onClick={() => onAccountSelect(account.account_id)}
            >
              <div>
                <div className="risk-id">{account.account_id}</div>
                <div className="risk-detail">Typology Score: {account.score}/100</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
