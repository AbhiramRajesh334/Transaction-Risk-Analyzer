"""Pydantic schemas for explainability evidence payloads."""

from pydantic import BaseModel


class EvidenceSchema(BaseModel):
    indicator: str
    description: str
    evidence_items: list[dict] = []
