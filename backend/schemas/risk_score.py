"""Pydantic schema definitions for final risk scoring API responses."""

from pydantic import BaseModel
from typing import Any, Dict, List


class IndicatorBreakdown(BaseModel):
    score: int
    evidence: Dict[str, Any]


class RiskScoreModel(BaseModel):
    account_id: str
    risk_score: int
    risk_level: str
    top_reasons: List[str]
    indicator_breakdown: Dict[str, IndicatorBreakdown]

    class Config:
        schema_extra = {
            "example": {
                "account_id": "A205",
                "risk_score": 92,
                "risk_level": "HIGH",
                "top_reasons": [
                    "Pass Through",
                    "Activity Spike"
                ],
                "indicator_breakdown": {
                    "activity_spike": {
                        "score": 82,
                        "evidence": {
                            "transaction_count": 14,
                            "velocity": 1.2,
                            "recent_activity_count": 8,
                        },
                    },
                    "amount_anomaly": {
                        "score": 12,
                        "evidence": {
                            "average_amount": 4200.0,
                            "max_amount": 250000.0,
                        },
                    },
                    "pass_through": {
                        "score": 88,
                        "evidence": {
                            "incoming_amount": 320000.0,
                            "outgoing_amount": 315000.0,
                            "pass_through_ratio": 0.98,
                        },
                    },
                    "counterparty_explosion": {
                        "score": 25,
                        "evidence": {
                            "unique_counterparties": 4,
                            "in_degree": 3,
                            "out_degree": 2,
                        },
                    },
                    "suspicious_exposure": {
                        "score": 41,
                        "evidence": {
                            "neighbor_count": 6,
                            "suspicious_neighbor_count": 2,
                            "average_neighbor_risk": 52.1,
                        },
                    },
                },
            }
        }
