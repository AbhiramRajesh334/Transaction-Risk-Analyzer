import React, { useState } from 'react';
import { fetchRecalculatedRisk } from '../../api/riskApi';

const DEFAULT_WEIGHTS = {
  activity_spike: 0.12,
  amount_anomaly: 0.16,
  pass_through: 0.22,
  counterparty_explosion: 0.08,
  suspicious_exposure: 0.16,
  round_tripping: 0.14,
  structuring: 0.08,
  circular_flow: 0.08,
};

const STORAGE_KEY = 'tra_custom_weights';

function loadSavedWeights() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return { ...DEFAULT_WEIGHTS, ...JSON.parse(saved) };
  } catch (_) { /* ignore */ }
  return DEFAULT_WEIGHTS;
}

export default function RiskConfigurator({ onRiskRecalculated }) {
  const [weights, setWeights] = useState(loadSavedWeights);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isCustom = Object.keys(DEFAULT_WEIGHTS).some(
    k => Math.abs((weights[k] || 0) - DEFAULT_WEIGHTS[k]) > 0.001
  );

  const handleWeightChange = (key, value) => {
    setWeights((prev) => ({
      ...prev,
      [key]: parseFloat(value) || 0,
    }));
  };

  const handleApply = async () => {
    setLoading(true);
    setError(null);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(weights));
      const result = await fetchRecalculatedRisk(weights);
      if (typeof onRiskRecalculated === 'function') {
        onRiskRecalculated(result, weights);
      }
    } catch (err) {
      setError(err.message || 'Failed to recalculate risk');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setWeights(DEFAULT_WEIGHTS);
    localStorage.removeItem(STORAGE_KEY);
    // Re-run with defaults so the queue resets too
    try {
      setLoading(true);
      const result = await fetchRecalculatedRisk(DEFAULT_WEIGHTS);
      if (typeof onRiskRecalculated === 'function') {
        onRiskRecalculated(result, null);
      }
    } catch (_) { /* silent */ } finally {
      setLoading(false);
    }
  };

  return (
    <div className="risk-configurator" style={{ padding: '16px', background: 'var(--panel-bg, #ffffff)', borderRadius: '16px', border: '1px solid var(--panel-border, rgba(15, 23, 42, 0.08))' }}>
      <div className="panel-title-block" style={{ marginBottom: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
          <h2 className="panel-title" style={{ fontSize: '1.1rem', margin: 0 }}>What-If Risk Configurator</h2>
          {isCustom && (
            <span style={{ padding: '2px 8px', borderRadius: '999px', fontSize: '0.7rem', fontWeight: 700, background: 'rgba(251,191,36,0.15)', color: '#f59e0b', border: '1px solid rgba(251,191,36,0.4)', whiteSpace: 'nowrap' }}>
              Custom active
            </span>
          )}
        </div>
        <p className="panel-copy" style={{ margin: '4px 0 0', fontSize: '0.82rem', color: '#64748b' }}>Adjust weights to recalculate risk scores. Changes are saved between sessions.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '380px', overflowY: 'auto', paddingRight: '8px' }}>
        {Object.entries(weights).map(([key, value]) => {
          const isChanged = Math.abs(value - (DEFAULT_WEIGHTS[key] || 0)) > 0.001;
          return (
            <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600 }}>
                <span style={{ textTransform: 'capitalize', color: isChanged ? '#f59e0b' : 'inherit' }}>
                  {key.replace(/_/g, ' ')}
                </span>
                <span style={{ color: isChanged ? '#f59e0b' : 'inherit' }}>{value.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={value}
                onChange={(e) => handleWeightChange(key, e.target.value)}
                style={{ width: '100%', cursor: 'pointer', accentColor: isChanged ? '#f59e0b' : undefined }}
              />
            </div>
          );
        })}
      </div>

      {error && <div style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '12px' }}>{error}</div>}

      <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
        <button
          type="button"
          onClick={handleApply}
          disabled={loading}
          style={{ flex: 1, padding: '8px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}
        >
          {loading ? 'Recalculating...' : 'Apply Weights'}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={loading}
          style={{ padding: '8px 12px', background: 'transparent', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '8px', cursor: 'pointer' }}
        >
          Reset
        </button>
      </div>
    </div>
  );
}
