"""Offline regression tests using only Python's standard library.

Run from the repository root:
    python -B -m unittest discover -s tests -v

Set NICHE_SOURCING_SKILL_DIR to test another checkout's skill directory.
All sellers, evidence, prices and outcomes below are synthetic. Passing these
tests confirms declared-input behavior, not market truth or business success.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL_DIRECTORY = Path(
    os.environ.get(
        "NICHE_SOURCING_SKILL_DIR",
        str(REPOSITORY / "skills" / "niche-aesthetic-sourcing"),
    )
)
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "test-ready.json"


def load_script(name):
    path = SKILL_DIRECTORY / "scripts" / f"{name}.py"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing skill script: {path}. Set NICHE_SOURCING_SKILL_DIR "
            "to a skill directory containing scripts/."
        )
    spec = importlib.util.spec_from_file_location(f"workflow_tests_{name}", path)
    module = importlib.util.module_from_spec(spec)
    # Loading the checked scripts must not add generated files to the skill.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


CHECKER = load_script("check_batch")
TRIAL_ANALYZER = load_script("analyze_trial")


def ready_batch():
    """Return a fresh fixture so mutations cannot leak between tests."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def discovery_batch():
    """Discovery is allowed before identity, channel or demand are known."""
    data = ready_batch()
    for key in (
        "seller_country", "seller_entity", "target_country", "target_channel",
        "ship_from", "budget", "currency",
    ):
        data["scope"][key] = None
    data["sources"] = []
    candidate = data["candidates"][0]
    candidate["stage"] = "discovery"
    candidate["gates"] = {
        key: {
            "status": "unknown",
            "rationale": "Synthetic fixture: evidence has not been collected.",
            "source_ids": [],
        }
        for key in CHECKER.GATES
    }
    for key in ("channel_access", "test_costs", "pilot", "funding_plan"):
        candidate.pop(key, None)
    return data


def synthetic_source(source_id, kind, metrics):
    return {
        "id": source_id,
        "title": f"Synthetic test source: {source_id}",
        "publisher": "synthetic fixture; no real buyer or seller",
        "independence_key": f"synthetic:{source_id}",
        "kind": kind,
        "url": f"https://example.invalid/{source_id}",
        "retrieved_at": "2026-10-02",
        "content_origin": "user_supplied",
        "market": "US",
        "data_scope": "sku",
        "metrics": metrics,
        "observation": "SYNTHETIC ONLY: invented observation for regression tests.",
        "limitations": "No real transaction, market fact or operating evidence.",
    }


def demand_batch():
    data = discovery_batch()
    data["scope"]["target_country"] = "US"
    data["sources"] = [synthetic_source(
        "SALES", "transaction_record", [{
            "name": "paid_orders", "value": 12, "unit": "orders",
            "scope": "sku", "basis": "transaction",
        }],
    )]
    data["candidates"][0]["gates"]["demand"] = {
        "status": "pass",
        "rationale": "Synthetic declared paid-purchase record.",
        "source_ids": ["SALES"],
        "details": {
            "target_country": "US",
            "measurement_scope": "sku",
            "sample_size": 12,
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "decision_threshold": "Synthetic threshold declared before evaluation.",
            "threshold_met": True,
        },
    }
    return data


def premium_batch():
    data = discovery_batch()
    data["scope"]["target_country"] = "US"
    data["sources"] = [synthetic_source(
        "MATCHED", "matched_comparison", [{
            "name": "median_sold_price", "value": 20, "currency": "USD",
            "unit": "USD_per_order", "scope": "sku", "basis": "transaction",
        }],
    )]
    data["candidates"][0]["gates"]["aesthetic_premium"] = {
        "status": "pass",
        "rationale": "Synthetic declared comparable prices.",
        "source_ids": ["MATCHED"],
        "details": {
            "price_basis": "transaction",
            "currency": "USD",
            "design_price": 20,
            "baseline_price": 10,
            "sample_size": 12,
            "matched_controls": [
                "material", "size", "function", "brand", "market", "delivery",
            ],
            "confound_reviewed": True,
            "decision_threshold": "Synthetic comparison threshold.",
            "threshold_met": True,
        },
    }
    return data


def amount(value):
    return {
        "low": value,
        "high": value,
        "basis": "SYNTHETIC ONLY: declared test amount, including zero charges.",
        "source_ids": ["SYNTHETIC-COST"],
    }


def trial_result(buyers, orders):
    """Invent a single deduplicated visitor cohort; do not imply actual sales."""
    values = {
        "product": 7, "packaging": 1, "delivery": 5,
        "platform_payment": 2, "taxes": 0, "returns": 0,
        "fulfillment_labor": 1, "design_allocated": 1, "other_variable": 0,
    }
    return {
        "schema_version": "1.0",
        "data_status": "synthetic",
        "currency": "USD",
        "boundary": "SYNTHETIC ONLY: buyer payment and all declared per-order charges; acquisition cash recorded separately.",
        "buyer_payment": amount(30),
        "costs": {key: amount(value) for key, value in values.items()},
        "min_contribution": 3,
        "fixed_setup": amount(10),
        "funnel": {
            "qualified_unique_visitors": 100,
            "paid_buyers": buyers,
            "paid_orders": orders,
            "measurement_basis": "Synthetic single cohort; unique visitors and buyers deduplicated; repeat orders counted separately.",
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "acquisition_investment": amount(60),
        },
    }


class WorkflowTests(unittest.TestCase):
    def assert_valid_batch(self, data):
        errors, rows = CHECKER.validate(data)
        self.assertEqual([], errors, "\n".join(errors))
        return rows

    def assert_invalid_batch(self, data, expected_error):
        errors, rows = CHECKER.validate(data)
        self.assertTrue(errors, "Contradictory input was accepted.")
        self.assertTrue(
            any(expected_error in error for error in errors),
            f"Expected {expected_error!r}; received {errors!r}",
        )
        return rows

    def test_discovery_accepts_unknown_seller_market_and_demand(self):
        rows = self.assert_valid_batch(discovery_batch())
        self.assertEqual("discovery", rows[0]["stage"])
        self.assertEqual(6, rows[0]["unknown"])
        self.assertEqual(0, rows[0]["pass"])

    def test_test_ready_does_not_require_demand_to_be_proven_in_advance(self):
        data = ready_batch()
        self.assertEqual("synthetic", data["data_status"])
        self.assertIn("SYNTHETIC ONLY", data["limitation"])
        self.assertEqual([], data["scope"]["authorization"])
        self.assertEqual(150, data["scope"]["budget"])
        rows = self.assert_valid_batch(data)
        self.assertEqual("test_ready", rows[0]["stage"])
        self.assertEqual(4, rows[0]["unknown"])
        self.assertEqual(2, rows[0]["pass"])
        for gate in ("demand", "aesthetic_premium", "competition_gap", "unit_economics"):
            self.assertEqual("unknown", data["candidates"][0]["gates"][gate]["status"])

    def test_latest_user_budget_invalidates_previously_ready_plan(self):
        data = ready_batch()
        self.assert_valid_batch(data)
        data["scope"]["budget"] = 25
        self.assert_invalid_batch(data, "trial budget exceeds the current scope user budget")
        self.assert_invalid_batch(data, "exceeds or lacks current user budget")

    def test_latest_user_currency_cannot_reuse_unconverted_cost_plan(self):
        data = ready_batch()
        data["scope"]["currency"] = "EUR"
        self.assert_invalid_batch(data, "trial currency conflicts with the current scope currency")
        self.assert_invalid_batch(data, "scope, trial and funding currencies must match")

    def test_demand_requires_consistent_source_metric_scope_and_market(self):
        valid = demand_batch()
        self.assert_valid_batch(valid)
        for field, replacement in (
            ("data_scope", "defined_niche"), ("metric_scope", "defined_niche"),
            ("market", "UK"),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(valid)
                source = data["sources"][0]
                if field == "metric_scope":
                    source["metrics"][0]["scope"] = replacement
                else:
                    source[field] = replacement
                self.assert_invalid_batch(data, "requires attributable paid-purchase metrics")

    def test_sold_price_evidence_cannot_contradict_market_or_currency(self):
        valid = premium_batch()
        self.assert_valid_batch(valid)
        for field, replacement, expected in (
            ("market", "UK", "sold-price source market cannot contradict"),
            ("currency", "GBP", "sold-price currency cannot contradict"),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(valid)
                source = data["sources"][0]
                if field == "currency":
                    source["metrics"][0]["currency"] = replacement
                else:
                    source[field] = replacement
                self.assert_invalid_batch(data, expected)

    def test_inventory_must_cover_moq_and_its_cash_commitment(self):
        with self.subTest(case="quantity_below_moq"):
            data = ready_batch()
            inventory = data["candidates"][0]["funding_plan"]["cash_components"]["inventory"]
            inventory["quantity"] = 4
            self.assert_invalid_batch(data, "inventory quantity must cover the quoted MOQ")
        with self.subTest(case="large_moq_exceeds_budget"):
            data = ready_batch()
            inventory = data["candidates"][0]["funding_plan"]["cash_components"]["inventory"]
            inventory.update(quantity=700, quote_minimum_quantity=700, high=4905)
            self.assert_invalid_batch(data, "exceeds or lacks current user budget")

    def test_whole_trial_funding_must_fit_budget_and_affordable_loss(self):
        with self.subTest(limit="current_user_budget"):
            data = ready_batch()
            # Per-order loss remains affordable, but total trial cash is 150.
            data["scope"]["budget"] = 145
            data["candidates"][0]["pilot"]["budget_cap"] = 145
            self.assert_invalid_batch(data, "whole-trial maximum cash commitment 150 exceeds or lacks current user budget")
        with self.subTest(limit="affordable_loss"):
            data = ready_batch()
            data["candidates"][0]["funding_plan"]["max_affordable_loss"] = 145
            self.assert_invalid_batch(data, "whole-trial maximum cash commitment 150 exceeds or lacks affordable loss")

    def test_whole_trial_acquisition_cannot_be_replaced_by_per_order_cap(self):
        data = ready_batch()
        candidate = data["candidates"][0]
        self.assertEqual(10, candidate["test_costs"]["acquisition_cap_per_order"])
        self.assertEqual(50, candidate["pilot"]["acquisition_budget_cap"])
        candidate["funding_plan"]["cash_components"]["acquisition"]["high"] = 10
        self.assert_invalid_batch(data, "whole-trial acquisition commitment must cover the planned cash spend cap")

    def test_funding_cannot_omit_inbound_shipping_or_expense_group(self):
        with self.subTest(case="omitted_inbound"):
            data = ready_batch()
            inventory = data["candidates"][0]["funding_plan"]["cash_components"]["inventory"]
            inventory["high"] = 35
            self.assert_invalid_batch(data, "inventory cash maximum must cover quantity times unit cost plus inbound cash costs")
        with self.subTest(case="omitted_samples_setup"):
            data = ready_batch()
            del data["candidates"][0]["funding_plan"]["cash_components"]["samples_setup"]
            self.assert_invalid_batch(data, "all six whole-trial cash expense groups are required")

    def test_zero_orders_retains_spend_but_per_order_profit_is_unknown(self):
        result = TRIAL_ANALYZER.analyze(trial_result(buyers=0, orders=0))
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual("synthetic", result["data_status"])
        self.assertEqual({"low": 60, "high": 60}, result["acquisition_investment_total"])
        self.assertEqual(0, result["purchase_conversion"])
        self.assertIsNone(result["investment_per_paid_buyer"])
        self.assertIsNone(result["investment_per_paid_order"])
        self.assertIsNone(result["after_acquisition_per_order"])
        self.assertIsNone(result["fixed_setup_recovery_orders_scenario"])
        self.assertEqual("no_observed_paid_orders_cost_per_order_undefined", result["decision"])

    def test_repeat_orders_do_not_inflate_unique_buyer_conversion(self):
        result = TRIAL_ANALYZER.analyze(trial_result(buyers=2, orders=6))
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(0.02, result["purchase_conversion"])
        self.assertEqual({"low": 30, "high": 30}, result["investment_per_paid_buyer"])
        self.assertEqual({"low": 10, "high": 10}, result["investment_per_paid_order"])
        self.assertEqual({"low": 13, "high": 13}, result["before_acquisition_per_order"])
        self.assertEqual({"low": 3, "high": 3}, result["after_acquisition_per_order"])
        self.assertEqual("declared_conservative_margin_meets_goal", result["decision"])


if __name__ == "__main__":
    unittest.main()
