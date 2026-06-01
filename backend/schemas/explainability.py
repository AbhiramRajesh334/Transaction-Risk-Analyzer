"""Pydantic schema definitions for explainability API responses."""

from pydantic import BaseModel
from typing import Any, Dict, List


class ExplanationEntry(BaseModel):
    indicator: str
    score: int
    explanation: str
    evidence: Dict[str, Any]


class ExplainabilityModel(BaseModel):
    account_id: str
    risk_score: int
    top_reasons: List[str]
    reasons: List[ExplanationEntry]

    class Config:
        schema_extra = {
            "example": {
                "account_id": "A205",
                "risk_score": 92,
                "top_reasons": [
                    "Rapid Pass Through",
                    "Activity Spike"
                ],
                "reasons": [
                    {
                        "indicator": "Rapid Pass Through",
                        "score": 88,
                        "explanation": "The account received 50,000.00 and forwarded 49,500.00, producing a pass-through ratio of 0.99. Such a high ratio is suspicious because it suggests funds are quickly routed through the account.",
                        "evidence": {
                            "incoming_amount": 50000.0,
                            "outgoing_amount": 49500.0,
                            "pass_through_ratio": 0.99,
                            "components": {
                                "amount_score": 98,
                                "ratio_score": 100
                            }
                        }
                    }
                ]
            }
        }
