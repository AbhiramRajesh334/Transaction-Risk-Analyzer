import React from 'react';

export default function TransactionFeed({ feed }) {
  return (
    <div>
      <div className="panel-title-block">
        <h2 className="panel-title">Live Transaction Feed</h2>
        <p className="panel-copy">Recent movements while the investigation is active.</p>
      </div>

      <div className="feed-list">
        {feed.map((item) => (
          <div key={item.transactionId} className="feed-item">
            <div className="feed-header">
              <span className="feed-id">{item.transactionId}</span>
              <span className="feed-time">{item.timestamp}</span>
            </div>
            <div className="feed-path">{item.sender} → {item.receiver}</div>
            <div className="feed-amount">{item.amount}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
