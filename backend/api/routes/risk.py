"""Risk-related API routes for final risk scoring."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional as Opt

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


class AccountRiskWithWeightsRequest(BaseModel):
    weights: Opt[dict] = None

@router.post("/account/{account_id}", response_model=RiskScoreModel)
def get_risk_for_account_with_weights_route(account_id: str, req: AccountRiskWithWeightsRequest):
    accounts = {a["account_id"] for a in list_accounts()}
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found.")
    return get_risk_for_account(account_id, custom_weights=req.weights)


@router.get("/all", response_model=List[RiskScoreModel])
def get_risk_for_all_route():
    return get_risk_for_all()


@router.get("/high-risk", response_model=List[RiskScoreModel])
def get_high_risk_route():
    return get_high_risk_accounts()


@router.get("/top-10", response_model=List[RiskScoreModel])
def get_top_10_route(limit: int = 10):
    return get_top_accounts(limit=limit)


class RecalculateRequest(BaseModel):
    weights: dict = Field(..., description="Custom weights for risk recalculation")

@router.post("/recalculate", response_model=List[RiskScoreModel])
def recalculate_risk_route(req: RecalculateRequest):
    # Return all accounts sorted by score so the full queue updates.
    all_accounts = get_risk_for_all(custom_weights=req.weights)
    return sorted(all_accounts, key=lambda a: a["risk_score"], reverse=True)


from services.risk_indicator_service import (
    get_top_activity_spike,
    get_top_pass_through,
    get_top_counterparty_explosion,
    get_top_exposure,
    get_top_round_tripping,
    get_top_structuring,
    get_top_circular_flow,
    get_top_amount_anomaly
)

@router.get("/typology/{typology_name}")
def get_typology_top_accounts(typology_name: str, limit: int = 10):
    mapping = {
        "activity_spike": get_top_activity_spike,
        "amount_anomaly": get_top_amount_anomaly,
        "pass_through": get_top_pass_through,
        "counterparty_explosion": get_top_counterparty_explosion,
        "round_tripping": get_top_round_tripping,
        "structuring": get_top_structuring,
        "circular_flow": get_top_circular_flow,
        "suspicious_exposure": get_top_exposure,
    }
    
    if typology_name not in mapping:
        raise HTTPException(status_code=400, detail="Invalid typology name")
        
    results = mapping[typology_name](limit=limit)
    
    # Extract only the necessary info for the scanner
    formatted = []
    for item in results:
        score = item[typology_name]["score"]
        if score > 0:
            formatted.append({
                "account_id": item["account_id"],
                "score": score,
                "evidence": item[typology_name].get("evidence", {})
            })
            
    return formatted
