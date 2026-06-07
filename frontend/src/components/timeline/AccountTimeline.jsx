import React, { useEffect, useState } from 'react';
import { fetchAccountTimeline } from '../../api/transactionsApi';

function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown time';
  return new Date(timestamp).toLocaleString();
}

export default function AccountTimeline({ accountId }) {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!accountId) {
      setTimeline([]);
      return undefined;
    }

    let active = true;
    setLoading(true);
    setError(null);

    fetchAccountTimeline(accountId)
      .then((result) => {
        if (!active) return;
        setTimeline(result.timeline || []);
      })
      .catch((fetchError) => {
        if (!active) return;
        console.error('Failed to load timeline', fetchError);
        setError('Unable to load account timeline.');
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [accountId]);

  if (!accountId) {
    return <div className="placeholder-block">Select an account to view its transaction timeline.</div>;
  }

  if (loading) {
    return <div className="placeholder-block">Loading timeline…</div>;
  }

  if (error) {
    return <div className="placeholder-block">{error}</div>;
  }

  if (!timeline.length) {
    return <div className="placeholder-block">No transactions found for this account.</div>;
  }

  return (
    <div className="timeline-list">
      {timeline.map((tx) => (
        <div key={tx.transaction_id} className={`timeline-item ${tx.direction}`}>
          <div className="timeline-meta">
            <span className="timeline-id">{tx.transaction_id}</span>
            <span className="timeline-time">{formatTimestamp(tx.timestamp)}</span>
          </div>
          <div className="timeline-flow">
            <span className={`timeline-direction ${tx.direction}`}>{tx.direction === 'incoming' ? 'IN' : 'OUT'}</span>
            <span>{tx.sender_account} → {tx.receiver_account}</span>
          </div>
          <div className="timeline-amount">₹{Number(tx.amount).toLocaleString()}</div>
        </div>
      ))}
    </div>
  );
}
