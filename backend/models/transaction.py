"""Transaction domain model definitions."""

from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: str
