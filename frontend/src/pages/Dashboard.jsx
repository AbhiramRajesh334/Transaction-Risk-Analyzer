// Dashboard.jsx
// Minimal dashboard page that displays the transaction graph and statistics.

import React, { useEffect, useState } from 'react';
import TransactionGraph from '../components/graph/TransactionGraph';
import GraphLegend from '../components/graph/GraphLegend';
import { fetchGraphStats, fetchAccountDetails } from '../api/graphApi';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accountDetails, setAccountDetails] = useState(null);

  useEffect(() => {
    fetchGraphStats().then((r) => setStats(r.statistics)).catch((e) => console.error(e));
  }, []);

  useEffect(() => {
    if (!selectedAccount) {
      setAccountDetails(null);
      return;
    }

    fetchAccountDetails(selectedAccount)
      .then((data) => setAccountDetails(data))
      .catch((e) => {
        console.error(e);
        setAccountDetails(null);
      });
  }, [selectedAccount]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16, padding: 16 }}>
      <div style={{ border: '1px solid #eee', padding: 8 }}>
        <h3>Transaction Network</h3>
        <TransactionGraph onNodeSelect={(id) => setSelectedAccount(id)} />
      </div>

      <div style={{ border: '1px solid #eee', padding: 8 }}>
        <h3>Graph Statistics</h3>
        {stats ? (
          <ul>
            <li>Total Nodes: {stats.total_nodes}</li>
            <li>Total Edges: {stats.total_edges}</li>
            <li>Average Degree: {stats.average_degree.toFixed(2)}</li>
            <li>Graph Density: {stats.graph_density.toFixed(4)}</li>
          </ul>
        ) : (
          <div>Loading stats…</div>
        )}

        <GraphLegend />

        {selectedAccount ? (
          <div style={{ marginTop: 12 }}>
            <h4>Selected Account</h4>
            {accountDetails ? (
              <div>
                <div><strong>Account ID:</strong> {accountDetails.account_id}</div>
                <div><strong>Account Type:</strong> {accountDetails.account_type}</div>
                <div><strong>Degree:</strong> {accountDetails.degree}</div>
                <div><strong>Incoming:</strong> {accountDetails.incoming_neighbors.length}</div>
                <div><strong>Outgoing:</strong> {accountDetails.outgoing_neighbors.length}</div>
                <div><strong>Incoming Transactions:</strong> {accountDetails.incoming_transactions}</div>
                <div><strong>Outgoing Transactions:</strong> {accountDetails.outgoing_transactions}</div>
                <div style={{ marginTop: 8 }}>
                  <strong>Recent Transactions</strong>
                  <ul style={{ paddingLeft: 16 }}>
                    {accountDetails.recent_transactions.map((tx) => (
                      <li key={tx.transaction_id} style={{ fontSize: 12, marginBottom: 4 }}>
                        {tx.direction === 'incoming' ? 'IN' : 'OUT'} {tx.transaction_id} • {tx.sender_account} → {tx.receiver_account} • ₹{tx.amount} • {new Date(tx.timestamp).toLocaleString()}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div>Loading account details…</div>
            )}
          </div>
        ) : (
          <div style={{ marginTop: 12, color: '#666', fontSize: 12 }}>Click a node to view account details.</div>
        )}
      </div>
    </div>
  );
}
