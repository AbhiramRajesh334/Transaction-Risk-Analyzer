"""Account-type baselines for relative anomaly scoring."""

from typing import Dict, Optional

from services.account_service import list_accounts
from services.behavioral_feature_service import get_all_features, refresh_if_needed

# Expected norms per account type (fallback when sample size is small).
TYPE_DEFAULTS = {
    "Student": {
        "transaction_count": 4.0,
        "velocity": 0.5,
        "recent_activity_count": 2.0,
        "average_amount": 80.0,
        "max_amount": 150.0,
        "unique_counterparties": 3.0,
        "incoming_amount": 200.0,
        "outgoing_amount": 200.0,
    },
    "Salaried": {
        "transaction_count": 5.0,
        "velocity": 0.8,
        "recent_activity_count": 3.0,
        "average_amount": 300.0,
        "max_amount": 500.0,
        "unique_counterparties": 5.0,
        "incoming_amount": 800.0,
        "outgoing_amount": 1200.0,
    },
    "Business": {
        "transaction_count": 6.0,
        "velocity": 1.0,
        "recent_activity_count": 4.0,
        "average_amount": 1500.0,
        "max_amount": 4000.0,
        "unique_counterparties": 8.0,
        "incoming_amount": 5000.0,
        "outgoing_amount": 8000.0,
    },
    "HighRisk": {
        "transaction_count": 8.0,
        "velocity": 2.0,
        "recent_activity_count": 5.0,
        "average_amount": 2000.0,
        "max_amount": 8000.0,
        "unique_counterparties": 6.0,
        "incoming_amount": 10000.0,
        "outgoing_amount": 10000.0,
    },
}

_cache: Dict[str, dict] = {}
_account_types: Dict[str, str] = {}


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _compute_type_baselines(features: list[dict], account_types: Dict[str, str]) -> Dict[str, dict]:
    grouped: Dict[str, list[dict]] = {}
    for entry in features:
        account_type = account_types.get(entry["account_id"], "Salaried")
        grouped.setdefault(account_type, []).append(entry)

    baselines: Dict[str, dict] = {}
    metric_keys = list(TYPE_DEFAULTS["Salaried"].keys())

    for account_type, entries in grouped.items():
        baselines[account_type] = {}
        for key in metric_keys:
            values = [float(entry.get(key) or 0) for entry in entries if entry.get(key) is not None]
            baselines[account_type][key] = _median(values) if values else TYPE_DEFAULTS.get(account_type, TYPE_DEFAULTS["Salaried"])[key]

    for account_type, defaults in TYPE_DEFAULTS.items():
        baselines.setdefault(account_type, defaults.copy())

    return baselines


def refresh_baselines() -> Dict[str, dict]:
    global _cache, _account_types
    refresh_if_needed()
    _account_types = {account["account_id"]: account["account_type"] for account in list_accounts()}
    _cache = _compute_type_baselines(get_all_features(), _account_types)
    return _cache


def get_type_baselines() -> Dict[str, dict]:
    if not _cache:
        refresh_baselines()
    return _cache


def get_account_type(account_id: str) -> str:
    if not _account_types:
        refresh_baselines()
    return _account_types.get(account_id, "Salaried")


def get_baseline_for_account(account_id: str) -> dict:
    baselines = get_type_baselines()
    account_type = get_account_type(account_id)
    return baselines.get(account_type, TYPE_DEFAULTS["Salaried"])


def relative_ratio(value: float, baseline: float, floor: float = 1.0) -> float:
    """Return how many times above baseline the value is (1.0 = normal)."""
    denominator = max(baseline, floor)
    return value / denominator
