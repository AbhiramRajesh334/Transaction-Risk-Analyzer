import React, { useEffect, useMemo, useState } from 'react';
import HighRiskAccountsPanel from '../components/risk/HighRiskAccountsPanel';
import TransactionGraph from '../components/graph/TransactionGraph';
import ExplainabilityPanel from '../components/explainability/ExplainabilityPanel';
import EvidenceViewer from '../components/evidence/EvidenceViewer';
import AccountTimeline from '../components/timeline/AccountTimeline';
import TransactionFeed from '../components/transactions/TransactionFeed';
import PathTracer from '../components/graph/PathTracer';
import RiskConfigurator from '../components/risk/RiskConfigurator';
import TypologyScanner from '../components/risk/TypologyScanner';
import { fetchHighRiskAccounts, fetchHighRiskCategoryAccounts, fetchRiskAccount, fetchRiskAccountWithWeights, fetchExplainability, fetchExplainabilityWithWeights, fetchAccountFeatures } from '../api/riskApi';
import { fetchGraphStats } from '../api/graphApi';
import { fetchRecentTransactions } from '../api/transactionsApi';
import { triggerLiveTick } from '../api/simulationApi';
import '../styles/InvestigationDashboard.css';

export default function InvestigationDashboard({ onBack }) {
  const [highRiskAccounts, setHighRiskAccounts] = useState([]);
  const [highRiskCategoryCount, setHighRiskCategoryCount] = useState(0);
  const [lowRiskCategoryCount, setLowRiskCategoryCount] = useState(0);
  const [highRiskLoading, setHighRiskLoading] = useState(false);
  const [highRiskError, setHighRiskError] = useState(null);
  
  const [sidebarTab, setSidebarTab] = useState('risk'); // 'risk' | 'timeline' | 'tracer' | 'config'

  const [selectedAccount, setSelectedAccount] = useState(null);
  const [selectedReason, setSelectedReason] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  // Custom weights from the What-If configurator (null = use defaults).
  const [customWeights, setCustomWeights] = useState(() => {
    try {
      const saved = localStorage.getItem('tra_custom_weights');
      return saved ? JSON.parse(saved) : null;
    } catch (_) { return null; }
  });

  const [selectedAccountRisk, setSelectedAccountRisk] = useState(null);
  const [selectedAccountExplainability, setSelectedAccountExplainability] = useState(null);
  const [selectedAccountFeatures, setSelectedAccountFeatures] = useState(null);
  const [selectedAccountLoading, setSelectedAccountLoading] = useState(false);
  const [selectedAccountError, setSelectedAccountError] = useState(null);

  const [graphStats, setGraphStats] = useState(null);
  const [graphStatsLoading, setGraphStatsLoading] = useState(false);
  const [graphStatsError, setGraphStatsError] = useState(null);

  const [liveFeed, setLiveFeed] = useState([]);
  const [liveFeedEnabled, setLiveFeedEnabled] = useState(false);

  const selectedReasonDetails = useMemo(
    () => selectedAccountExplainability?.reasons?.find((reason) => reason.indicator === selectedReason) || null,
    [selectedAccountExplainability, selectedReason],
  );

  useEffect(() => {
    let active = true;
    setHighRiskLoading(true);
    setHighRiskError(null);

    Promise.all([fetchHighRiskAccounts(16), fetchHighRiskCategoryAccounts()])
      .then(([rankedAccounts, highRiskAccountsOnly]) => {
        if (!active) return;
        setHighRiskAccounts(rankedAccounts);
        setHighRiskCategoryCount(highRiskAccountsOnly.length);
        setLowRiskCategoryCount(rankedAccounts.filter(a => a.risk_level === 'LOW').length);
        if (!selectedAccount && rankedAccounts.length > 0) {
          setSelectedAccount(rankedAccounts[0].account_id);
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
    setSelectedAccountFeatures(null);
    setSelectedReason(null);
    setSelectedEvidence(null);

    Promise.all([
      customWeights ? fetchRiskAccountWithWeights(selectedAccount, customWeights) : fetchRiskAccount(selectedAccount),
      customWeights ? fetchExplainabilityWithWeights(selectedAccount, customWeights) : fetchExplainability(selectedAccount),
      fetchAccountFeatures(selectedAccount)
    ])
      .then(([riskResponse, explainResponse, featuresResponse]) => {
        if (!active) return;
        setSelectedAccountRisk(riskResponse);
        const availableReasons = explainResponse?.reasons || [];
        const trimmedReasons = availableReasons.length > 3 ? availableReasons.slice(0, 3) : availableReasons;
        setSelectedAccountExplainability({
          ...explainResponse,
          reasons: trimmedReasons,
        });
        setSelectedAccountFeatures(featuresResponse);
        setSelectedReason(null);
        setSelectedEvidence(null);
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
    let active = true;

    async function loadFeed() {
      try {
        const result = await fetchRecentTransactions(12);
        if (!active) return;
        setLiveFeed(
          (result.transactions || []).map((tx) => ({
            transactionId: tx.transaction_id,
            timestamp: new Date(tx.timestamp).toLocaleString(),
            sender: tx.sender_account,
            receiver: tx.receiver_account,
            amount: `₹${Number(tx.amount).toLocaleString()}`,
          })),
        );
      } catch (feedError) {
        console.error('Failed to load live feed', feedError);
      }
    }

    loadFeed();
    if (!liveFeedEnabled) {
      return () => {
        active = false;
      };
    }

    const interval = setInterval(async () => {
      try {
        await triggerLiveTick(1);
        const result = await fetchRecentTransactions(12);
        if (!active) return;
        setLiveFeed(
          (result.transactions || []).map((tx) => ({
            transactionId: tx.transaction_id,
            timestamp: new Date(tx.timestamp).toLocaleString(),
            sender: tx.sender_account,
            receiver: tx.receiver_account,
            amount: `₹${Number(tx.amount).toLocaleString()}`,
          })),
        );
        const statsResult = await fetchGraphStats();
        if (!active) return;
        setGraphStats(statsResult.statistics);
      } catch (tickError) {
        console.error('Live feed tick failed', tickError);
      }
    }, 5000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [liveFeedEnabled]);

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
          <strong style={{ color: '#ef4444' }}>{highRiskCategoryCount}</strong>
          <p>{highRiskLoading ? 'Updating…' : 'Accounts flagged for review'}</p>
        </div>
        <div className="summary-chip">
          <span className="summary-chip-label">Low-risk accounts</span>
          <strong style={{ color: '#10b981' }}>{lowRiskCategoryCount}</strong>
          <p>Accounts with minimal risk signals</p>
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
        <aside className="panel-card risk-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid rgba(148, 163, 184, 0.3)', paddingBottom: '12px' }}>
            <button type="button" onClick={() => setSidebarTab('risk')} className={`ghost-button ${sidebarTab === 'risk' ? 'active-live' : ''}`} style={{ padding: '6px 8px', flex: 1, fontSize: '0.8rem' }}>Risk Queue</button>
            <button type="button" onClick={() => setSidebarTab('timeline')} className={`ghost-button ${sidebarTab === 'timeline' ? 'active-live' : ''}`} style={{ padding: '6px 8px', flex: 1, fontSize: '0.8rem' }}>Timeline</button>
            <button type="button" onClick={() => setSidebarTab('tracer')} className={`ghost-button ${sidebarTab === 'tracer' ? 'active-live' : ''}`} style={{ padding: '6px 8px', flex: 1, fontSize: '0.8rem' }}>Tracer</button>
            <button type="button" onClick={() => setSidebarTab('config')} className={`ghost-button ${sidebarTab === 'config' ? 'active-live' : ''}`} style={{ padding: '6px 8px', flex: 1, fontSize: '0.8rem', position: 'relative' }}>
              What-If
              {customWeights && <span style={{ position: 'absolute', top: 4, right: 4, width: 6, height: 6, borderRadius: '50%', background: '#f59e0b' }} />}
            </button>
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            {sidebarTab === 'risk' && (
              <HighRiskAccountsPanel
                accounts={highRiskAccounts}
                selectedAccount={selectedAccount}
                loading={highRiskLoading}
                error={highRiskError}
                onAccountSelect={handleAccountSelect}
              />
            )}
            {sidebarTab === 'timeline' && (
              <AccountTimeline accountId={selectedAccount} />
            )}
            {sidebarTab === 'tracer' && (
              <PathTracer 
                defaultSource={selectedAccount} 
                onPathFound={(result) => {
                  if (result && result.path_accounts) {
                    // Adapt PathTracer response to the format expected by the graph
                    setSelectedEvidence({
                      highlight_accounts: result.path_accounts,
                      highlight_transaction_ids: result.path.map(p => p.transaction_id)
                    });
                    setSelectedReason('path_tracer');
                  } else if (result && result.indicator === 'path_tracer') {
                     // For our custom PathTracer component shape
                     setSelectedEvidence(result.evidence);
                     setSelectedReason('path_tracer');
                  } else {
                    setSelectedEvidence(null);
                    setSelectedReason(null);
                  }
                }} 
              />
            )}
            {sidebarTab === 'config' && (
              <RiskConfigurator 
                onRiskRecalculated={(rankedAccounts, weights) => {
                  setHighRiskAccounts(rankedAccounts.slice(0, 16));
                  setHighRiskCategoryCount(rankedAccounts.filter(a => a.risk_level === 'HIGH').length);
                  setLowRiskCategoryCount(rankedAccounts.filter(a => a.risk_level === 'LOW').length);
                  // weights is null on Reset → revert to default scoring
                  setCustomWeights(weights ?? null);
                  setSidebarTab('risk');
                }}
              />
            )}
          </div>
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
            accountFeatures={selectedAccountFeatures}
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

      <section className="investigation-tools-grid">
        <div className="panel-card">
          <div className="live-feed-header">
            <TransactionFeed feed={liveFeed} />
            <button
              type="button"
              className={`ghost-button ${liveFeedEnabled ? 'active-live' : ''}`}
              onClick={() => setLiveFeedEnabled((current) => !current)}
              style={{ color: '#ef4444' }}
            >
              {liveFeedEnabled ? 'Stop live simulation' : 'Start live simulation'}
            </button>
          </div>
        </div>

        <div className="panel-card">
          <TypologyScanner 
            selectedAccount={selectedAccount}
            onAccountSelect={handleAccountSelect}
          />
        </div>
      </section>
    </div>
  );
}
