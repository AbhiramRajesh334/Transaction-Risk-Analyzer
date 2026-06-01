# Explainable Transaction Behavior and Relationship Risk Analyzer

This project is a full-stack platform for explainable financial transaction monitoring and account risk analysis.

## Purpose

The system ingests transaction streams, builds a dynamic account graph, computes risk indicators, and surfaces clear, evidence-backed explanations for every risk score.

## Architecture Overview

- **Backend**: Python + FastAPI for API endpoints, risk engines, synthetic data generation, and graph services.
- **Frontend**: React + Vite for an interactive dashboard, transaction feed, graph visualization, and explainability panels.
- **Database**: SQLite for lightweight persistence and seeded synthetic data.
- **Graph Layer**: NetworkX provides the transaction graph foundation.

## Folder Structure

- `backend/` — FastAPI application, service layers, risk and explainability engines, simulation utilities.
- `frontend/` — React application with pages, components, hooks, and API clients.
- `docs/` — Architecture, API design, and system design documentation.
- `scripts/` — Utility scripts for development and project maintenance.
- `tests/` — Placeholder test suites for backend and frontend.

## Getting Started

This repository currently contains a scaffolded architecture and placeholder files for the first development phase.

## Notes

- The backend now includes a synthetic data generation layer for accounts and transactions.
- The SQLite persistence layer is initialized on startup and stores `accounts` and `transactions`.
- API simulation endpoints are available under `/api/simulation`.
- No fraud detection, risk scoring, graph algorithms, or UI logic are implemented yet.

