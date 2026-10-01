"""Validate citations and stage gates. No network, installations, or writes.

This checks declared evidence structure; it does not establish source truth,
legal compliance, comparability, or commercial success.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

GATES = (
    "demand", "aesthetic_premium", "competition_gap", "unit_economics",
    "rights_and_channel", "fulfillment_fit",
)
PASS_KINDS = {
    "demand": {"platform_sales_data", "transaction_record", "purchase_experiment"},
    "aesthetic_premium": {"matched_comparison", "purchase_experiment"},
    "competition_gap": {"matched_comparison", "platform_sales_data", "platform_search_data"},
    "unit_economics": {"cost_model"},
    "rights_and_channel": {"rights_document"},
    "fulfillment_fit": {"fulfillment_test"},
}
KINDS = set().union(*PASS_KINDS.values()) | {
    "product_listing", "customer_review", "community_report", "method_documentation",
    "supplier_quote", "supplier_price_listing", "channel_policy", "seller_account_record"
}
ORIGINS = {"reader", "live", "cached", "user_supplied", "search_snippet", "blocked"}
STAGES = {"discovery", "validation", "test_ready", "pilot_ready", "rejected"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def finite_number(value, minimum=0):
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= minimum
    except (OverflowError, TypeError):
        return False


def source_metrics(source):
    metrics = source.get("metrics", [])
    return metrics if isinstance(metrics, list) else []


def decision_source_usable(source):
    if source.get("content_origin") in ("blocked", "search_snippet"):
        return False
    try:
        date.fromisoformat(source.get("retrieved_at", ""))
        return True
    except (TypeError, ValueError):
        return False


def validate_pass_gate(cid, key, gate, usable, scope, by_id, version="1.0", cutoff=None):
    """Require concrete fields, not merely the right evidence type label."""
    errors = []
    prefix = f"{cid}/{key}"
    details = gate.get("details")
    if not isinstance(details, dict):
        return [f"{prefix}: pass requires structured details."]

    def require(condition, message):
        if not condition:
            errors.append(f"{prefix}: {message}")

    def references(refs, label):
        valid = isinstance(refs, list) and bool(refs) and all(nonempty(ref) and ref in by_id for ref in refs)
        require(valid, f"{label} requires valid nonempty source references.")
        if valid:
            require(all(decision_source_usable(by_id[ref]) for ref in refs),
                    f"{label} cannot use blocked pages, snippets or undated sources.")

    if key in ("demand", "competition_gap", "rights_and_channel"):
        require(nonempty(scope.get("target_country")) and details.get("target_country") == scope.get("target_country"),
                "evidence target_country must match the explicit batch market.")
    if key in ("competition_gap", "rights_and_channel"):
        require(nonempty(scope.get("target_channel")) and details.get("target_channel") == scope.get("target_channel"),
                "evidence target_channel must match the explicit batch channel.")
    if key == "demand":
        require(details.get("measurement_scope") in ("sku", "defined_niche", "purchase_experiment"),
                "demand requires SKU, defined-niche, or experiment scope; shop totals are insufficient.")
        require(finite_number(details.get("sample_size"), 1), "demand sample_size must be positive.")
        require(nonempty(details.get("decision_threshold")), "demand decision_threshold must be recorded before judging pass.")
        require(details.get("threshold_met") is True, "demand threshold must have been met.")
        try:
            start = date.fromisoformat(details.get("period_start", ""))
            end = date.fromisoformat(details.get("period_end", ""))
            require(end >= start, "demand period is inverted.")
            require(cutoff is None or end <= cutoff, "completed demand period cannot be after as_of.")
        except (TypeError, ValueError):
            require(False, "demand requires ISO period_start and period_end.")
        sales_metrics = [m for s in usable if isinstance(s.get("kind"), str) and s.get("kind") in PASS_KINDS[key]
                         and s.get("data_scope") == details.get("measurement_scope")
                         and s.get("market") == scope.get("target_country")
                         for m in source_metrics(s) if isinstance(m, dict) and m.get("scope") == s.get("data_scope")]
        require(any(m.get("name") in ("units_sold", "paid_orders", "purchases")
                    and m.get("basis") in ("transaction", "platform_sales_data", "purchase_experiment")
                    and m.get("scope") in ("sku", "defined_niche", "purchase_experiment")
                    and finite_number(m.get("value"), 1) for m in sales_metrics),
                "requires attributable paid-purchase metrics in the target market, not reviews or shop sales.")
    elif key == "aesthetic_premium":
        require(details.get("price_basis") == "transaction", "premium requires transaction prices, not asking prices.")
        require(nonempty(details.get("currency")), "premium requires one explicit currency.")
        require(finite_number(details.get("design_price"), 0.000001) and finite_number(details.get("baseline_price"), 0.000001),
                "premium requires positive comparable price values.")
        if finite_number(details.get("design_price")) and finite_number(details.get("baseline_price")):
            require(details["design_price"] > details["baseline_price"], "a claimed aesthetic premium requires design price above the matched baseline.")
        require(finite_number(details.get("sample_size"), 1), "premium sample_size must be positive.")
        controls = details.get("matched_controls")
        needed = {"material", "size", "function", "brand", "market", "delivery"}
        require(isinstance(controls, list) and all(isinstance(x, str) for x in controls) and needed.issubset(controls),
                "premium must disclose matching of material, size, function, brand, market and delivery.")
        require(details.get("confound_reviewed") is True and nonempty(details.get("decision_threshold")),
                "premium requires confound review and an explicit decision threshold.")
        require(details.get("threshold_met") is True, "premium threshold must have been met.")
        price_sources = [s for s in usable if s.get("kind") in PASS_KINDS[key]]
        require(all(not nonempty(s.get("market")) or s.get("market") == scope.get("target_country") for s in price_sources),
                "explicit sold-price source market cannot contradict the target market.")
        require(all(not nonempty(m.get("currency")) or m.get("currency") == details.get("currency")
                    for s in price_sources for m in source_metrics(s) if isinstance(m, dict)
                    and m.get("name") in ("median_sold_price", "experiment_paid_price")),
                "explicit sold-price currency cannot contradict the comparison currency; use a documented derived record for conversions.")
        if version == "1.2":
            require(nonempty(scope.get("target_country")), "premium requires an explicit target market.")
            require(all(s.get("market") == scope.get("target_country") for s in price_sources),
                    "premium sold-price records require the target market.")
        require(any(any(isinstance(m, dict)
                    and m.get("name") in ("median_sold_price", "experiment_paid_price")
                    and m.get("basis") == "transaction"
                    and (version != "1.2" or m.get("currency") == details.get("currency"))
                    and finite_number(m.get("value"), 0.000001) for m in source_metrics(s)) for s in price_sources),
                "premium sources must contain actual sold-price or paid-experiment metrics.")
    elif key == "competition_gap":
        require(finite_number(details.get("direct_substitutes_examined"), 1), "direct substitutes must have been examined.")
        require(details.get("new_entrant_evidence_reviewed") is True, "new-entrant evidence must have been reviewed.")
        require(nonempty(details.get("gap_statement")) and nonempty(details.get("coverage_limitations")),
                "gap and coverage limitations must be recorded.")
        references(details.get("unmet_need_source_ids"), "unmet need")
        references(details.get("comparator_source_ids"), "comparator review")
    elif key == "unit_economics":
        require(nonempty(details.get("currency")), "cost model currency is required.")
        require(any(s.get("kind") == "supplier_quote" for s in usable), "unit economics also requires a real supplier quote reference.")
        require(details.get("working_capital_checked") is True, "working capital must have been checked.")
        components = details.get("components")
        costs = ("purchase", "packaging", "international_shipping", "platform_payment", "taxes", "cac", "returns", "other_variable")
        if version in ("1.1", "1.2"):
            costs += ("fulfillment_labor", "design_allocated")
        if not isinstance(components, dict):
            require(False, "cost model components are required.")
        else:
            complete = True
            for name in ("revenue",) + costs:
                component = components.get(name)
                if not isinstance(component, dict):
                    require(False, f"cost model component {name} is missing.")
                    complete = False
                    continue
                low, high = component.get("low"), component.get("high")
                good = finite_number(low) and finite_number(high) and high >= low
                require(good, f"{name} requires a nonnegative low/high range.")
                complete = complete and good
                references(component.get("source_ids"), f"cost component {name}")
                require(nonempty(component.get("basis")), f"{name} requires an amount/zero-cost basis.")
            floor = details.get("contribution_margin_floor")
            require(finite_number(floor), "contribution_margin_floor must be explicit and nonnegative.")
            if complete and finite_number(floor):
                conservative = components["revenue"]["low"] - sum(components[name]["high"] for name in costs)
                require(conservative >= floor, f"conservative contribution {conservative:.2f} is below required floor {floor:.2f}.")
    elif key == "rights_and_channel":
        require(any(s.get("kind") == "rights_document" for s in usable) and any(s.get("kind") == "channel_policy" for s in usable),
                "requires both product-specific rights materials and channel rules.")
        require(details.get("rights_basis") in ("original_design_reviewed", "licensed_verified", "legal_review_recorded"),
                "specific rights basis is required.")
        for field in ("final_design_assets_reviewed", "marketing_assets_reviewed", "channel_eligibility_reviewed"):
            require(details.get(field) is True, f"{field} must be completed.")
    elif key == "fulfillment_fit":
        require(any(s.get("kind") == "fulfillment_test" for s in usable), "a quote alone cannot establish fulfillment.")
        for field in ("sample_checked", "fit_quality_checked", "delivery_plan_checked"):
            require(details.get(field) is True, f"{field} must be completed.")
        require(nonempty(details.get("test_date")) and nonempty(details.get("test_result")), "sample test date and result are required.")
        try:
            tested = date.fromisoformat(details.get("test_date", ""))
            require(cutoff is None or tested <= cutoff, "completed sample test cannot be after as_of.")
        except (TypeError, ValueError):
            require(False, "sample test date must be ISO format.")
    return errors


def validate_sales_readiness(cid, candidate, scope, by_id, cutoff=None):
    """Commercial test readiness differs from evidence of validated demand."""
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(f"{cid}: {message}")

    def sources(refs, label, kind=None):
        valid = isinstance(refs, list) and bool(refs) and all(nonempty(ref) and ref in by_id for ref in refs)
        require(valid, f"{label} requires actual source references.")
        linked = [by_id[ref] for ref in refs] if valid else []
        require(all(decision_source_usable(s) for s in linked), f"{label} cannot use snippets, blocked or undated sources.")
        if kind:
            require(any(s.get("kind") == kind for s in linked), f"{label} requires {kind} evidence.")
        return linked

    for field in ("seller_country", "seller_entity", "target_country", "target_channel", "ship_from"):
        require(nonempty(scope.get(field)), f"commercial readiness requires explicit {field}.")
    access = candidate.get("channel_access")
    if not isinstance(access, dict):
        require(False, "channel_access record is required.")
    else:
        require(access.get("status") == "pass", "real channel access must pass.")
        for key in ("seller_country", "seller_entity", "target_channel"):
            require(access.get(key) == scope.get(key) and nonempty(access.get(key)), f"channel_access {key} must match scope.")
        require(access.get("seller_verification_reviewed") is True and access.get("payout_reviewed") is True,
                "seller verification and payout conditions must have been reviewed.")
        require(nonempty(access.get("rationale")), "channel access rationale required.")
        sources(access.get("source_ids"), "channel rules", "channel_policy")
        sources(access.get("seller_evidence_source_ids"), "actual seller eligibility", "seller_account_record")
    if candidate.get("stage") == "pilot_ready":
        pilot = candidate.get("pilot", {})
        economics = candidate.get("gates", {}).get("unit_economics", {}).get("details", {})
        model_currency = economics.get("currency") if isinstance(economics, dict) else None
        require(isinstance(pilot, dict) and pilot.get("currency") == model_currency,
                "pilot budget currency must match unit economics; convert explicitly rather than mix currencies.")
        acquisition = candidate.get("acquisition")
        if not isinstance(acquisition, dict):
            require(False, "validated operating evidence requires acquisition record.")
        else:
            require(acquisition.get("status") == "pass", "acquisition must be supported by actual results.")
            require(nonempty(acquisition.get("channel")) and nonempty(acquisition.get("measurement_basis")), "acquisition channel and attribution basis required.")
            visits, buyers, orders = (acquisition.get(x) for x in ("qualified_unique_visitors", "paid_buyers", "paid_orders"))
            good = all(isinstance(x, int) and not isinstance(x, bool) and x > 0 for x in (visits, buyers, orders))
            require(good and visits >= buyers and orders >= buyers, "acquisition needs consistent positive visitors, paid buyers and orders.")
            require(finite_number(acquisition.get("investment_total")), "acquisition cash/labor investment must be recorded.")
            require(nonempty(acquisition.get("investment_basis")), "zero or nonzero acquisition investment needs a disclosed basis.")
            if acquisition.get("currency") is not None:
                require(acquisition.get("currency") == model_currency, "acquisition currency must match the cost model.")
            require(nonempty(acquisition.get("decision_threshold")) and acquisition.get("threshold_met") is True, "acquisition criterion must be predefined and met.")
            evidence = sources(acquisition.get("source_ids"), "acquisition outcomes")
            require(any(s.get("kind") in ("transaction_record", "purchase_experiment", "platform_sales_data")
                        and s.get("market") == scope.get("target_country")
                        and s.get("data_scope") in ("sku", "defined_niche", "purchase_experiment")
                        and any(isinstance(m, dict) and m.get("name") == "paid_orders" and m.get("value") == orders
                                and finite_number(m.get("value"), 1) and m.get("basis") in ("transaction", "platform_sales_data", "purchase_experiment")
                                and m.get("scope") == s.get("data_scope") for m in source_metrics(s)) for s in evidence),
                    "acquisition outcomes need attributable target-market paid evidence.")
            require(all(not nonempty(s.get("channel")) or s.get("channel") == scope.get("target_channel") for s in evidence),
                    "explicit transaction channel cannot contradict the declared selling channel.")
            try:
                start = date.fromisoformat(acquisition.get("period_start", ""))
                end = date.fromisoformat(acquisition.get("period_end", ""))
                require(end >= start, "acquisition period is inverted.")
                require(cutoff is None or end <= cutoff, "completed acquisition period cannot be after as_of.")
            except (ValueError, TypeError):
                require(False, "acquisition ISO observation period required.")
        return errors

    gates = candidate.get("gates", {})
    for key in ("rights_and_channel", "fulfillment_fit"):
        gate = gates.get(key, {}) if isinstance(gates, dict) else {}
        require(isinstance(gate, dict) and gate.get("status") == "pass", f"test_ready requires {key} to pass.")
    require(isinstance(gates, dict) and all(isinstance(gates.get(key), dict) and gates[key].get("status") != "fail" for key in GATES),
            "test_ready cannot ignore a failed gate; revise the specific plan first.")
    costs = candidate.get("test_costs")
    if not isinstance(costs, dict):
        require(False, "test_costs with a complete bounded scenario are required.")
        return errors
    require(nonempty(costs.get("currency")), "test cost currency is required.")
    require(nonempty(costs.get("boundary")), "test cost revenue/tax/refund/labor boundary required.")
    sources(costs.get("quote_source_ids"), "test manufacturing quote", "supplier_quote")
    sources(costs.get("model_source_ids"), "test cost scenario", "cost_model")
    require(finite_number(costs.get("acquisition_cap_per_order")), "test acquisition cap must be explicit and nonnegative.")
    require(finite_number(costs.get("max_affordable_loss")), "test loss budget must be explicit and nonnegative.")
    require(costs.get("working_capital_checked") is True, "test inventory/settlement/loss funding must have been checked.")
    components = costs.get("components")
    names = ("revenue", "purchase", "packaging", "international_shipping", "platform_payment", "taxes", "returns", "other_variable", "fulfillment_labor", "design_allocated")
    if not isinstance(components, dict):
        require(False, "test cost components are required.")
    else:
        complete = True
        for name in names:
            value = components.get(name)
            valid = isinstance(value, dict) and finite_number(value.get("low")) and finite_number(value.get("high")) and value["high"] >= value["low"]
            require(valid, f"test component {name} needs finite ordered low/high.")
            complete = complete and valid
            if isinstance(value, dict):
                require(nonempty(value.get("basis")), f"test component {name} needs an amount/zero-cost basis.")
                sources(value.get("source_ids"), f"test component {name}")
        if complete and finite_number(costs.get("acquisition_cap_per_order")) and finite_number(costs.get("max_affordable_loss")):
            worst_order_contribution = components["revenue"]["low"] - sum(components[name]["high"] for name in names if name != "revenue")
            worst_one_order_loss = max(0, -worst_order_contribution) + costs["acquisition_cap_per_order"]
            require(math.isfinite(worst_one_order_loss) and worst_one_order_loss <= costs["max_affordable_loss"],
                    "one fulfilled order plus its capped acquisition spend cannot exceed the entire affordable loss budget.")
    pilot = candidate.get("pilot", {})
    if isinstance(pilot, dict):
        require(finite_number(pilot.get("qualified_visit_target"), 1), "test needs a predefined qualified visitor target.")
        require(nonempty(pilot.get("acquisition_channel")), "test needs an acquisition channel hypothesis.")
        require(finite_number(pilot.get("budget_cap")) and finite_number(costs.get("max_affordable_loss"))
                and pilot["budget_cap"] <= costs["max_affordable_loss"], "test budget must fit the declared affordable loss.")
        require(pilot.get("currency") == costs.get("currency"), "test budget and cost scenario currencies must match.")
    return errors


def validate_funding(cid, candidate, scope, by_id):
    """Conservative cash ceiling: no assumed revenue or inventory recovery."""
    errors = []
    prefix = f"{cid}/funding"

    def require(condition, message):
        if not condition:
            errors.append(f"{prefix}: {message}")

    plan = candidate.get("funding_plan")
    if not isinstance(plan, dict):
        return [f"{prefix}: schema 1.2 readiness requires a whole-trial funding_plan."]
    pilot = candidate.get("pilot", {})
    if not isinstance(pilot, dict):
        pilot = {}
    require(plan.get("currency") == scope.get("currency") == pilot.get("currency") and nonempty(plan.get("currency")),
            "scope, trial and funding currencies must match.")
    require(finite_number(scope.get("budget")), "current user cash budget is required.")
    require(finite_number(plan.get("max_affordable_loss")), "user-approved affordable loss must be explicit.")
    require(finite_number(plan.get("max_orders"), 1) and isinstance(plan.get("max_orders"), int),
            "a positive integer fulfillment/order cap is required.")
    require(nonempty(plan.get("boundary")), "cash commitments, settlement delay and noncash labor boundary required.")
    require(plan.get("zero_revenue_zero_recovery") is True, "conservative funding assumes no customer revenue or unsold-stock recovery.")
    require(plan.get("no_double_counting_reviewed") is True, "cash expense groups must be reviewed for overlap.")
    expected = {"inventory", "samples_setup", "acquisition", "fulfillment_reserve", "fees_taxes_returns_reserve", "other_commitments"}
    costs = plan.get("cash_components")
    require(isinstance(costs, dict) and set(costs) == expected, "all six whole-trial cash expense groups are required.")
    total = 0
    complete = isinstance(costs, dict) and set(costs) == expected
    if isinstance(costs, dict):
        for key in expected:
            item = costs.get(key)
            good = isinstance(item, dict) and finite_number(item.get("high"))
            require(good, f"{key} requires a finite nonnegative maximum cash commitment.")
            complete = complete and good
            if isinstance(item, dict):
                require(nonempty(item.get("basis")), f"{key} needs quantity/period/zero basis, including quote MOQ and payment terms where relevant.")
                refs = item.get("source_ids")
                valid = isinstance(refs, list) and bool(refs) and all(nonempty(r) and r in by_id for r in refs)
                require(valid, f"{key} requires valid sources.")
                if valid:
                    require(all(decision_source_usable(by_id[r]) for r in refs), f"{key} cannot use snippets, blocked or undated sources.")
                if key == "inventory":
                    quantity, minimum = item.get("quantity"), item.get("quote_minimum_quantity")
                    unit, inbound = item.get("unit_cash_high"), item.get("inbound_cash_high")
                    quantities_valid = all(isinstance(x, int) and not isinstance(x, bool) and finite_number(x) for x in (quantity, minimum))
                    require(quantities_valid and quantity >= minimum, "inventory quantity must cover the quoted MOQ.")
                    require(finite_number(unit) and finite_number(inbound), "inventory maximum unit cost and inbound cash cost required.")
                    require(valid and any(by_id[r].get("kind") == "supplier_quote" for r in refs), "inventory commitment requires the actual supplier quote.")
                    if quantities_valid and finite_number(unit) and finite_number(inbound) and good:
                        required = quantity * unit + inbound
                        require(finite_number(required) and item["high"] >= required,
                                "inventory cash maximum must cover quantity times unit cost plus inbound cash costs.")
                if key == "acquisition":
                    cap = pilot.get("acquisition_budget_cap")
                    require(finite_number(cap) and good and item["high"] >= cap,
                            "whole-trial acquisition commitment must cover the planned cash spend cap.")
            if good:
                total += item["high"]
    if complete:
        require(finite_number(total), "total commitments overflowed.")
        for limit, label in ((scope.get("budget"), "current user budget"),
                             (pilot.get("budget_cap"), "trial budget cap"),
                             (plan.get("max_affordable_loss"), "affordable loss")):
            require(finite_number(limit) and total <= limit, f"whole-trial maximum cash commitment {total} exceeds or lacks {label}.")
        if candidate.get("stage") == "test_ready":
            costs = candidate.get("test_costs", {})
            if isinstance(costs, dict):
                require(finite_number(costs.get("max_affordable_loss")) and total <= costs["max_affordable_loss"],
                        "whole-trial commitments exceed the per-order record's loss boundary.")
    return errors


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["Root must be an object."], []
    version = data.get("schema_version")
    if version not in ("1.0", "1.1", "1.2"):
        errors.append("schema_version must be 1.0, 1.1 or 1.2.")
    try:
        cutoff = date.fromisoformat(data.get("as_of", ""))
    except (TypeError, ValueError):
        errors.append("as_of must be an ISO date.")
        cutoff = None
    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be an object.")
        scope = {}
    if scope.get("budget") is not None:
        if not finite_number(scope.get("budget")):
            errors.append("scope budget must be finite and nonnegative or unknown.")
        if not nonempty(scope.get("currency")):
            errors.append("an explicit scope budget requires currency.")
    sources = data.get("sources", [])
    candidates = data.get("candidates", [])
    if not isinstance(sources, list) or not isinstance(candidates, list):
        return errors + ["sources and candidates must be lists."], []
    by_id = {}
    for index, source in enumerate(sources):
        prefix = f"source[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix}: must be an object.")
            continue
        sid = source.get("id")
        if not nonempty(sid) or sid in by_id:
            errors.append(f"{prefix}: missing or duplicate id.")
            continue
        by_id[sid] = source
        for field in ("title", "publisher", "independence_key", "observation", "limitations"):
            if not nonempty(source.get(field)):
                errors.append(f"{sid}: {field} must be nonempty.")
        if not isinstance(source.get("kind"), str) or source.get("kind") not in KINDS:
            errors.append(f"{sid}: invalid kind.")
        if not isinstance(source.get("content_origin"), str) or source.get("content_origin") not in ORIGINS:
            errors.append(f"{sid}: invalid content_origin.")
        try:
            parsed = urlparse(str(source.get("url", "")))
            valid_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except ValueError:
            valid_url = False
        if not valid_url:
            if not (source.get("content_origin") == "user_supplied" and nonempty(source.get("local_reference"))):
                errors.append(f"{sid}: requires URL or a user-supplied local reference.")
        if version in ("1.1", "1.2") and source.get("retrieved_at") is None:
            if not nonempty(source.get("date_unknown_reason")):
                errors.append(f"{sid}: unknown retrieval date requires date_unknown_reason.")
        else:
            try:
                retrieved = date.fromisoformat(source.get("retrieved_at", ""))
                if cutoff and retrieved > cutoff:
                    errors.append(f"{sid}: retrieved_at is after as_of.")
            except (TypeError, ValueError):
                errors.append(f"{sid}: retrieved_at must be an ISO date or schema 1.1/1.2 explicit unknown.")
        metrics = source.get("metrics", [])
        if not isinstance(metrics, list):
            errors.append(f"{sid}: metrics must be a list.")
            continue
        for metric in metrics:
            if not isinstance(metric, dict):
                errors.append(f"{sid}: each metric must be an object.")
                continue
            for field in ("name", "unit", "scope", "basis"):
                if not nonempty(metric.get(field)):
                    errors.append(f"{sid}: metric {field} must be nonempty.")
            value = metric.get("value")
            if not finite_number(value, -math.inf):
                errors.append(f"{sid}: metric value must be finite numeric.")
            if metric.get("name") == "price" and not nonempty(metric.get("currency")):
                errors.append(f"{sid}: price requires currency.")
            if metric.get("name") == "units_sold" and metric.get("basis") in ("review_count", "shop_sales", "views", "favorites", "asking_price"):
                errors.append(f"{sid}: proxy metric cannot be declared units_sold.")
    seen = set()
    rows = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"candidate[{index}]: must be an object.")
            continue
        cid = candidate.get("id")
        if not nonempty(cid) or cid in seen:
            errors.append(f"candidate[{index}]: missing or duplicate id.")
            continue
        seen.add(cid)
        stage = candidate.get("stage")
        if not isinstance(stage, str) or stage not in STAGES:
            errors.append(f"{cid}: invalid stage.")
        for field in ("name", "hypothesis", "next_action"):
            if not nonempty(candidate.get(field)):
                errors.append(f"{cid}: {field} must be nonempty.")
        exclusions = scope.get("user_exclusions", [])
        if isinstance(exclusions, list) and candidate.get("name") in exclusions and stage != "rejected":
            errors.append(f"{cid}: user-excluded candidate must be rejected.")
        gates = candidate.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{cid}: gates must be an object.")
            continue
        statuses = []
        for key in GATES:
            gate = gates.get(key)
            if not isinstance(gate, dict):
                errors.append(f"{cid}: missing gate {key}.")
                statuses.append("unknown")
                continue
            status = gate.get("status")
            statuses.append(status)
            if not isinstance(status, str) or status not in {"pass", "unknown", "fail"}:
                errors.append(f"{cid}/{key}: invalid status.")
            if not nonempty(gate.get("rationale")):
                errors.append(f"{cid}/{key}: rationale is required.")
            refs = gate.get("source_ids", [])
            if not isinstance(refs, list) or any(not nonempty(ref) for ref in refs):
                errors.append(f"{cid}/{key}: source_ids must be a list of IDs.")
                continue
            missing = [ref for ref in refs if ref not in by_id]
            if missing:
                errors.append(f"{cid}/{key}: unknown sources {missing}.")
            linked = [by_id[ref] for ref in refs if ref in by_id]
            if status == "pass":
                usable = [s for s in linked if decision_source_usable(s)]
                if not any(isinstance(s.get("kind"), str) and s.get("kind") in PASS_KINDS[key] for s in usable):
                    errors.append(f"{cid}/{key}: no usable evidence of the required kind.")
                errors.extend(validate_pass_gate(cid, key, gate, usable, scope, by_id, version, cutoff))
        if stage in ("test_ready", "pilot_ready"):
            if stage == "test_ready" and version not in ("1.1", "1.2"):
                errors.append(f"{cid}: test_ready requires schema 1.1 or 1.2.")
            if stage == "pilot_ready" and any(status != "pass" for status in statuses):
                errors.append(f"{cid}: pilot_ready requires all six gates to pass.")
            for field in ("target_country", "target_channel"):
                if not nonempty(scope.get(field)):
                    errors.append(f"{cid}: pilot_ready requires {field}.")
            pilot = candidate.get("pilot")
            if not isinstance(pilot, dict):
                errors.append(f"{cid}: pilot plan is required.")
            else:
                for field in ("audience", "duration", "variables", "success_criteria", "stop_criteria", "authorization_required"):
                    if not nonempty(pilot.get(field)):
                        errors.append(f"{cid}: pilot {field} is required.")
                amount = pilot.get("budget_cap")
                if not finite_number(amount):
                    errors.append(f"{cid}: pilot budget_cap must be a nonnegative number.")
                if not nonempty(pilot.get("currency")):
                    errors.append(f"{cid}: pilot currency is required.")
                if finite_number(scope.get("budget")) and finite_number(amount) and amount > scope["budget"]:
                    errors.append(f"{cid}: trial budget exceeds the current scope user budget.")
                if nonempty(scope.get("currency")) and pilot.get("currency") != scope.get("currency"):
                    errors.append(f"{cid}: trial currency conflicts with the current scope currency.")
            if version in ("1.1", "1.2"):
                errors.extend(validate_sales_readiness(cid, candidate, scope, by_id, cutoff))
            if version == "1.2":
                errors.extend(validate_funding(cid, candidate, scope, by_id))
        if stage == "rejected" and not nonempty(candidate.get("rejection_reason")):
            errors.append(f"{cid}: rejection_reason is required.")
        rows.append({"id": cid, "name": candidate.get("name"), "stage": stage,
                     "pass": statuses.count("pass"), "unknown": statuses.count("unknown"),
                     "fail": statuses.count("fail")})
    return errors, rows


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    args = parser.parse_args()
    try:
        if args.batch.stat().st_size > 5_000_000:
            raise ValueError("Input exceeds 5 MB.")
        data = json.loads(args.batch.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    errors, rows = validate(data)
    print(json.dumps({"valid": not errors, "errors": errors, "candidates": rows,
                      "limitation": "Structure and declared gates only; no source-truth or business-success verification."},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
