"""Explainability-related API routes."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from services.account_service import list_accounts
from services.explainability_service import (
    get_explanation_for_account,
    get_high_risk_explanations,
)
from schemas.explainability import ExplainabilityModel

router = APIRouter(prefix="/explanations", tags=["explainability"])


@router.get("/account/{account_id}", response_model=ExplainabilityModel)
def get_explanation_for_account_route(account_id: str):
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_explanation_for_account(account_id)


class ExplainabilityWithWeightsRequest(BaseModel):
    weights: Optional[dict] = None


@router.post("/account/{account_id}", response_model=ExplainabilityModel)
def get_explanation_with_weights_route(account_id: str, req: ExplainabilityWithWeightsRequest):
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_explanation_for_account(account_id, custom_weights=req.weights)


@router.get("/high-risk", response_model=List[ExplainabilityModel])
def get_high_risk_explanations_route():
    return get_high_risk_explanations()
