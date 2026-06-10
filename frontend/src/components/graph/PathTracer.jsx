import React, { useEffect, useState } from 'react';
import { fetchFundFlowPath } from '../../api/graphApi';

export default function PathTracer({ defaultSource, defaultTarget, onPathFound }) {
  const [source, setSource] = useState(defaultSource || '');

  useEffect(() => {
    if (defaultSource) {
      setSource(defaultSource);
    }
  }, [defaultSource]);
  const [target, setTarget] = useState(defaultTarget || '');
  const [pathResult, setPathResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTrace = async () => {
    if (!source || !target) {
      setError('Enter both source and target accounts.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await fetchFundFlowPath(source.trim(), target.trim());
      setPathResult(result);
      if (typeof onPathFound === 'function') {
        onPathFound(result);
      }
    } catch (traceError) {
      console.error('Path trace failed', traceError);
      setError(traceError.message || 'Unable to trace fund flow path.');
      setPathResult(null);
      if (typeof onPathFound === 'function') {
        onPathFound(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setPathResult(null);
    setTarget('');
    setError(null);
    if (typeof onPathFound === 'function') {
      onPathFound(null);
    }
  };

  return (
    <div className="path-tracer">
      <div className="path-tracer-form">
        <label>
          Source
          <input value={source} onChange={(event) => setSource(event.target.value)} placeholder="e.g. STU01" />
        </label>
        <label>
          Target
          <input value={target} onChange={(event) => setTarget(event.target.value)} placeholder="e.g. BUS02" />
        </label>
        <div style={{ display: 'flex', gap: 8, alignSelf: 'end' }}>
          <button type="button" className="primary-button compact-button" onClick={handleTrace} disabled={loading}>
            {loading ? 'Tracing…' : 'Trace path'}
          </button>
          {pathResult && (
            <button type="button" className="secondary-button compact-button" onClick={handleClear}>
              Clear
            </button>
          )}
        </div>
      </div>

      {error && <div className="placeholder-block" style={{ marginTop: 12 }}>{error}</div>}

      {pathResult && (
        <div className="path-result">
          {pathResult.found ? (
            <>
              <p className="panel-copy">
                Found {pathResult.hop_count} hop path: {pathResult.path_accounts.join(' → ')}
              </p>
              <div className="path-steps">
                {pathResult.path.map((step) => (
                  <div key={`${step.transaction_id}-${step.step}`} className="path-step">
                    <span className="path-step-index">Hop {step.step}</span>
                    <span>{step.sender_account} → {step.receiver_account}</span>
                    <span>₹{Number(step.amount).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="placeholder-block" style={{ marginTop: 12 }}>No path found within the hop limit.</div>
          )}
        </div>
      )}
    </div>
  );
}
