"""Simulation endpoints for synthetic account and transaction generation."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.account_service import count_accounts, insert_accounts, list_accounts
from services.transaction_service import count_transactions, insert_transactions
from simulation.account_generator import generate_accounts
from simulation.transaction_generator import generate_transactions
from app.simulation.fraud_injector import inject_scenarios, list_ground_truth
from database.database import clear_demo_data
from simulation.demo_generator import generate_demo_dataset
from graph_engine.graph_manager import graph_manager

router = APIRouter(prefix="/simulation", tags=["simulation"])


class AccountGenerationRequest(BaseModel):
    number_of_accounts: int = Field(..., gt=0, description="Number of synthetic accounts to create.")


class TransactionGenerationRequest(BaseModel):
    number_of_transactions: int = Field(
        ..., gt=0, description="Number of synthetic transactions to create."
    )


class FraudInjectionRequest(BaseModel):
    scenarios: list[str] | None = Field(
        default=None,
        description="Optional list of fraud scenario types to inject. If omitted, all scenarios are injected.",
    )


@router.post("/accounts")
def generate_synthetic_accounts(request: AccountGenerationRequest):
    existing_count = count_accounts()
    accounts = generate_accounts(request.number_of_accounts, start_index=existing_count + 1)
    inserted = insert_accounts(accounts)
    return {
        "created_accounts": inserted,
        "total_accounts": existing_count + inserted,
        "accounts": accounts,
    }


@router.post("/transactions")
def generate_synthetic_transactions(request: TransactionGenerationRequest):
    accounts = list_accounts()
    if len(accounts) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two accounts are required before generating transactions.",
        )

    existing_tx_count = count_transactions()
    transactions = generate_transactions(
        accounts, request.number_of_transactions, start_index=existing_tx_count + 1
    )
    inserted = insert_transactions(transactions)
    return {
        "created_transactions": inserted,
        "total_transactions": existing_tx_count + inserted,
        "transactions": transactions,
    }


@router.post("/inject-fraud")
def inject_fraud(request: FraudInjectionRequest):
    try:
        result = inject_scenarios(request.scenarios)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return result


@router.get("/ground-truth")
def get_ground_truth():
    return {"ground_truth": list_ground_truth()}


@router.post("/generate-demo")
def generate_demo():
    """Create a realistic demo dataset and inject five fraud scenarios, then refresh the graph."""
    summary = generate_demo_dataset()
    graph_manager.refresh_graph()
    return {"demo_summary": summary, "graph_stats": {"nodes": graph_manager.get_graph().number_of_nodes(), "edges": graph_manager.get_graph().number_of_edges()}}


@router.post("/reset-demo")
def reset_demo():
    """Clear existing demo data, rebuild a realistic dataset, and refresh the graph."""
    clear_demo_data()
    summary = generate_demo_dataset()
    graph_manager.refresh_graph()
    return {"demo_summary": summary, "graph_stats": {"nodes": graph_manager.get_graph().number_of_nodes(), "edges": graph_manager.get_graph().number_of_edges()}}
