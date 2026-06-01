import React, { useEffect, useMemo, useState } from 'react';
import HighRiskAccountsPanel from '../components/risk/HighRiskAccountsPanel';
import TransactionGraph from '../components/graph/TransactionGraph';
import ExplainabilityPanel from '../components/explainability/ExplainabilityPanel';
import EvidenceViewer from '../components/evidence/EvidenceViewer';
import { fetchHighRiskAccounts, fetchRiskAccount, fetchExplainability } from '../api/riskApi';
import { fetchGraphStats } from '../api/graphApi';
import '../styles/InvestigationDashboard.css';

export default function InvestigationDashboard({ onBack }) {
  const [highRiskAccounts, setHighRiskAccounts] = useState([]);
  const [highRiskLoading, setHighRiskLoading] = useState(false);
  const [highRiskError, setHighRiskError] = useState(null);

  const [selectedAccount, setSelectedAccount] = useState(null);
  const [selectedReason, setSelectedReason] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  const [selectedAccountRisk, setSelectedAccountRisk] = useState(null);
  const [selectedAccountExplainability, setSelectedAccountExplainability] = useState(null);
  const [selectedAccountLoading, setSelectedAccountLoading] = useState(false);
  const [selectedAccountError, setSelectedAccountError] = useState(null);

  const [graphStats, setGraphStats] = useState(null);
  const [graphStatsLoading, setGraphStatsLoading] = useState(false);
  const [graphStatsError, setGraphStatsError] = useState(null);

  const selectedReasonDetails = useMemo(
    () => selectedAccountExplainability?.reasons?.find((reason) => reason.indicator === selectedReason) || selectedAccountExplainability?.reasons?.[0] || null,
    [selectedAccountExplainability, selectedReason],
  );

  useEffect(() => {
    let active = true;
    setHighRiskLoading(true);
    setHighRiskError(null);

    fetchHighRiskAccounts()
      .then((accounts) => {
        if (!active) return;
        setHighRiskAccounts(accounts);
        if (!selectedAccount && accounts.length > 0) {
          setSelectedAccount(accounts[0].account_id);
        }
      })
      .catch((error) => {
        if (!active) return;
        console.error('Failed to load high-risk accounts', error);
        setHighRiskError('Unable to load high-risk accounts.');
      })
      .finally(() => {
        if (!active) return;
        setHighRiskLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    setGraphStatsLoading(true);
    setGraphStatsError(null);

    fetchGraphStats()
      .then((result) => {
        if (!active) return;
        setGraphStats(result.statistics);
      })
      .catch((error) => {
        if (!active) return;
        console.error('Failed to load graph statistics', error);
        setGraphStatsError('Unable to load graph statistics.');
      })
      .finally(() => {
        if (!active) return;
        setGraphStatsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedAccount) {
      setSelectedAccountRisk(null);
      setSelectedAccountExplainability(null);
      setSelectedReason(null);
      setSelectedEvidence(null);
      return;
    }

    let active = true;
    setSelectedAccountLoading(true);
    setSelectedAccountError(null);
    setSelectedAccountRisk(null);
    setSelectedAccountExplainability(null);
    setSelectedReason(null);
    setSelectedEvidence(null);

    Promise.all([fetchRiskAccount(selectedAccount), fetchExplainability(selectedAccount)])
      .then(([riskResponse, explainResponse]) => {
        if (!active) return;
        setSelectedAccountRisk(riskResponse);
        setSelectedAccountExplainability(explainResponse);
        const initialReason = explainResponse?.reasons?.[0]?.indicator;
        setSelectedReason(initialReason || null);
        setSelectedEvidence(explainResponse?.reasons?.[0]?.evidence || null);
      })
      .catch((error) => {
        if (!active) return;
        console.error('Failed to load selected account details', error);
        setSelectedAccountError('Unable to load the selected account details.');
      })
      .finally(() => {
        if (!active) return;
        setSelectedAccountLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedAccount]);

  useEffect(() => {
    if (!selectedReasonDetails) {
      setSelectedEvidence(null);
      return;
    }

    setSelectedEvidence(selectedReasonDetails.evidence || null);
    if (selectedReason !== selectedReasonDetails.indicator) {
      setSelectedReason(selectedReasonDetails.indicator);
    }
  }, [selectedReasonDetails, selectedReason]);

  const handleAccountSelect = (accountId) => {
    setSelectedAccount(accountId);
  };

  return (
    <div className="investigation-shell">
      <div className="page-header">
        <div>
          <span className="eyebrow">Network Investigation</span>
          <h1>Inspect the transaction graph and surface the strongest risk signals.</h1>
          <p className="panel-copy">
            Select a high-risk account to focus the graph. Then choose the clearest explainability signal to reveal supporting evidence.
          </p>
        </div>
        <div className="page-header-actions">
          <button type="button" className="ghost-button" onClick={() => (typeof onBack === 'function' ? onBack() : null)}>
            Back to overview
          </button>
        </div>
      </div>

      <div className="investigation-summary-cards">
        <div className="summary-chip">
          <span className="summary-chip-label">High-risk queue</span>
          <strong>{highRiskAccounts.length}</strong>
          <p>{highRiskLoading ? 'Updating…' : 'Accounts flagged for review'}</p>
        </div>
        <div className="summary-chip">
          <span className="summary-chip-label">Active accounts</span>
          <strong>{graphStatsLoading ? '…' : graphStats?.total_nodes ?? 0}</strong>
          <p>Accounts currently mapped in the graph</p>
        </div>
        <div className="summary-chip">
          <span className="summary-chip-label">Transactions</span>
          <strong>{graphStatsLoading ? '…' : graphStats?.total_edges ?? 0}</strong>
          <p>Edges representing recent transaction flow</p>
        </div>
      </div>

      <section className="investigation-grid">
        <aside className="panel-card risk-card">
          <HighRiskAccountsPanel
            accounts={highRiskAccounts}
            selectedAccount={selectedAccount}
            loading={highRiskLoading}
            error={highRiskError}
            onAccountSelect={handleAccountSelect}
          />
        </aside>

        <main className="panel-card graph-card">
          <div className="panel-title-block">
            <h2 className="panel-title">Transaction Network</h2>
            <p className="panel-copy">Focus the relationship graph on the account under investigation.</p>
          </div>
          <TransactionGraph
            selectedAccount={selectedAccount}
            selectedReason={selectedReason}
            selectedEvidence={selectedEvidence}
            onNodeSelect={handleAccountSelect}
          />
        </main>
      </section>

      <section className="graph-detail-stack">
        <div className="panel-card explainability-card">
          <div className="panel-title-block">
            <h2 className="panel-title">Explainability</h2>
            <p className="panel-copy">Tap a reason to highlight the exact network evidence for the selected account.</p>
          </div>
          <ExplainabilityPanel
            accountId={selectedAccount}
            accountRisk={selectedAccountRisk}
            accountExplainability={selectedAccountExplainability}
            selectedReason={selectedReason}
            selectedReasonDetails={selectedReasonDetails}
            loading={selectedAccountLoading}
            error={selectedAccountError}
            onReasonSelect={setSelectedReason}
          />
        </div>

        <div className="panel-card evidence-panel">
          <div className="panel-title-block">
            <h2 className="panel-title">Evidence</h2>
            <p className="panel-copy">Detailed supporting information for the selected reason.</p>
          </div>
          <EvidenceViewer
            selectedReason={selectedReasonDetails}
            evidence={selectedEvidence}
            loading={selectedAccountLoading}
            error={selectedAccountError}
          />
        </div>
      </section>
    </div>
  );
}
