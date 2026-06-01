"""Pydantic schema definitions for behavioral features API responses."""

from pydantic import BaseModel
from typing import Optional


class BehavioralFeatures(BaseModel):
    account_id: str
    transaction_count: int
    incoming_count: int
    outgoing_count: int
    incoming_amount: float
    outgoing_amount: float
    average_amount: float
    max_amount: float
    unique_counterparties: int
    in_degree: int
    out_degree: int
    velocity: float
    pass_through_ratio: Optional[float]
    recent_activity_count: int

    class Config:
        schema_extra = {
            "example": {
                "account_id": "A205",
                "transaction_count": 14,
                "incoming_count": 9,
                "outgoing_count": 5,
                "incoming_amount": 320000.0,
                "outgoing_amount": 315000.0,
                "average_amount": 4200.0,
                "max_amount": 250000.0,
                "unique_counterparties": 4,
                "in_degree": 3,
                "out_degree": 2,
                "velocity": 1.5,
                "pass_through_ratio": 0.984,
                "recent_activity_count": 8,
            }
        }
