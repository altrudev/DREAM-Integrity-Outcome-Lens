from __future__ import annotations

import json
import unittest
from pathlib import Path

from dream_lens.adapters.dream import DreamPublicApiClient
from dream_lens.engine import evaluate
from dream_lens.evidence import sha256_json, snapshot_envelope
from dream_lens.models import FindingState
from dream_lens.normalization import normalize_portal_observation, normalize_public_project
from dream_lens.rules import finance_chain, orphan_relationship, outcome_evidence, source_drift, temporal_plausibility

FIXTURE = Path(__file__).parent / "fixtures" / "sample_record.json"
LIVE_HEAL = Path(__file__).parent / "fixtures" / "live" / "heal-040825-30fc5b9e.json"
LIVE_TRANSPORT = Path(__file__).parent / "fixtures" / "live" / "ten-t-070825-07bff93a.json"
EXPECTED_INFERENCE_BOUNDARY = "Findings describe evidence state and deterministic consistency only; they do not establish cause, intent, responsibility, attribution, ownership, or legal conclusions."


class EvidenceTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self) -> None:
        self.assertEqual(sha256_json({"b": 2, "a": 1}), sha256_json({"a": 1, "b": 2}))

    def test_snapshot_hashes_payload_only(self) -> None:
        payload = {"title": "Тест", "value": 1}
        envelope = snapshot_envelope(source_url="https://example.invalid", observed_at="2026-01-01T00:00:00Z", payload=payload)
        self.assertEqual(envelope["payload_sha256"], sha256_json(payload))


class NormalizationTests(unittest.TestCase):
    def test_public_project_normalization_selects_highest_budget_active_approach(self) -> None:
        payload = {
            "internal": {"id": "uuid-1", "code": "070825-TEST"},
            "cdu_response": {
                "title": [{"lang": "uk", "translation": "Тестовий проєкт"}, {"lang": "en", "translation": "Test project"}],
                "status": "active",
                "parties": [{"roles": ["initiator"], "identifier": {"legalName": "Ініціатор"}}],
                "relatedProcesses": [{"relationship": "sectoralPipeline", "identifier": "sp-1", "details": {"status": "active", "relatedItem": "stream-1"}}],
                "approaches": [
                    {"id": "a-small", "status": "active", "budget": {"valueBreakdown": [{"value": {"amount": 10}}]}},
                    {
                        "id": "a-large",
                        "status": "active",
                        "title": [{"lang": "uk", "translation": "Обране рішення"}],
                        "budget": {
                            "valueBreakdown": [{"value": {"amount": 20}}, {"value": {"amount": 5}}],
                            "finance": [{"id": "f1", "value": {"amount": 25}}],
                        },
                        "implementation": {
                            "financialProgress": {
                                "breakdown": [
                                    {"classifications": {"budgetFinanceId": "f1"}, "measure": {"available": 20, "disbursed": 15, "spent": 10}},
                                    {"classifications": {"budgetFinanceId": "other-source"}, "measure": {"available": 999, "disbursed": 999, "spent": 999}},
                                ]
                            }
                        },
                    },
                ],
            },
        }
        normalized = normalize_public_project(payload)
        self.assertEqual(normalized["schema_version"], "0.2")
        self.assertEqual(normalized["project_id"], "070825-TEST")
        self.assertEqual(normalized["title"], "Тестовий проєкт")
        self.assertEqual(normalized["initiator"], "Ініціатор")
        self.assertEqual(normalized["selected_approach"]["id"], "a-large")
        self.assertEqual(normalized["selected_approach"]["budget_breakdown_total"], "25")
        self.assertEqual(normalized["finance"], {"expected": "25", "available": "20", "disbursed": "15", "spent": "10"})

    def test_portal_observation_normalization_preserves_timeline(self) -> None:
        raw = json.loads(LIVE_TRANSPORT.read_text(encoding="utf-8"))
        normalized = normalize_portal_observation(raw)
        self.assertEqual(normalized["project_id"], "DREAM-UA-070825-07BFF93A")
        self.assertEqual(normalized["timeline"]["project_duration_months"], 72)


class RuleTests(unittest.TestCase):
    def test_source_drift_consistent(self) -> None:
        self.assertEqual(source_drift(subject="p:status", left_value="a", right_value="a", left_label="api", right_label="portal").state, FindingState.CONSISTENT)

    def test_source_drift_contradictory_preserves_inference_boundary(self) -> None:
        finding = source_drift(subject="p:status", left_value="a", right_value="b", left_label="api", right_label="portal")
        self.assertEqual(finding.state, FindingState.CONTRADICTORY)
        self.assertIn("representation-level", finding.interpretation)

    def test_orphan_relationship(self) -> None:
        self.assertEqual(orphan_relationship(subject="p:rel", related_id="missing", resolvable_ids={"other"}).state, FindingState.UNRESOLVED)

    def test_finance_chain_consistent(self) -> None:
        self.assertEqual(finance_chain(subject="p:finance", expected=100, available=90, disbursed=80, spent=70).state, FindingState.CONSISTENT)

    def test_finance_chain_violation_requires_review(self) -> None:
        self.assertEqual(finance_chain(subject="p:finance", expected=100, available=90, disbursed=80, spent=95).state, FindingState.REQUIRES_HUMAN_REVIEW)

    def test_temporal_arithmetic_contradiction(self) -> None:
        finding = temporal_plausibility(subject="p:timeline", project_duration_months=72, feasibility_months=24, implementation_months=47)
        self.assertEqual(finding.state, FindingState.CONTRADICTORY)

    def test_outcome_gap_is_incomplete_not_failure(self) -> None:
        finding = outcome_evidence(subject="p:out", completed=True, expected_outcomes=["capacity"], measured_outcomes={})
        self.assertEqual(finding.state, FindingState.INCOMPLETE)
        self.assertIn("not evidence", finding.interpretation)


class EngineTests(unittest.TestCase):
    def test_fixture_evaluates_deterministically(self) -> None:
        record = json.loads(FIXTURE.read_text(encoding="utf-8"))
        first, second = evaluate(record), evaluate(record)
        self.assertEqual(first, second)
        self.assertEqual(first["bundle_sha256"], second["bundle_sha256"])
        self.assertTrue(all(f["state"] == "CONSISTENT" for f in first["findings"]))

    def test_bundle_states_are_from_closed_taxonomy(self) -> None:
        record = json.loads(FIXTURE.read_text(encoding="utf-8"))
        bundle = evaluate(record)
        allowed = {state.value for state in FindingState}
        self.assertTrue(all(item["state"] in allowed for item in bundle["findings"]))

    def test_bundle_inference_boundary_is_attribution_neutral(self) -> None:
        record = json.loads(FIXTURE.read_text(encoding="utf-8"))
        bundle = evaluate(record)
        self.assertEqual(bundle["inference_boundary"], EXPECTED_INFERENCE_BOUNDARY)

    def test_heal_public_observation_requires_timeline_review(self) -> None:
        record = json.loads(LIVE_HEAL.read_text(encoding="utf-8"))
        bundle = evaluate(record)
        self.assertEqual(len(bundle["findings"]), 1)
        self.assertEqual(bundle["findings"][0]["rule_id"], "DIO-TIME-001")
        self.assertEqual(bundle["findings"][0]["state"], "REQUIRES_HUMAN_REVIEW")

    def test_transport_public_observation_is_timeline_consistent(self) -> None:
        record = json.loads(LIVE_TRANSPORT.read_text(encoding="utf-8"))
        bundle = evaluate(record)
        self.assertEqual(len(bundle["findings"]), 1)
        self.assertEqual(bundle["findings"][0]["state"], "CONSISTENT")


class AdapterBoundaryTests(unittest.TestCase):
    def test_rejects_non_allowlisted_host(self) -> None:
        with self.assertRaises(ValueError): DreamPublicApiClient(base_url="https://example.com")

    def test_rejects_non_https(self) -> None:
        with self.assertRaises(ValueError): DreamPublicApiClient(base_url="http://public-api.dream.gov.ua")

    def test_rejects_path_in_base_url(self) -> None:
        with self.assertRaises(ValueError): DreamPublicApiClient(base_url="https://public-api.dream.gov.ua/other")

    def test_rejects_project_id_path_escape(self) -> None:
        with self.assertRaises(ValueError): DreamPublicApiClient().get_project("../secret")


if __name__ == "__main__":
    unittest.main()
