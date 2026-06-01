"""Pydantic schemas for account API payloads."""

from pydantic import BaseModel


class AccountSchema(BaseModel):
    account_id: str
    account_type: str
