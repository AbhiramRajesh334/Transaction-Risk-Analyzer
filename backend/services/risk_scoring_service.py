"""Final risk scoring engine: convert indicators into an explainable risk score."""

from typing import Dict, List

from services.risk_indicator_service import (
    get_all_indicators,
    get_indicators_for_account,
)
from services.account_service import list_accounts


WEIGHTS = {
    "activity_spike": 0.12,
    "amount_anomaly": 0.16,
    "pass_through": 0.22,
    "counterparty_explosion": 0.08,
    "suspicious_exposure": 0.16,
    "round_tripping": 0.14,
    "structuring": 0.08,
    "circular_flow": 0.08,
}


def _risk_level(score: float) -> str:
    if score >= 65:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _top_reasons(indicators: dict, limit: int = 8, custom_weights: dict = None) -> List[str]:
    weights = custom_weights if custom_weights is not None else WEIGHTS
    contributions = []
    for key, weight in weights.items():
        indicator = indicators.get(key, {})
        score = indicator.get("score", 0)
        if score > 0:
            contributions.append((key, score * weight))

    contributions.sort(key=lambda item: item[1], reverse=True)
    return [key.replace("_", " ").title() for key, _ in contributions[:limit]]


def _build_indicator_breakdown(indicators: dict, custom_weights: dict = None) -> dict:
    weights = custom_weights if custom_weights is not None else WEIGHTS
    return {
        key: {
            "score": indicators.get(key, {}).get("score", 0),
            "evidence": indicators.get(key, {}).get("evidence", {}),
        }
        for key in weights.keys()
    }


def _compute_score(indicators: dict, custom_weights: dict = None) -> float:
    weights = custom_weights if custom_weights is not None else WEIGHTS
    score = 0.0
    peak_indicator = 0.0
    for key, weight in weights.items():
        indicator = indicators.get(key, {})
        indicator_score = indicator.get("score", 0)
        score += indicator_score * weight
        peak_indicator = max(peak_indicator, indicator_score)

    # Strong single-signal boost: one very high indicator should pull score up.
    if peak_indicator >= 80:
        score += (peak_indicator - 80) * 0.45

    return max(0.0, min(100.0, score))


def _build_risk_profile(account_id: str, indicators: dict, custom_weights: dict = None) -> dict:
    normalized_score = _compute_score(indicators, custom_weights)
    return {
        "account_id": account_id,
        "risk_score": int(round(normalized_score)),
        "risk_level": _risk_level(normalized_score),
        "top_reasons": _top_reasons(indicators, custom_weights=custom_weights),
        "indicator_breakdown": _build_indicator_breakdown(indicators, custom_weights),
    }


def get_risk_for_account(account_id: str, custom_weights: dict = None) -> dict:
    indicators = get_indicators_for_account(account_id)
    return _build_risk_profile(account_id, indicators, custom_weights)


def get_risk_for_all(custom_weights: dict = None) -> List[dict]:
    indicators = get_all_indicators()
    return [_build_risk_profile(entry["account_id"], entry, custom_weights) for entry in indicators]


def get_high_risk_accounts(custom_weights: dict = None) -> List[dict]:
    return [
        profile
        for profile in get_risk_for_all(custom_weights)
        if profile["risk_level"] == "HIGH"
    ]


def get_top_accounts(limit: int = 10, custom_weights: dict = None) -> List[dict]:
    return sorted(get_risk_for_all(custom_weights), key=lambda item: item["risk_score"], reverse=True)[:limit]
