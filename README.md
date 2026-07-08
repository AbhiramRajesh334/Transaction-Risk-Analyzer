# Explainable Transaction Behavior and Relationship Risk Analyzer

This project is a full-stack platform for explainable financial transaction monitoring and account risk analysis.

## Purpose

The system ingests transaction streams, builds a dynamic account graph, computes risk indicators, and surfaces clear, evidence-backed explanations for every risk score. By moving beyond "black-box" risk models, this tool allows investigators to visually trace the exact transaction networks and behavioral patterns that trigger alerts.

## Key Features

- **Live Transaction Simulation**: An interactive live feed that streams simulated transactions, updating risk indicators in real-time.
- **Network Graph Visualization**: Interactive graph interface built with Cytoscape. Investigators can explore an account's neighborhood, trace incoming/outgoing flows, and visualize full network topologies.
- **Evidence-Backed Explainability**: Transparent risk scoring that breaks down exactly *why* an account is flagged. Highlights include pass-through ratios, counterparty explosions, and circular flows.
- **High-Risk Queue**: Automated prioritization of accounts based on behavioral and relational anomalies.
- **Risk Configurator**: Interactive UI to customize risk thresholds and indicator weights on the fly.
- **Dark Mode Support**: Comprehensive dark mode for improved accessibility and prolonged monitoring sessions.

## Architecture & Data Structures

The system architecture bridges a high-performance analytics backend with a rich frontend UI.

- **Backend**: Python + FastAPI
- **Frontend**: React + Vite
- **Database**: SQLite for relational persistence (SQLAlchemy)

### Core Data Structures

- **Directed Multi-Graph (`nx.MultiDiGraph`)**: At the heart of the engine lies a NetworkX directed multi-graph. 
  - **Nodes** represent individual accounts.
  - **Edges** represent individual transactions. 
  - A *Multi-Graph* is essential here because two identical accounts can have multiple separate transactions between them over time, which must be stored as distinct edges.
- **Adjacency Lists**: Used implicitly by NetworkX for extremely fast O(1) neighbor lookups (both predecessors and successors) during subgraph rendering and traversal.
- **Relational Tables**: Persistent storage of `accounts`, `transactions`, and `features` using standard SQL tables to support historical queries and graph initialization.

## Algorithms

The risk and explainability engines rely heavily on graph theory and behavioral pattern detection algorithms:

- **Shortest Path Traversal**: Uses Dijkstra's algorithm (via NetworkX) to find the shortest fund-flow path between two accounts (up to a bounded maximum depth). This is critical for tracing how quickly money moves from a suspicious source to a target.
- **Bounded Cycle Detection**: Employs a constrained Depth-First Search (DFS) / neighborhood iteration algorithm to identify short, closed, directed cycles (e.g., A → B → C → A). This algorithm specifically targets "round-tripping" and circular money laundering patterns.
- **Degree Centrality Analysis**: Evaluates node degree (both in-degree and out-degree) to quickly flag "Counterparty Explosions"—scenarios where an account suddenly transacts with an unusually high number of unique partners.
- **Behavioral Ratio Computation**: Time-windowed aggregations that calculate heuristics like *Rapid Pass-Through*. By comparing the volume of incoming funds to outgoing funds within tight time constraints, the engine identifies accounts acting as mere conduits for illicit money flow.

## Getting Started

To run the application locally:
1. Start the FastAPI backend: `cd backend && uvicorn main:app --reload`
2. Start the React frontend: `cd frontend && npm run dev`
