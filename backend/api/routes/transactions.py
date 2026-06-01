"""Transaction-related API routes."""

from fastapi import APIRouter
from services.transaction_service import list_transactions

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/")
def get_transactions():
    return {"transactions": list_transactions()}
