import React from 'react';

function formatLabel(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatCurrency(value) {
  const amount = Number(value || 0);
  return `₹${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatNumber(value) {
  const numeric = Number(value || 0);
  return Number.isInteger(numeric) ? numeric.toLocaleString('en-US') : numeric.toFixed(2);
}

function getEvidenceNarrative(indicator, evidence) {
  const label = (indicator || '').toLowerCase();

  if (label.includes('activity')) {
    return 'This burst of activity is a strong sign of a short-term fraud surge rather than normal account behavior.';
  }

  if (label.includes('amount')) {
    return 'Large transfers stand out from the account’s typical pattern, which makes the amount profile look intentionally abnormal.';
  }

  if (label.includes('pass')) {
    return 'The account is acting as a fast relay for funds, which is a classic pass-through laundering pattern.';
  }

  if (label.includes('counterparty')) {
    return 'The account is expanding its network too quickly, which often signals a spreading fraud or laundering ring.';
  }

  if (label.includes('exposure')) {
    return 'Exposure to elevated-risk neighbors increases the chance this account is being used to support a broader fraud chain.';
  }

  return 'The selected signal points to unusual transaction behavior that deserves investigation.';
}

function buildFactCards(evidence = {}) {
  const cards = [];

  if (evidence.incoming_amount != null) {
    cards.push({ label: 'Incoming flow', value: formatCurrency(evidence.incoming_amount), note: 'Funds entering the account' });
  }

  if (evidence.outgoing_amount != null) {
    cards.push({ label: 'Outgoing flow', value: formatCurrency(evidence.outgoing_amount), note: 'Funds exiting the account' });
  }

  if (evidence.pass_through_ratio != null) {
    cards.push({ label: 'Pass-through ratio', value: `${Number(evidence.pass_through_ratio).toFixed(2)}`, note: 'How quickly money is being relayed' });
  }

  if (evidence.average_amount != null) {
    cards.push({ label: 'Average transfer', value: formatCurrency(evidence.average_amount), note: 'Typical transaction size' });
  }

  if (evidence.max_amount != null) {
    cards.push({ label: 'Largest transfer', value: formatCurrency(evidence.max_amount), note: 'Highest observed amount' });
  }

  if (evidence.unique_counterparties != null) {
    cards.push({ label: 'Distinct counterparties', value: formatNumber(evidence.unique_counterparties), note: 'Unique parties connected to the account' });
  }

  if (evidence.neighbor_count != null) {
    cards.push({ label: 'Connected accounts', value: formatNumber(evidence.neighbor_count), note: 'Accounts in the surrounding network' });
  }

  if (evidence.suspicious_neighbor_count != null) {
    cards.push({ label: 'High-risk neighbors', value: formatNumber(evidence.suspicious_neighbor_count), note: 'Neighbors flagged as elevated risk' });
  }

  return cards.slice(0, 4);
}

export default function EvidenceViewer({ selectedReason, evidence, loading, error }) {
  const factCards = buildFactCards(evidence || {});
  const contextTransactions = evidence?.supporting_transactions || [];

  return (
    <div className="evidence-panel-shell">
      {loading ? (
        <div className="placeholder-block">Loading evidence…</div>
      ) : error ? (
        <div className="placeholder-block">{error}</div>
      ) : !selectedReason ? (
        <div className="placeholder-block">Select a signal to review the fraud explanation and its supporting evidence.</div>
      ) : (
        <>
          <article className="evidence-story-card">
            <span className="section-label">Fraud story</span>
            <h3>{formatLabel(selectedReason.indicator)}</h3>
            <p className="evidence-story-text">{selectedReason.explanation}</p>
            <p className="evidence-story-note">{getEvidenceNarrative(selectedReason.indicator, evidence)}</p>
          </article>

          {factCards.length > 0 ? (
            <section className="evidence-facts-grid">
              {factCards.map((item) => (
                <article key={item.label} className="evidence-fact-card">
                  <span className="evidence-fact-label">{item.label}</span>
                  <strong className="evidence-fact-value">{item.value}</strong>
                  <span className="evidence-fact-note">{item.note}</span>
                </article>
              ))}
            </section>
          ) : null}

          {contextTransactions.length > 0 ? (
            <section className="evidence-context-card">
              <h4>Supporting transactions</h4>
              <p>High-impact transfers behind the selected fraud signal.</p>
              <ul className="evidence-transaction-list">
                {contextTransactions.slice(0, 4).map((tx) => {
                  const txLabel = tx.direction === 'incoming'
                    ? `Incoming from ${tx.sender_account || 'unknown account'}`
                    : `Outgoing to ${tx.receiver_account || 'unknown account'}`;

                  return (
                    <li key={tx.transaction_id || tx.id}>
                      <strong>{tx.transaction_id || tx.id}</strong>
                      <span>{txLabel}</span>
                      <span>{formatCurrency(tx.amount)} · {tx.direction || 'transaction'}</span>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
