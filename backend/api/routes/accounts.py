"""Account-related API routes."""

from fastapi import APIRouter
from services.account_service import list_accounts

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/")
def get_accounts():
    return {"accounts": list_accounts()}
