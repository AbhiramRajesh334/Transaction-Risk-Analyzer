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
                  onClick={() => onReasonSelect(selectedReason === reason.indicator ? null : reason.indicator)}
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
