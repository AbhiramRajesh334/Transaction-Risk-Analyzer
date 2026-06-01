"""Account domain model definitions."""

from pydantic import BaseModel


class Account(BaseModel):
    account_id: str
    account_type: str
    created_at: str
