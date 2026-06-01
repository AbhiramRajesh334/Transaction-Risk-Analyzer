import React from 'react';

function formatLabel(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function summarizeValue(value) {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return 'None';
    const sample = value.slice(0, 3).join(', ');
    return `${value.length} item${value.length === 1 ? '' : 's'}${value.length > 3 ? ` (${sample}...)` : ` (${sample})`}`;
  }

  if (typeof value === 'object') {
    const keys = Object.keys(value);
    return keys.length === 0 ? 'None' : `${keys.length} field${keys.length === 1 ? '' : 's'}${keys.length <= 3 ? ` (${keys.map(formatLabel).join(', ')})` : ''}`;
  }

  return String(value);
}

export default function EvidenceViewer({ selectedReason, evidence, loading, error }) {
  return (
    <div>
      {loading ? (
        <div className="placeholder-block">Loading evidence…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : !selectedReason ? (
        <div className="placeholder-block">Select a signal to view short evidence details.</div>
      ) : (
        <>
          <div className="evidence-summary compact">
            <span className="section-label">Selected Signal</span>
            <strong>{formatLabel(selectedReason.indicator)}</strong>
            <p>{selectedReason.explanation}</p>
          </div>

          {evidence ? (
            <div className="evidence-list short-list">
              {Object.entries(evidence).slice(0, 4).map(([key, value]) => (
                <div key={key} className="evidence-card compact">
                  <div className="evidence-id">{formatLabel(key)}</div>
                  <div className="evidence-meta">{summarizeValue(value)}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="placeholder-block">No evidence available for this signal.</div>
          )}
        </>
      )}
    </div>
  );
}
