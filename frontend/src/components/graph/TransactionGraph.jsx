// TransactionGraph.jsx
// Cytoscape integration for the investigation graph with a true neighborhood subgraph view.

import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { fetchFullGraph } from '../../api/graphApi';

if (coseBilkent) cytoscape.use(coseBilkent);

export default function TransactionGraph({ selectedAccount, selectedReason, selectedEvidence, onNodeSelect }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState(null);
  const [showFullNetwork, setShowFullNetwork] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function init() {
      try {
        const data = await fetchFullGraph();
        if (!mounted) return;
        setGraphData(data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to initialize graph', err);
      }
    }

    init();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const graph = graphData;
    if (!graph || !containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const activeAccount = selectedAccount || graph.nodes[0]?.id;
    const nodesById = new Map(graph.nodes.map((node) => [node.id, node]));
    const neighborIds = new Set();
    const incidentEdges = graph.edges.filter((edge) => edge.source === activeAccount || edge.target === activeAccount);

    incidentEdges.forEach((edge) => {
      if (edge.source !== activeAccount) neighborIds.add(edge.source);
      if (edge.target !== activeAccount) neighborIds.add(edge.target);
    });

    const subgraphNodes = [
      { data: { id: activeAccount, label: activeAccount, account_type: nodesById.get(activeAccount)?.account_type } },
      ...Array.from(neighborIds).map((id) => ({ data: { id, label: id, account_type: nodesById.get(id)?.account_type } })),
    ];

    const subgraphEdges = incidentEdges.map((edge) => ({ data: { id: edge.transaction_id, source: edge.source, target: edge.target, amount: edge.amount } }));

    const displayNodes = showFullNetwork
      ? graph.nodes.map((node) => ({ data: { id: node.id, label: node.id, account_type: node.account_type } }))
      : subgraphNodes;

    const displayEdges = showFullNetwork
      ? graph.edges.map((edge) => ({ data: { id: edge.transaction_id, source: edge.source, target: edge.target, amount: edge.amount } }))
      : subgraphEdges;

    const layoutConfig = showFullNetwork
      ? {
        name: 'grid',
        fit: true,
        padding: 100,
        avoidOverlap: true,
        avoidOverlapPadding: 24,
        nodeDimensionsIncludeLabels: true,
        rows: 4,
        cols: 5,
        animate: true,
        animationDuration: 700,
      }
      : (() => {
        const positions = {};
        positions[activeAccount] = { x: 0, y: 0 };
        const count = neighborIds.size;
        const radius = Math.max(240, count * 70);
        Array.from(neighborIds).forEach((neighborId, index) => {
          const angle = (Math.PI * 2 * index) / Math.max(count, 1);
          positions[neighborId] = {
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
          };
        });

        return {
          name: 'preset',
          positions,
          fit: true,
          padding: 100,
          animate: true,
          animationDuration: 500,
          randomize: false,
        };
      })();

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [...displayNodes, ...displayEdges],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#38bdf8',
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': 13,
            color: '#0f172a',
            'text-outline-width': 0,
            'text-wrap': 'wrap',
            'text-max-width': 100,
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.92,
            'text-background-shape': 'roundrectangle',
            'text-background-padding': '3px',
            width: 56,
            height: 56,
            'overlay-padding': 6,
            'z-index': 10,
          },
        },
        {
          selector: 'node[account_type = "Student"]',
          style: {
            'background-color': '#38bdf8',
            'border-width': 3,
            'border-color': '#7dd3fc',
          },
        },
        {
          selector: 'node[account_type = "Salaried"]',
          style: {
            'background-color': '#16a34a',
            'border-width': 3,
            'border-color': '#86efac',
          },
        },
        {
          selector: 'node[account_type = "Business"]',
          style: {
            'background-color': '#f59e0b',
            'border-width': 3,
            'border-color': '#fcd34d',
          },
        },
        {
          selector: 'node[account_type = "HighRisk"]',
          style: {
            'background-color': '#ef4444',
            'border-width': 4,
            'border-color': '#fecaca',
            width: 64,
            height: 64,
          },
        },
        {
          selector: 'node.center',
          style: {
            'background-color': '#facc15',
            'border-color': '#f59e0b',
            'border-width': 4,
            width: 72,
            height: 72,
            color: '#0f172a',
            'text-outline-color': '#f8fafc',
            'text-outline-width': 10,
          },
        },
        {
          selector: 'node.neighbor',
          style: {
            'background-color': '#38bdf8',
            width: 60,
            height: 60,
            'border-width': 4,
            'border-color': '#93c5fd',
          },
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            width: 4,
            opacity: 0.9,
          },
        },
        {
          selector: 'edge.incoming',
          style: {
            'line-color': '#34d399',
            'target-arrow-color': '#34d399',
            width: 4,
          },
        },
        {
          selector: 'edge.outgoing',
          style: {
            'line-color': '#60a5fa',
            'target-arrow-color': '#60a5fa',
            width: 4,
          },
        },
        {
          selector: 'node.faded',
          style: {
            opacity: 0.18,
          },
        },
        {
          selector: 'edge.faded',
          style: {
            opacity: 0.18,
          },
        },
        {
          selector: 'node.highlighted',
          style: {
            'background-color': '#f59e0b',
            'border-color': '#fbbf24',
            width: 88,
            height: 88,
            'z-index': 11,
          },
        },
        {
          selector: 'edge.highlighted',
          style: {
            'line-color': '#f59e0b',
            'target-arrow-color': '#f59e0b',
            width: 7,
            opacity: 1,
          },
        },
      ],
      layout: layoutConfig,
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
      wheelSensitivity: 0.2,
    });

    const cy = cyRef.current;
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onNodeSelect) onNodeSelect(node.id());
    });

    cy.batch(() => {
      cy.nodes().removeClass('center neighbor faded highlighted');
      cy.edges().removeClass('incoming outgoing faded highlighted');

      if (!showFullNetwork) {
        const centerNode = cy.getElementById(activeAccount);
        centerNode.addClass('center');
        const neighborNodes = centerNode.neighborhood('node');
        neighborNodes.addClass('neighbor');

        subgraphEdges.forEach((edgeData) => {
          const edge = cy.getElementById(edgeData.data.id);
          if (edge.data('target') === activeAccount) {
            edge.addClass('incoming');
          }
          if (edge.data('source') === activeAccount) {
            edge.addClass('outgoing');
          }
        });
      } else {
        cy.nodes().not(cy.getElementById(activeAccount)).addClass('faded');
      }

      if (selectedEvidence) {
        const highlightAccountIds = new Set(selectedEvidence.highlight_accounts || []);
        const highlightEdgeIds = new Set(selectedEvidence.highlight_transaction_ids || []);

        if (selectedReason === 'activity_spike') {
          highlightAccountIds.add(activeAccount);
          incidentEdges.forEach((edge) => highlightEdgeIds.add(edge.transaction_id));
        }

        if (selectedReason === 'counterparty_explosion' || selectedReason === 'suspicious_exposure') {
          highlightAccountIds.add(activeAccount);
          incidentEdges.forEach((edge) => {
            if (highlightAccountIds.has(edge.source) || highlightAccountIds.has(edge.target)) {
              highlightEdgeIds.add(edge.transaction_id);
            }
          });
        }

        Array.from(highlightAccountIds).forEach((nodeId) => {
          const node = cy.getElementById(nodeId);
          if (node) {
            node.removeClass('faded');
            node.addClass('highlighted');
          }
        });

        Array.from(highlightEdgeIds).forEach((edgeId) => {
          const edge = cy.getElementById(edgeId);
          if (edge) {
            edge.removeClass('faded');
            edge.addClass('highlighted');
          }
        });

        cy.nodes().forEach((node) => {
          if (!node.hasClass('highlighted')) {
            node.addClass('faded');
          }
        });

        cy.edges().forEach((edge) => {
          if (!edge.hasClass('highlighted')) {
            edge.addClass('faded');
          }
        });
      }
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graphData, selectedAccount, showFullNetwork, onNodeSelect, selectedReason, selectedEvidence]);

  const activeAccount = selectedAccount || graphData?.nodes?.[0]?.id || 'Loading';
  const neighborCount = graphData
    ? Array.from(
      new Set(
        graphData.edges.reduce((ids, edge) => {
          if (edge.source === activeAccount && edge.target !== activeAccount) ids.push(edge.target);
          if (edge.target === activeAccount && edge.source !== activeAccount) ids.push(edge.source);
          return ids;
        }, []),
      ),
    ).length
    : 0;
  const incidentEdges = graphData
    ? graphData.edges.filter((edge) => edge.source === activeAccount || edge.target === activeAccount)
    : [];
  const incomingEdgeCount = incidentEdges.filter((edge) => edge.target === activeAccount).length;
  const outgoingEdgeCount = incidentEdges.filter((edge) => edge.source === activeAccount).length;
  const totalEdgeCount = incidentEdges.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div className="graph-toolbar">
        <div className="graph-focus-label">
          Investigation Focus: {activeAccount} · Neighbors: {neighborCount} · Edges: {totalEdgeCount} · Incoming: {incomingEdgeCount} · Outgoing: {outgoingEdgeCount}
        </div>
        <button type="button" className="graph-toggle-button" onClick={() => setShowFullNetwork((current) => !current)}>
          {showFullNetwork ? 'Show Neighborhood View' : 'Show Full Network'}
        </button>
      </div>

      {loading && <div style={{ color: '#475569', marginBottom: 12 }}>Loading transaction network…</div>}

      {/* Graph canvas with floating controls and legend */}
      <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
        <div ref={containerRef} className="graph-canvas" style={{ width: '100%', height: '100%', borderRadius: 20, overflow: 'hidden' }} />

        {/* Floating zoom controls — top-right */}
        <div className="graph-zoom-controls">
          <button
            type="button"
            className="graph-zoom-btn"
            title="Zoom in"
            onClick={() => cyRef.current && cyRef.current.zoom({ level: cyRef.current.zoom() * 1.3, renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 } })}
          >＋</button>
          <button
            type="button"
            className="graph-zoom-btn"
            title="Zoom out"
            onClick={() => cyRef.current && cyRef.current.zoom({ level: cyRef.current.zoom() * 0.77, renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 } })}
          >－</button>
          <button
            type="button"
            className="graph-zoom-btn"
            title="Fit to screen"
            onClick={() => cyRef.current && cyRef.current.fit(undefined, 40)}
          >⊡</button>
        </div>

        {/* Legend — bottom-left */}
        <div className="graph-legend">
          <div className="graph-legend-row"><span className="graph-legend-dot" style={{ background: '#facc15', borderColor: '#f59e0b' }} />Focus account</div>
          <div className="graph-legend-row"><span className="graph-legend-dot" style={{ background: '#38bdf8', borderColor: '#93c5fd' }} />Neighbor</div>
          <div className="graph-legend-row"><span className="graph-legend-dot" style={{ background: '#ef4444', borderColor: '#fecaca' }} />High-Risk</div>
          <div className="graph-legend-row"><span className="graph-legend-dot" style={{ background: '#16a34a', borderColor: '#86efac' }} />Salaried</div>
          <div className="graph-legend-row"><span className="graph-legend-dot" style={{ background: '#f59e0b', borderColor: '#fcd34d' }} />Business</div>
          <div className="graph-legend-divider" />
          <div className="graph-legend-row"><span className="graph-legend-edge" style={{ background: '#34d399' }} />Incoming</div>
          <div className="graph-legend-row"><span className="graph-legend-edge" style={{ background: '#60a5fa' }} />Outgoing</div>
        </div>
      </div>
    </div>
  );
}
