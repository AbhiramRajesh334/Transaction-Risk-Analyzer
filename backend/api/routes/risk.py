"""Risk-related API routes for final risk scoring."""

from fastapi import APIRouter, HTTPException
from typing import List

from services.risk_scoring_service import (
    get_risk_for_account,
    get_risk_for_all,
    get_high_risk_accounts,
    get_top_accounts,
)
from services.account_service import list_accounts
from schemas.risk_score import RiskScoreModel

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/account/{account_id}", response_model=RiskScoreModel)
def get_risk_for_account_route(account_id: str):
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_risk_for_account(account_id)


@router.get("/all", response_model=List[RiskScoreModel])
def get_risk_for_all_route():
    return get_risk_for_all()


@router.get("/high-risk", response_model=List[RiskScoreModel])
def get_high_risk_route():
    return get_high_risk_accounts()


@router.get("/top-10", response_model=List[RiskScoreModel])
def get_top_10_route(limit: int = 10):
    return get_top_accounts(limit=limit)
