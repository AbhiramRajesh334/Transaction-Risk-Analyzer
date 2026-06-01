"""Pydantic schemas for risk API payloads."""

from pydantic import BaseModel


class RiskSchema(BaseModel):
    account_id: str
    score: int
    category: str
    reasons: list[str] = []
