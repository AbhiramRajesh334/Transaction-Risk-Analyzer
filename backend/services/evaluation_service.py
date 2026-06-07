"""Evaluate detection quality against stored ground-truth labels."""

from typing import Dict, List, Set

from database.database import list_ground_truth_entries
from services.risk_scoring_service import get_risk_for_all, WEIGHTS

HIGH_RISK_THRESHOLD = 60

SCENARIO_THRESHOLDS = {
    "activity_spike": 58,
    "amount_anomaly": 60,
    "rapid_pass_through": 60,
    "counterparty_explosion": 60,
    "suspicious_exposure": 38,
    "round_tripping": 60,
    "structuring": 60,
    "circular_flow": 58,
}

SCENARIO_DISPLAY = {
    "activity_spike": "Activity Spike",
    "amount_anomaly": "Amount Anomaly",
    "rapid_pass_through": "Rapid Pass Through",
    "counterparty_explosion": "Counterparty Explosion",
    "suspicious_exposure": "Suspicious Exposure",
    "round_tripping": "Round Tripping",
    "structuring": "Structuring",
    "circular_flow": "Circular Flow",
}

INDICATOR_TO_SCENARIO = {
    "activity_spike": "activity_spike",
    "amount_anomaly": "amount_anomaly",
    "pass_through": "rapid_pass_through",
    "counterparty_explosion": "counterparty_explosion",
    "suspicious_exposure": "suspicious_exposure",
    "round_tripping": "round_tripping",
    "structuring": "structuring",
    "circular_flow": "circular_flow",
}


def _metrics(tp: int, fp: int, fn: int, tn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) else 0.0
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }


def _top_indicator_key(profile: dict) -> str:
    breakdown = profile.get("indicator_breakdown", {})
    if not breakdown:
        return ""
    return max(breakdown.items(), key=lambda item: item[1].get("score", 0))[0]


def _scenario_threshold(scenario_type: str, default: int) -> int:
    return SCENARIO_THRESHOLDS.get(scenario_type, default)


def _scenario_match(profile: dict, scenario_type: str, default_threshold: int) -> bool:
    indicator_key = INDICATOR_TO_SCENARIO.get(_top_indicator_key(profile), "")
    threshold = _scenario_threshold(scenario_type, default_threshold)
    return indicator_key == scenario_type and profile.get("risk_score", 0) >= threshold


def get_evaluation_report(threshold: int = HIGH_RISK_THRESHOLD) -> dict:
    ground_truth_rows = list_ground_truth_entries()
    fraud_by_scenario: Dict[str, Set[str]] = {}
    fraud_accounts: Set[str] = set()

    for row in ground_truth_rows:
        account_id = row["account_id"]
        scenario_type = row["scenario_type"]
        fraud_accounts.add(account_id)
        fraud_by_scenario.setdefault(scenario_type, set()).add(account_id)

    risk_profiles = get_risk_for_all()
    all_accounts: Set[str] = {profile["account_id"] for profile in risk_profiles}
    predicted_accounts: Set[str] = {
        profile["account_id"] for profile in risk_profiles if profile.get("risk_score", 0) >= threshold
    }

    true_positives = fraud_accounts & predicted_accounts
    false_positives = predicted_accounts - fraud_accounts
    false_negatives = fraud_accounts - predicted_accounts
    true_negatives = (all_accounts - fraud_accounts) - predicted_accounts

    profile_map = {profile["account_id"]: profile for profile in risk_profiles}

    per_scenario = []
    for scenario_type, labeled_accounts in sorted(fraud_by_scenario.items()):
        scenario_threshold = _scenario_threshold(scenario_type, threshold)
        detected = {
            account_id
            for account_id in labeled_accounts
            if account_id in profile_map and profile_map[account_id].get("risk_score", 0) >= scenario_threshold
        }
        scenario_tp = len(detected)
        scenario_fn = len(labeled_accounts - detected)
        scenario_precision_den = sum(
            1
            for account_id in predicted_accounts
            if account_id in profile_map and _scenario_match(profile_map[account_id], scenario_type, threshold)
        )
        per_scenario.append(
            {
                "scenario_type": scenario_type,
                "display_name": SCENARIO_DISPLAY.get(scenario_type, scenario_type.replace("_", " ").title()),
                "labeled_accounts": sorted(labeled_accounts),
                "detected_accounts": sorted(detected),
                "missed_accounts": sorted(labeled_accounts - detected),
                "detection_rate": round(scenario_tp / len(labeled_accounts), 4) if labeled_accounts else 0.0,
                "metrics": _metrics(scenario_tp, max(scenario_precision_den - scenario_tp, 0), scenario_fn, 0),
            }
        )

    return {
        "threshold": threshold,
        "overall_metrics": _metrics(
            len(true_positives),
            len(false_positives),
            len(false_negatives),
            len(true_negatives),
        ),
        "labeled_fraud_accounts": sorted(fraud_accounts),
        "predicted_accounts": sorted(predicted_accounts),
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(false_negatives),
        "account_details": [
            {
                "account_id": profile["account_id"],
                "risk_score": profile["risk_score"],
                "risk_level": profile["risk_level"],
                "is_labeled_fraud": profile["account_id"] in fraud_accounts,
                "is_predicted_fraud": profile["account_id"] in predicted_accounts,
                "labeled_scenarios": sorted(
                    {
                        row["scenario_type"]
                        for row in ground_truth_rows
                        if row["account_id"] == profile["account_id"]
                    }
                ),
                "top_reasons": profile.get("top_reasons", []),
            }
            for profile in sorted(risk_profiles, key=lambda item: item["risk_score"], reverse=True)
        ],
        "per_scenario": per_scenario,
        "indicator_weights": WEIGHTS,
    }
