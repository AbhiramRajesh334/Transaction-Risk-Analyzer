import React, { useEffect, useState } from 'react';
import { fetchHighRiskCategoryAccounts } from '../api/riskApi';
import { fetchGraphStats } from '../api/graphApi';

const featureHighlights = [
  {
    title: 'Flag high-risk accounts',
    description: 'Spot the most suspicious entities and review the signals driving each risk score.',
  },
  {
    title: 'Map transaction relationships',
    description: 'Follow linked accounts and exposure paths to uncover hidden risk clusters.',
  },
  {
    title: 'Explain every finding',
    description: 'Open evidence-backed summaries that turn complex graph behavior into clear investigation steps.',
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
          fetchHighRiskCategoryAccounts(),
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
          <h1>Detect fraud patterns, trace risky relationships, and explain every alert.</h1>
          <p>Monitor suspicious accounts, map transaction networks, and surface evidence-backed insights from one concise investigation workspace.</p>
          <button type="button" className="primary-button" onClick={() => onNavigate('network')}>
            Explore the investigation dashboard
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
