"""Transaction-related API routes."""

from fastapi import APIRouter, Query
from services.transaction_service import list_transactions

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/")
def get_transactions():
    return {"transactions": list_transactions()}


@router.get("/recent")
def get_recent_transactions(
    limit: int = Query(20, ge=1, le=100),
    after_id: str | None = Query(None, description="Return transactions after this transaction ID."),
):
    transactions = list_transactions()
    if after_id:
        ids = [tx["transaction_id"] for tx in transactions]
        if after_id in ids:
            start_index = ids.index(after_id) + 1
            transactions = transactions[start_index:]

    recent = transactions[-limit:]
    return {
        "transactions": recent,
        "latest_id": recent[-1]["transaction_id"] if recent else after_id,
        "total_count": len(list_transactions()),
    }
