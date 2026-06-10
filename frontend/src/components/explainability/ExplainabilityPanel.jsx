import React from 'react';

function labelFromIndicator(indicator) {
  return indicator
    ? indicator
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (char) => char.toUpperCase())
    : 'Reason';
}

export default function ExplainabilityPanel({
  accountId,
  accountRisk,
  accountExplainability,
  accountFeatures,
  selectedReason,
  selectedReasonDetails,
  loading,
  error,
  onReasonSelect,
}) {
  return (
    <div>
      {loading ? (
        <div className="placeholder-block">Loading explainability details…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : !accountId ? (
        <div className="placeholder-block">Select an account from the graph or risk queue to review explanations.</div>
      ) : (
        <div className="explainability-card">
          <div className="explainability-header">
            <h3>Account details</h3>
            <p>Summary of the selected account risk profile.</p>
          </div>
          <div className="account-detail-grid">
            <div className="account-detail-label">Account</div>
            <div>{accountId}</div>
            <div className="account-detail-label">Score</div>
            <div>{accountRisk?.risk_score ?? 'N/A'}</div>
            <div className="account-detail-label">Level</div>
            <div>{accountRisk?.risk_level ?? 'N/A'}</div>
          </div>

          {accountFeatures && (
            <div className="explainability-section compact" style={{ marginBottom: 22 }}>
              <div className="explainability-header">
                <h3>Behavioral features</h3>
                <p>Calculated transaction patterns and relationship signals.</p>
              </div>
              <div className="features-grid" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: 16,
                background: '#ffffff',
                border: '1px solid rgba(148, 163, 184, 0.16)',
                borderRadius: 16,
                padding: 16
              }}>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Transactions</div>
                  <strong style={{ fontSize: 16 }}>{accountFeatures.transaction_count}</strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>
                    {accountFeatures.incoming_count} in / {accountFeatures.outgoing_count} out
                  </span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Fund Flow</div>
                  <strong style={{ fontSize: 16 }}>
                    ₹{(accountFeatures.incoming_amount || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })} in
                  </strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>
                    ₹{(accountFeatures.outgoing_amount || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })} out
                  </span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Pass-through</div>
                  <strong style={{ fontSize: 16 }}>
                    {accountFeatures.pass_through_ratio != null 
                      ? `${(accountFeatures.pass_through_ratio * 100).toFixed(0)}%` 
                      : '0%'}
                  </strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>Relayed funds ratio</span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Tx Velocity</div>
                  <strong style={{ fontSize: 16 }}>{accountFeatures.velocity.toFixed(2)} / hr</strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>
                    {accountFeatures.recent_activity_count} in last 7d
                  </span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Counterparties</div>
                  <strong style={{ fontSize: 16 }}>{accountFeatures.unique_counterparties} unique</strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>
                    {accountFeatures.in_degree} senders / {accountFeatures.out_degree} receivers
                  </span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <div style={{ color: '#64748b', fontWeight: 600 }}>Pattern Flags</div>
                  <strong style={{ fontSize: 14, color: accountFeatures.circular_flow_participation || accountFeatures.round_trip_count || accountFeatures.structuring_count ? '#ef4444' : '#16a34a' }}>
                    {accountFeatures.circular_flow_participation ? 'Cycle ' : ''}
                    {accountFeatures.round_trip_count ? `Round-trip (${accountFeatures.round_trip_count}) ` : ''}
                    {accountFeatures.structuring_count ? `Struct (${accountFeatures.structuring_count})` : ''}
                    {!accountFeatures.circular_flow_participation && !accountFeatures.round_trip_count && !accountFeatures.structuring_count ? 'None' : ''}
                  </strong>
                  <span style={{ color: '#64748b', fontSize: 11, display: 'block' }}>Laundering/Structuring alerts</span>
                </div>
              </div>
            </div>
          )}

          <div className="explainability-section compact">
            <div className="explainability-header">
              <h3>Reasons</h3>
              <p>Tap a reason to highlight the most relevant network evidence.</p>
            </div>
            <div className="reason-list short-list">
              {accountExplainability?.reasons?.map((reason) => (
                <button
                  key={reason.indicator}
                  type="button"
                  className={`reason-item ${selectedReason === reason.indicator ? 'selected' : ''}`}
                  onClick={() => onReasonSelect(reason.indicator)}
                >
                  <div>
                    <strong>{labelFromIndicator(reason.indicator)}</strong>
                    <p>{reason.explanation}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
