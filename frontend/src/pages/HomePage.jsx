import React, { useEffect, useState } from 'react';
import { fetchHighRiskAccounts } from '../api/riskApi';
import { fetchGraphStats } from '../api/graphApi';

const featureHighlights = [
  {
    title: 'Investigate flagged entities',
    description: 'Browse the top high-risk accounts and examine why they are flagged by the model.',
  },
  {
    title: 'Map suspicious relationships',
    description: 'Explore the transaction network and identify the most important risk clusters.',
  },
  {
    title: 'Evidence-backed explanations',
    description: 'Open concise reason summaries and inspect supporting evidence quickly.',
  },
];

export default function HomePage({ onNavigate }) {
  const [highRiskCount, setHighRiskCount] = useState(0);
  const [graphStats, setGraphStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function loadData() {
      setLoading(true);
      try {
        const [accounts, statsResult] = await Promise.all([
          fetchHighRiskAccounts(10),
          fetchGraphStats(),
        ]);

        if (!active) return;
        setHighRiskCount(accounts.length);
        setGraphStats(statsResult.statistics);
      } catch (error) {
        console.error('Home page fetch failed', error);
      } finally {
        if (!active) return;
        setLoading(false);
      }
    }

    loadData();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="home-shell">
      <section className="home-hero">
        <div className="home-hero-panel">
          <span className="hero-tag">Investigation Console</span>
          <h1>Enterprise transaction risk visibility.</h1>
          <p>Track suspicious accounts, inspect graph relationships, and drill into explainable signals from one clean dashboard.</p>
          <button type="button" className="primary-button" onClick={() => onNavigate('network')}>
            Open network graph
          </button>
        </div>
      </section>

      <section className="home-stats">
        <div className="landing-card">
          <div className="landing-card-icon">🔥</div>
          <strong>{loading ? '–' : highRiskCount}</strong>
          <p>High-risk accounts</p>
        </div>
        <div className="landing-card">
          <div className="landing-card-icon">🧭</div>
          <strong>{loading ? '–' : graphStats?.total_nodes ?? '–'}</strong>
          <p>Active graph accounts</p>
        </div>
        <div className="landing-card">
          <div className="landing-card-icon">🔗</div>
          <strong>{loading ? '–' : graphStats?.total_edges ?? '–'}</strong>
          <p>Transaction relationships</p>
        </div>
        <div className="landing-card">
          <div className="landing-card-icon">📊</div>
          <strong>{loading ? '–' : graphStats?.graph_density?.toFixed(4) ?? '–'}</strong>
          <p>Graph density</p>
        </div>
      </section>

      <section className="feature-grid compact-grid">
        {featureHighlights.map((feature) => (
          <article key={feature.title} className="feature-card">
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
