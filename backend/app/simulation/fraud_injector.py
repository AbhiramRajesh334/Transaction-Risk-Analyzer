"""Fraud scenario injection engine that operates on top of normal synthetic datasets."""

from datetime import datetime
from typing import List

from app.simulation.scenarios.activity_spike import inject_activity_spike
from app.simulation.scenarios.amount_anomaly import inject_amount_anomaly
from app.simulation.scenarios.rapid_pass_through import inject_rapid_pass_through
from app.simulation.scenarios.counterparty_explosion import inject_counterparty_explosion
from app.simulation.scenarios.suspicious_exposure import inject_suspicious_exposure
from database.database import get_db_connection, insert_ground_truth_entries
from services.account_service import insert_accounts, list_accounts
from services.transaction_service import insert_transactions, list_transactions

SCENARIO_MODULES = {
    "activity_spike": inject_activity_spike,
    "amount_anomaly": inject_amount_anomaly,
    "rapid_pass_through": inject_rapid_pass_through,
    "counterparty_explosion": inject_counterparty_explosion,
    "suspicious_exposure": inject_suspicious_exposure,
}


def _next_transaction_index(transactions: list[dict]) -> int:
    if not transactions:
        return 1
    max_id = max(int(tx["transaction_id"].replace("TX", "")) for tx in transactions)
    return max_id + 1


def inject_scenarios(selected_scenarios: List[str] | None = None) -> dict:
    """Inject fraud scenarios into the current synthetic dataset."""
    if selected_scenarios is None:
        selected_scenarios = list(SCENARIO_MODULES.keys())

    accounts = list_accounts()
    transactions = list_transactions()

    if len(accounts) < 3:
        raise ValueError("At least three accounts must exist to inject fraud scenarios.")

    next_tx_index = _next_transaction_index(transactions)
    injected_summary = []
    inserted_transactions = []
    inserted_ground_truth = []
    new_accounts = []

    for scenario_name in selected_scenarios:
        if scenario_name not in SCENARIO_MODULES:
            raise ValueError(f"Unknown scenario type: {scenario_name}")

        scenario_executor = SCENARIO_MODULES[scenario_name]
        result = scenario_executor(accounts, transactions, next_tx_index)

        next_tx_index = result["next_transaction_index"]
        injected_transactions.extend(result.get("transactions", []))
        inserted_ground_truth.extend(result.get("ground_truth_entries", []))

        if result.get("new_accounts"):
            insert_accounts(result["new_accounts"])
            new_accounts.extend(result["new_accounts"])
            accounts.extend(result["new_accounts"])

        transactions.extend(result.get("transactions", []))

        injected_summary.append(
            {
                "scenario_type": scenario_name,
                "created_transactions": len(result.get("transactions", [])),
                "ground_truth_records": len(result.get("ground_truth_entries", [])),
            }
        )

    if injected_transactions:
        insert_transactions(injected_transactions)

    if inserted_ground_truth:
        insert_ground_truth_entries(inserted_ground_truth)

    return {
        "summary": injected_summary,
        "created_transactions": len(injected_transactions),
        "created_ground_truth": len(inserted_ground_truth),
        "new_accounts": new_accounts,
    }


def list_ground_truth() -> list[dict]:
    """Return all ground truth scenario records."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, account_id, scenario_type, description, created_at FROM ground_truth_scenarios ORDER BY id"
    )
    return [dict(row) for row in cursor.fetchall()]
