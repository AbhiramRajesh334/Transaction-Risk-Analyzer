"""Pydantic schemas for transaction API payloads."""

from pydantic import BaseModel


class TransactionSchema(BaseModel):
    transaction_id: str
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: str
