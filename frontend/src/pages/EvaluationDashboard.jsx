import React, { useEffect, useState } from 'react';
import { fetchEvaluationMetrics } from '../api/evaluationApi';
import { resetDemoDataset } from '../api/simulationApi';

function MetricCard({ label, value }) {
  return (
    <div className="summary-chip">
      <span className="summary-chip-label">{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function EvaluationDashboard({ onBack }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resetting, setResetting] = useState(false);

  const loadReport = () => {
    setLoading(true);
    setError(null);
    fetchEvaluationMetrics()
      .then((result) => setReport(result))
      .catch((fetchError) => {
        console.error('Evaluation fetch failed', fetchError);
        setError('Unable to load evaluation metrics.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadReport();
  }, []);

  const handleResetDemo = async () => {
    setResetting(true);
    try {
      await resetDemoDataset();
      loadReport();
    } catch (resetError) {
      console.error('Demo reset failed', resetError);
      setError('Failed to reset demo dataset.');
    } finally {
      setResetting(false);
    }
  };

  const metrics = report?.overall_metrics;

  return (
    <div className="investigation-shell">
      <div className="page-header">
        <div>
          <span className="eyebrow">Detection Evaluation</span>
          <h1>Measure how well the risk engine finds labeled fraud in the demo dataset.</h1>
          <p className="panel-copy">
            Compare predicted high-risk accounts against stored ground-truth labels and review per-scenario detection rates.
          </p>
        </div>
        <div className="page-header-actions">
          <button type="button" className="ghost-button" onClick={handleResetDemo} disabled={resetting}>
            {resetting ? 'Resetting…' : 'Reset demo data'}
          </button>
          <button type="button" className="ghost-button" onClick={() => (typeof onBack === 'function' ? onBack() : null)}>
            Back to overview
          </button>
        </div>
      </div>

      {loading && <div className="placeholder-block">Loading evaluation metrics…</div>}
      {error && <div className="placeholder-block">{error}</div>}

      {metrics && (
        <>
          <div className="investigation-summary-cards">
            <MetricCard label="Precision" value={metrics.precision.toFixed(2)} />
            <MetricCard label="Recall" value={metrics.recall.toFixed(2)} />
            <MetricCard label="F1 score" value={metrics.f1_score.toFixed(2)} />
            <MetricCard label="Accuracy" value={metrics.accuracy.toFixed(2)} />
          </div>

          <div className="investigation-summary-cards">
            <MetricCard label="True positives" value={metrics.true_positives} />
            <MetricCard label="False positives" value={metrics.false_positives} />
            <MetricCard label="False negatives" value={metrics.false_negatives} />
            <MetricCard label="Threshold" value={report.threshold} />
          </div>

          <section className="panel-card">
            <div className="panel-title-block">
              <h2 className="panel-title">Per-scenario detection</h2>
            </div>
            <div className="evaluation-table">
              {report.per_scenario.map((scenario) => (
                <div key={scenario.scenario_type} className="evaluation-row">
                  <div>
                    <strong>{scenario.display_name}</strong>
                    <p className="panel-copy">Labeled: {scenario.labeled_accounts.join(', ') || '—'}</p>
                  </div>
                  <div className="evaluation-stats">
                    <span>Detected: {(scenario.detection_rate * 100).toFixed(0)}%</span>
                    <span>Missed: {scenario.missed_accounts.join(', ') || '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="panel-card">
            <div className="panel-title-block">
              <h2 className="panel-title">Account comparison</h2>
            </div>
            <div className="evaluation-table">
              {report.account_details.map((account) => (
                <div key={account.account_id} className="evaluation-row">
                  <div>
                    <strong>{account.account_id}</strong>
                    <p className="panel-copy">Score {account.risk_score} · {account.risk_level}</p>
                  </div>
                  <div className="evaluation-stats">
                    <span className={account.is_labeled_fraud ? 'tag-fraud' : 'tag-normal'}>
                      {account.is_labeled_fraud ? 'Labeled fraud' : 'Normal'}
                    </span>
                    <span className={account.is_predicted_fraud ? 'tag-predicted' : 'tag-normal'}>
                      {account.is_predicted_fraud ? 'Predicted fraud' : 'Not flagged'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
