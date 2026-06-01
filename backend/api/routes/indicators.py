"""Indicator-related API routes."""

from fastapi import APIRouter, HTTPException
from typing import List

from services.risk_indicator_service import (
    get_indicators_for_account,
    get_all_indicators,
    get_top_activity_spike,
    get_top_pass_through,
    get_top_counterparty_explosion,
    get_top_exposure,
)
from services.account_service import list_accounts
from schemas.risk_indicators import RiskIndicators

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/account/{account_id}", response_model=RiskIndicators)
def get_account_indicators(account_id: str):
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_indicators_for_account(account_id)


@router.get("/all", response_model=List[RiskIndicators])
def get_all_indicators_route():
    return get_all_indicators()


@router.get("/top-activity-spike", response_model=List[RiskIndicators])
def get_top_activity_spike_route(limit: int = 10):
    return get_top_activity_spike(limit=limit)


@router.get("/top-pass-through", response_model=List[RiskIndicators])
def get_top_pass_through_route(limit: int = 10):
    return get_top_pass_through(limit=limit)


@router.get("/top-counterparty-explosion", response_model=List[RiskIndicators])
def get_top_counterparty_explosion_route(limit: int = 10):
    return get_top_counterparty_explosion(limit=limit)


@router.get("/top-exposure", response_model=List[RiskIndicators])
def get_top_exposure_route(limit: int = 10):
    return get_top_exposure(limit=limit)
