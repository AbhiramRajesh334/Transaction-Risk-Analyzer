# Explainable Transaction Behavior and Relationship Risk Analyzer

This project is a full-stack platform for explainable financial transaction monitoring and account risk analysis.

## Purpose

The system ingests transaction streams, builds a dynamic account graph, computes risk indicators, and surfaces clear, evidence-backed explanations for every risk score. By moving beyond "black-box" risk models, this tool allows investigators to visually trace the exact transaction networks and behavioral patterns that trigger alerts, improving the efficiency and accuracy of investigations into money laundering, fraud, and structured financing.

---

## System Architecture and Flow

The architecture bridges a high-performance analytics backend with a rich, interactive frontend UI, emphasizing real-time processing and explainability.

### Flow
1. **Data Ingestion & Simulation**: The backend utilizes a simulation engine that streams realistic financial transaction scenarios (e.g., structuring, rapid pass-through, ghost account reactivation) into the system. 
2. **Graph Construction**: As transactions stream in, they are immediately ingested into an in-memory graph representation and saved to relational storage.
3. **Risk Scoring Engine**: Event-driven rules evaluate each transaction and node state against multiple behavioral and relational heuristics. 
4. **Explainability Module**: Once a high-risk entity is flagged, the explainability module traces back the exact sub-graphs, pathways, and metrics that contributed to the score, preparing a human-readable justification.
5. **Frontend Delivery**: The React frontend pulls data via REST/WebSocket, rendering a live investigation dashboard and interactive network graph (via Cytoscape) where analysts can visually explore the flagged behavior.

### Tech Stack
- **Backend**: Python + FastAPI
- **Frontend**: React + Vite
- **Database**: SQLite for relational persistence (SQLAlchemy) + In-Memory Graph structures

---

## Detailed Features

- **Live Transaction Simulation**: An interactive live feed that streams simulated transactions with complex scenarios (like *fan-out cash-out* and *layering*), updating risk indicators in real-time.
- **Investigation Dashboard & Network Graph**: A comprehensive dashboard featuring an interactive graph interface built with Cytoscape. Investigators can explore an account's neighborhood, trace incoming/outgoing flows, and visualize full network topologies dynamically.
- **Evidence-Backed Explainability**: Transparent risk scoring that breaks down exactly *why* an account is flagged. The platform surfaces metrics such as pass-through ratios, counterparty explosions, and circular flows rather than a single opaque score.
- **High-Risk Queue**: Automated prioritization of accounts based on behavioral and relational anomalies, allowing investigators to focus on the highest-threat nodes first.
- **Risk Configurator**: Interactive UI to customize risk thresholds, indicator weights, and time windows on the fly.
- **Modern UI & Dark Mode**: Comprehensive dark mode for improved accessibility and prolonged monitoring sessions with a clean, modern aesthetic.

---

## Data Structures

The application relies heavily on graph data structures to map financial networks effectively:

- **Directed Multi-Graph (`nx.MultiDiGraph`)**: At the heart of the engine lies a NetworkX directed multi-graph. 
  - **Nodes** represent individual accounts, maintaining state such as total volume and risk score.
  - **Edges** represent individual transactions, carrying metadata like amount, timestamp, and transaction type. 
  - A *Multi-Graph* is essential because two identical accounts can transact multiple times over varying periods; these must be stored as distinct, time-stamped edges.
- **Adjacency Lists**: Used implicitly by NetworkX for extremely fast O(1) neighbor lookups (both predecessors and successors) during subgraph rendering and traversal.
- **Relational Tables**: Persistent storage of `accounts`, `transactions`, and `features` using standard SQL tables (via SQLAlchemy) to support historical queries, fast filtering, and graph initialization.
- **In-Memory Caches & Queues**: Utilized for streaming transactions and maintaining the high-risk priority queues without taxing the relational database.

---

## Algorithms Used

The risk and explainability engines rely heavily on graph theory and behavioral pattern detection algorithms:

- **Shortest Path Traversal**: Uses Dijkstra's algorithm (via NetworkX) to find the shortest fund-flow path between two accounts (up to a bounded maximum depth). This is critical for tracing how quickly money moves from a suspicious source to a target.
- **Bounded Cycle Detection**: Employs a constrained Depth-First Search (DFS) / neighborhood iteration algorithm to identify short, closed, directed cycles (e.g., A → B → C → A). This specifically targets "round-tripping" and circular money laundering patterns.
- **Degree Centrality Analysis**: Evaluates node degree (both in-degree and out-degree) to quickly flag "Counterparty Explosions"—scenarios where an account suddenly transacts with an unusually high number of unique partners.
- **Graph Clustering & Subgraph Extraction**: Extracts k-hop ego graphs around high-risk nodes to render localized contexts for the investigators without loading the entire network.
- **Behavioral Ratio Computation**: Time-windowed aggregations that calculate heuristics like *Rapid Pass-Through*. By comparing the volume of incoming funds to outgoing funds within tight time constraints, the engine identifies accounts acting as mere conduits for illicit money flow.

---

## Methodology

The core methodology revolves around **Heuristic-Driven Graph Analytics** combined with **Explainable AI (XAI) principles**:

1. **Scenario-Based Modeling**: Instead of relying solely on black-box ML models, the system simulates and detects well-known AML (Anti-Money Laundering) typologies (e.g., Structuring, Layered Pass-Through, Ghost Account Reactivation, Amount Anomalies).
2. **Temporal Analysis**: Analyzes transactions within sliding time windows to detect sudden spikes in activity, rapid fund movement, or changes in behavior over time.
3. **Traceability**: Every risk flag is explicitly tied to a specific sub-graph pattern or metric threshold (e.g., "Flagged because out-degree increased by 500% in 24 hours"). This ensures that investigators have actionable evidence to present to regulators or compliance teams.
4. **Human-in-the-Loop**: The system is designed to augment human intelligence. The UI empowers the investigator to adjust weights, dive into visualizations, and ultimately make the final determination based on the provided evidence.

---

## Getting Started

To run the application locally:
1. Start the FastAPI backend: `cd backend && uvicorn main:app --reload`
2. Start the React frontend: `cd frontend && npm run dev`
