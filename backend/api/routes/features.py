"""API routes exposing behavioral feature engine outputs."""

from fastapi import APIRouter, HTTPException
from typing import List

from services.behavioral_feature_service import (
    get_features_for_account,
    get_all_features,
    get_top_activity,
    get_top_counterparties,
)
from services.account_service import list_accounts
from schemas.behavioral_features import BehavioralFeatures

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/account/{account_id}", response_model=BehavioralFeatures)
def get_account_features(account_id: str):
    # Ensure the account exists in the accounts table. If it does not exist,
    # return 404. If it exists but has no transactions, the service will
    # return a zero-filled feature record.
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_features_for_account(account_id)


@router.get("/all", response_model=List[BehavioralFeatures])
def get_features_all():
    return get_all_features()


@router.get("/top-activity", response_model=List[BehavioralFeatures])
def get_top_by_activity(limit: int = 10):
    return get_top_activity(limit=limit)


@router.get("/top-counterparties", response_model=List[BehavioralFeatures])
def get_top_by_counterparties(limit: int = 10):
    return get_top_counterparties(limit=limit)
