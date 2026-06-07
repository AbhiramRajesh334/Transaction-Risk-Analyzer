"""API router registration package."""

from fastapi import APIRouter

from .routes.transactions import router as transactions_router
from .routes.accounts import router as accounts_router
from .routes.graph import router as graph_router
from .routes.risk import router as risk_router
from .routes.explainability import router as explainability_router
from .routes.simulation import router as simulation_router
from .routes.features import router as features_router
from .routes.indicators import router as indicators_router
from .routes.evaluation import router as evaluation_router

api_router = APIRouter()
api_router.include_router(transactions_router)
api_router.include_router(accounts_router)
api_router.include_router(graph_router)
api_router.include_router(risk_router)
api_router.include_router(explainability_router)
api_router.include_router(simulation_router)
api_router.include_router(features_router)
api_router.include_router(indicators_router)
api_router.include_router(evaluation_router)
