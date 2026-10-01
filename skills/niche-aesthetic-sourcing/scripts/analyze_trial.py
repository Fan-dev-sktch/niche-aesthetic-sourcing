"""Calculate order scenarios and observed funnels. Standard library, local read-only.

Inputs are declarations, not verified quotes or causal market evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

COST_NAMES = (
    "product", "packaging", "delivery", "platform_payment", "taxes", "returns",
    "fulfillment_labor", "design_allocated", "other_variable",
)


def numeric(value):
    try:
        return not isinstance(value, bool) and isinstance(value, (float, int)) and math.isfinite(value) and value >= 0
    except (OverflowError, TypeError):
        return False


def count(value):
    return isinstance(value, int) and numeric(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def interval(value, path, errors, missing):
    if value is None:
        missing.append(path)
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a low/high object or null.")
        return None
    lo, hi = value.get("low"), value.get("high")
    if not numeric(lo) or not numeric(hi) or hi < lo:
        errors.append(f"{path}: finite nonnegative ordered low/high are required.")
        return None
    refs = value.get("source_ids")
    if not text(value.get("basis")) or not isinstance(refs, list) or not refs or not all(text(x) for x in refs):
        errors.append(f"{path}: basis and nonempty source_ids are required, including for zero costs.")
        return None
    return (lo, hi)


def rounded(lo, hi):
    return {"low": round(lo, 6), "high": round(hi, 6)}


def wilson(successes, total):
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return rounded(max(0, center - half), min(1, center + half))


def analyze(data):
    if not isinstance(data, dict):
        return {"valid": False, "errors": ["Root must be an object."]}
    errors, missing = [], []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0.")
    if not text(data.get("currency")) or not text(data.get("boundary")):
        errors.append("currency and the revenue/cost boundary are required.")
    if data.get("data_status") not in ("scenario", "observed", "synthetic", "template"):
        errors.append("data_status must be scenario, observed, synthetic, or template.")
    revenue = interval(data.get("buyer_payment"), "buyer_payment", errors, missing)
    costs = data.get("costs")
    if not isinstance(costs, dict):
        errors.append("costs must be an object.")
        costs = {}
    extra = sorted(set(costs) - set(COST_NAMES))
    if extra:
        errors.append(f"Unknown cost fields {extra}; use a named field or other_variable rather than silently omit.")
    cost_ranges = {name: interval(costs.get(name), f"costs.{name}", errors, missing) for name in COST_NAMES}
    goal = data.get("min_contribution")
    if goal is None:
        missing.append("min_contribution")
    elif not numeric(goal):
        errors.append("min_contribution must be finite and nonnegative or null.")
    fixed = interval(data.get("fixed_setup"), "fixed_setup", errors, missing)
    funnel = data.get("funnel")
    if not isinstance(funnel, dict):
        errors.append("funnel must be an object.")
        funnel = {}
    fields = ("qualified_unique_visitors", "paid_buyers", "paid_orders")
    for name in fields:
        val = funnel.get(name)
        if val is None:
            missing.append(f"funnel.{name}")
        elif not count(val):
            errors.append(f"funnel.{name}: nonnegative integer or null required.")
    n, buyers, orders = (funnel.get(x) for x in fields)
    counts_known = all(count(x) for x in (n, buyers, orders))
    if counts_known:
        if buyers > n or orders < buyers or (buyers == 0 and orders > 0):
            errors.append("Funnel contradicts its cohort: buyers <= visitors, orders >= buyers, and zero buyers means zero orders.")
        if not text(funnel.get("measurement_basis")):
            errors.append("Known funnel counts require a cohort/attribution/deduplication measurement_basis.")
        try:
            start = date.fromisoformat(funnel.get("period_start", ""))
            end = date.fromisoformat(funnel.get("period_end", ""))
            if end < start:
                errors.append("Funnel period is inverted.")
        except (ValueError, TypeError):
            errors.append("Known funnel counts require ISO period_start and period_end.")
    spend = interval(funnel.get("acquisition_investment"), "funnel.acquisition_investment", errors, missing)
    result = {
        "valid": not errors, "errors": errors, "missing": missing,
        "data_status": data.get("data_status"), "currency": data.get("currency"),
        "before_acquisition_per_order": None, "after_acquisition_per_order": None,
        "break_even_acquisition_per_order": None, "target_acquisition_cap_per_order": None,
        "purchase_conversion": None, "conversion_wilson_95": None,
        "investment_per_paid_buyer": None, "investment_per_paid_order": None,
        "acquisition_investment_total": rounded(*spend) if spend else None,
        "fixed_setup_recovery_orders_scenario": None,
        "decision": "unknown",
        "limitations": [
            "Declared inputs only: no source, quote, tax, rights, or truth verification.",
            "Monetary ranges are scenario bounds, not probabilities or confidence intervals.",
            "Wilson interval assumes independent buyer events in the stated visitor cohort; nonrandom traffic limits inference.",
            "Observed conversion does not establish a winning experiment, aesthetic causality, repeatable demand, or future profit.",
            "Acquisition investment must include its disclosed cash/labor boundary; buyer cost is not automatically new-customer CAC.",
        ],
    }
    if errors:
        return result
    pre = None
    if revenue and all(x is not None for x in cost_ranges.values()):
        pre = (revenue[0] - sum(x[1] for x in cost_ranges.values()),
               revenue[1] - sum(x[0] for x in cost_ranges.values()))
        if not all(math.isfinite(x) for x in pre):
            result.update(valid=False, errors=["Aggregated monetary values exceed finite numeric range."], decision="invalid_numeric_range")
            return result
        result["before_acquisition_per_order"] = rounded(*pre)
        result["break_even_acquisition_per_order"] = round(pre[0], 6)
        if goal is not None:
            result["target_acquisition_cap_per_order"] = round(pre[0] - goal, 6)
    if counts_known and n:
        result["purchase_conversion"] = buyers / n
        result["conversion_wilson_95"] = wilson(buyers, n)
    if spend and counts_known:
        if buyers:
            result["investment_per_paid_buyer"] = rounded(spend[0] / buyers, spend[1] / buyers)
        if orders:
            per_order = (spend[0] / orders, spend[1] / orders)
            result["investment_per_paid_order"] = rounded(*per_order)
            if pre:
                after = (pre[0] - per_order[1], pre[1] - per_order[0])
                if not all(math.isfinite(x) for x in after):
                    result.update(valid=False, errors=["Aggregated monetary values exceed finite numeric range."], decision="invalid_numeric_range")
                    return result
                result["after_acquisition_per_order"] = rounded(*after)
                if goal is not None:
                    result["decision"] = "declared_conservative_margin_meets_goal" if after[0] >= goal else "declared_conservative_margin_below_goal"
                if fixed and after[0] > 0:
                    recovery = (fixed[0] / after[1], fixed[1] / after[0])
                    if not all(math.isfinite(x) for x in recovery):
                        result.update(valid=False, errors=["Recovery scenario exceeds finite numeric range."], decision="invalid_numeric_range")
                        return result
                    result["fixed_setup_recovery_orders_scenario"] = {"low": math.ceil(recovery[0]), "high": math.ceil(recovery[1]), "not_a_date": True}
        elif n:
            result["decision"] = "no_observed_paid_orders_cost_per_order_undefined"
    if counts_known and n == 0:
        result["decision"] = "no_qualified_visitors_acquisition_unvalidated"
    return result


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 5_000_000:
            raise ValueError("Input exceeds 5 MB.")
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = analyze(data)
    except (ValueError, OSError) as exc:
        result = {"valid": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
