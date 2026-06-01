"""Risk scoring domain model definitions."""

from pydantic import BaseModel


class RiskScore(BaseModel):
    account_id: str
    score: int
    category: str
    reasons: list[str] = []
