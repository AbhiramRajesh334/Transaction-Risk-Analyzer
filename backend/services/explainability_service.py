"""Explainability engine: build human-readable risk explanations from features and indicators."""

from typing import Dict, List, Optional

from services.account_service import list_accounts
from services.behavioral_feature_service import get_features_for_account
from services.risk_indicator_service import get_indicators_for_account
from services.risk_scoring_service import get_high_risk_accounts, get_risk_for_account
from graph_engine.graph_queries import get_account_transactions, get_account_neighbors, get_incoming_neighbors, get_outgoing_neighbors


INDICATOR_DISPLAY_NAMES = {
    "activity_spike": "Activity Spike",
    "amount_anomaly": "Amount Anomaly",
    "pass_through": "Rapid Pass Through",
    "counterparty_explosion": "Counterparty Explosion",
    "suspicious_exposure": "Suspicious Exposure",
    "round_tripping": "Round Tripping",
    "structuring": "Structuring",
    "circular_flow": "Circular Flow",
}

REVERSE_INDICATOR_NAMES = {v: k for k, v in INDICATOR_DISPLAY_NAMES.items()}
REVERSE_INDICATOR_NAMES["Pass Through"] = "pass_through"


def _format_amount(value: float) -> str:
    return f"{value:,.2f}"


def _format_ratio(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def _select_top_transactions(account_id: str, direction: Optional[str] = None, limit: int = 3) -> List[dict]:
    transactions = get_account_transactions(account_id)
    if direction:
        transactions = [tx for tx in transactions if tx.get("direction") == direction]
    return sorted(transactions, key=lambda tx: tx.get("amount", 0), reverse=True)[:limit]


def _build_counterparty_support(account_id: str, max_parties: int = 5) -> dict:
    transactions = get_account_transactions(account_id)
    counterparty_amounts: Dict[str, float] = {}
    counterparty_transactions: Dict[str, List[dict]] = {}

    for tx in transactions:
        other = tx["sender_account"] if tx["direction"] == "incoming" else tx["receiver_account"]
        amount = float(tx.get("amount") or 0)
        counterparty_amounts[other] = counterparty_amounts.get(other, 0) + amount
        counterparty_transactions.setdefault(other, []).append(tx)

    top_counterparties = sorted(counterparty_amounts.items(), key=lambda item: item[1], reverse=True)[:max_parties]
    return {
        "supporting_accounts": [account for account, _ in top_counterparties],
        "supporting_transactions": [tx for account in [account for account, _ in top_counterparties] for tx in counterparty_transactions.get(account, [])][:6],
        "highlight_accounts": [account_id] + [account for account, _ in top_counterparties],
        "highlight_transaction_ids": [
            tx["transaction_id"]
            for account in [account for account, _ in top_counterparties]
            for tx in counterparty_transactions.get(account, [])[:2]
        ],
    }


def _build_reason_transactions(account_id: str, limit: int = 3) -> List[dict]:
    return _select_top_transactions(account_id, limit=limit)


def _explain_activity_spike(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    transaction_count = features.get("transaction_count", 0)
    velocity = features.get("velocity", 0.0)
    recent_activity_count = features.get("recent_activity_count", 0)
    top_transactions = _build_reason_transactions(account_id, limit=3)

    explanation = (
        f"The account processed {transaction_count} transactions overall, with "
        f"{recent_activity_count} in the last 7 days and a velocity of {velocity:.2f} tx/hr. "
        "This burst of activity is suspicious because it indicates a rapid volume spike."
    )

    evidence = {
        "transaction_count": transaction_count,
        "velocity": round(velocity, 3),
        "recent_activity_count": recent_activity_count,
        "components": indicator.get("evidence", {}).get("components", {}),
        "highlight_accounts": [account_id] if account_id else [],
        "highlight_transaction_ids": [tx["transaction_id"] for tx in top_transactions],
        "supporting_transactions": top_transactions,
    }

    return {
        "indicator": INDICATOR_DISPLAY_NAMES["activity_spike"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_amount_anomaly(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    average_amount = features.get("average_amount", 0.0)
    max_amount = features.get("max_amount", 0.0)
    top_transactions = _build_reason_transactions(account_id, limit=3)
    highlight_accounts = {account_id}
    for tx in top_transactions:
        highlight_accounts.add(tx.get("sender_account"))
        highlight_accounts.add(tx.get("receiver_account"))

    explanation = (
        f"The account has an average transaction size of { _format_amount(average_amount) } "
        f"and a maximum transaction of { _format_amount(max_amount) }. "
        "Large transaction amounts like these are suspicious because they deviate from typical account behavior."
    )

    evidence = {
        "average_amount": average_amount,
        "max_amount": max_amount,
        "components": indicator.get("evidence", {}).get("components", {}),
        "highlight_accounts": list(filter(None, highlight_accounts)),
        "highlight_transaction_ids": [tx["transaction_id"] for tx in top_transactions],
        "supporting_transactions": top_transactions,
    }

    return {
        "indicator": INDICATOR_DISPLAY_NAMES["amount_anomaly"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_pass_through(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    incoming_amount = features.get("incoming_amount", 0.0)
    outgoing_amount = features.get("outgoing_amount", 0.0)
    ratio = features.get("pass_through_ratio")

    incoming = _select_top_transactions(account_id, direction="incoming", limit=1)
    outgoing = _select_top_transactions(account_id, direction="outgoing", limit=1)
    path_accounts = [
        incoming[0]["sender_account"] if incoming else None,
        account_id,
        outgoing[0]["receiver_account"] if outgoing else None,
    ]
    supporting_transactions = [*incoming, *outgoing]

    explanation = (
        f"The account received { _format_amount(incoming_amount) } and forwarded "
        f"{ _format_amount(outgoing_amount) }, producing a pass-through ratio of { _format_ratio(ratio) }. "
        "Such a high ratio is suspicious because it suggests funds are quickly routed through the account."
    )

    evidence = {
        "incoming_amount": incoming_amount,
        "outgoing_amount": outgoing_amount,
        "pass_through_ratio": ratio,
        "components": indicator.get("evidence", {}).get("components", {}),
        "path_accounts": [account for account in path_accounts if account],
        "highlight_accounts": [account for account in path_accounts if account],
        "highlight_transaction_ids": [tx["transaction_id"] for tx in supporting_transactions],
        "supporting_transactions": supporting_transactions,
    }

    return {
        "indicator": INDICATOR_DISPLAY_NAMES["pass_through"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_counterparty_explosion(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    unique_counterparties = features.get("unique_counterparties", 0)
    in_degree = features.get("in_degree", 0)
    out_degree = features.get("out_degree", 0)
    support = _build_counterparty_support(account_id)

    explanation = (
        f"The account connected with {unique_counterparties} distinct counterparties, "
        f"including {in_degree} incoming and {out_degree} outgoing relationships. "
        "Rapid expansion of counterparties is suspicious because it can indicate a spreading fraud or laundering network."
    )

    evidence = {
        "unique_counterparties": unique_counterparties,
        "in_degree": in_degree,
        "out_degree": out_degree,
        "components": indicator.get("evidence", {}).get("components", {}),
        "supporting_accounts": support.get("supporting_accounts", []),
        "supporting_transactions": support.get("supporting_transactions", []),
        "highlight_accounts": support.get("highlight_accounts", []),
        "highlight_transaction_ids": support.get("highlight_transaction_ids", []),
    }

    return {
        "indicator": INDICATOR_DISPLAY_NAMES["counterparty_explosion"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _format_top_neighbors(top_neighbors: List[dict]) -> str:
    neighbor_strings = [
        f"{neighbor.get('account_id')} (score {neighbor.get('max_indicator_score')})"
        for neighbor in top_neighbors
    ]
    if not neighbor_strings:
        return "no high-risk neighbors"
    return ", ".join(neighbor_strings)


def _explain_suspicious_exposure(account_id: str, indicator: dict) -> dict:
    evidence_data = indicator.get("evidence", {})
    neighbor_count = evidence_data.get("neighbor_count", 0)
    suspicious_neighbor_count = evidence_data.get("suspicious_neighbor_count", 0)
    top_neighbors = evidence_data.get("top_neighbors", [])
    neighbors_text = _format_top_neighbors(top_neighbors)
    suspicious_ids = [neighbor.get("account_id") for neighbor in top_neighbors if neighbor.get("account_id")]

    explanation = (
        f"The account is exposed to {neighbor_count} connected accounts, "
        f"including {suspicious_neighbor_count} with elevated risk. "
        f"Top connected accounts are {neighbors_text}. "
        "Exposure to high-risk neighbors increases this account's own fraud risk."
    )

    evidence = {
        "neighbor_count": neighbor_count,
        "suspicious_neighbor_count": suspicious_neighbor_count,
        "top_neighbors": top_neighbors,
        "highlight_accounts": [account_id] + suspicious_ids,
        "supporting_accounts": suspicious_ids,
    }

    return {
        "indicator": INDICATOR_DISPLAY_NAMES["suspicious_exposure"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_round_tripping(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    round_trip_count = features.get("round_trip_count", 0)
    top_transactions = _build_reason_transactions(account_id, limit=4)
    highlight_accounts = {account_id}
    for tx in top_transactions:
        highlight_accounts.add(tx.get("sender_account"))
        highlight_accounts.add(tx.get("receiver_account"))

    explanation = (
        f"The account shows {round_trip_count} round-trip counterparty relationship(s) "
        "where funds were both sent and received. This pattern is suspicious because it can "
        "indicate layering or attempts to disguise the origin of funds."
    )
    evidence = {
        "round_trip_count": round_trip_count,
        "components": indicator.get("evidence", {}).get("components", {}),
        "highlight_accounts": list(filter(None, highlight_accounts)),
        "highlight_transaction_ids": [tx["transaction_id"] for tx in top_transactions],
        "supporting_transactions": top_transactions,
    }
    return {
        "indicator": INDICATOR_DISPLAY_NAMES["round_tripping"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_structuring(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    structuring_count = features.get("structuring_count", 0)
    transactions = get_account_transactions(account_id)
    sub_threshold = [
        tx for tx in transactions
        if 8000 <= float(tx.get("amount") or 0) <= 9999
    ][:5]

    explanation = (
        f"The account executed {structuring_count} transfers in the 8,000-9,999 band. "
        "Repeated sub-threshold transfers are suspicious because they may be structured "
        "to avoid reporting limits."
    )
    evidence = {
        "structuring_count": structuring_count,
        "threshold_band": "8000-9999",
        "components": indicator.get("evidence", {}).get("components", {}),
        "highlight_accounts": [account_id] + [
            tx.get("receiver_account") if tx.get("direction") == "outgoing" else tx.get("sender_account")
            for tx in sub_threshold
        ],
        "highlight_transaction_ids": [tx["transaction_id"] for tx in sub_threshold],
        "supporting_transactions": sub_threshold,
    }
    return {
        "indicator": INDICATOR_DISPLAY_NAMES["structuring"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


def _explain_circular_flow(features: dict, indicator: dict) -> dict:
    account_id = features.get("account_id")
    participation = features.get("circular_flow_participation", 0)
    transactions = get_account_transactions(account_id)[:6]
    path_accounts = [account_id]
    for tx in transactions:
        if tx.get("direction") == "outgoing":
            path_accounts.append(tx.get("receiver_account"))
        else:
            path_accounts.append(tx.get("sender_account"))

    explanation = (
        "The account participates in a directed fund-flow cycle. "
        "Circular movement of money is suspicious because it can be used to create "
        "artificial transaction history or obscure true fund origins."
    )
    evidence = {
        "circular_flow_participation": participation,
        "path_accounts": list(dict.fromkeys(filter(None, path_accounts))),
        "components": indicator.get("evidence", {}).get("components", {}),
        "highlight_accounts": list(dict.fromkeys(filter(None, path_accounts))),
        "highlight_transaction_ids": [tx["transaction_id"] for tx in transactions],
        "supporting_transactions": transactions,
    }
    return {
        "indicator": INDICATOR_DISPLAY_NAMES["circular_flow"],
        "score": indicator.get("score", 0),
        "explanation": explanation,
        "evidence": evidence,
    }


EXPLANATION_BUILDERS = {
    "activity_spike": _explain_activity_spike,
    "amount_anomaly": _explain_amount_anomaly,
    "pass_through": _explain_pass_through,
    "counterparty_explosion": _explain_counterparty_explosion,
    "suspicious_exposure": _explain_suspicious_exposure,
    "round_tripping": _explain_round_tripping,
    "structuring": _explain_structuring,
    "circular_flow": _explain_circular_flow,
}


def _build_reason_entries(account_id: str, top_reasons: List[str], indicators: dict, features: dict) -> List[dict]:
    entries = []
    for reason_name in top_reasons:
        key = REVERSE_INDICATOR_NAMES.get(reason_name)
        if not key:
            continue
        indicator = indicators.get(key)
        if not indicator:
            continue
        builder = EXPLANATION_BUILDERS.get(key)
        if not builder:
            continue
        entry = builder(features, indicator) if key != "suspicious_exposure" else builder(account_id, indicator)
        entries.append(entry)
    return entries


def get_explanation_for_account(account_id: str, custom_weights: dict = None) -> dict:
    risk_profile = get_risk_for_account(account_id, custom_weights=custom_weights)
    features = get_features_for_account(account_id)
    indicators = get_indicators_for_account(account_id)

    reasons = _build_reason_entries(
        account_id,
        risk_profile.get("top_reasons", []),
        indicators,
        features,
    )

    if not reasons:
        # Fallback: return top 8 indicators by score if top_reasons are unavailable.
        sorted_keys = [
            item for item in sorted(
                indicators.items(),
                key=lambda item: item[1].get("score", 0),
                reverse=True,
            ) if item[1].get("score", 0) > 0
        ][:8]
        if not sorted_keys:
            sorted_keys = sorted(
                indicators.items(),
                key=lambda item: item[1].get("score", 0),
                reverse=True,
            )[:2]
        fallback_reasons = [key for key, _ in sorted_keys]
        reasons = _build_reason_entries(account_id, [INDICATOR_DISPLAY_NAMES[key] for key in fallback_reasons], indicators, features)

    return {
        "account_id": account_id,
        "risk_score": risk_profile.get("risk_score", 0),
        "top_reasons": risk_profile.get("top_reasons", []),
        "reasons": reasons,
    }


def get_high_risk_explanations() -> List[dict]:
    high_risk_profiles = get_high_risk_accounts()
    return [get_explanation_for_account(profile["account_id"]) for profile in high_risk_profiles]
