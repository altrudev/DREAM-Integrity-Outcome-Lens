from __future__ import annotations

import json
import unittest
from pathlib import Path

from dream_lens.adapters.dream import DreamPublicApiClient
from dream_lens.engine import evaluate
from dream_lens.evidence import sha256_json, snapshot_envelope
from dream_lens.models import FindingState
from dream_lens.rules import finance_chain, orphan_relationship, outcome_evidence, source_drift

FIXTURE = Path(__file__).parent / "fixtures" / "sample_record.json"


class EvidenceTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self) -> None:
        self.assertEqual(sha256_json({"b": 2, "a": 1}), sha256_json({"a": 1, "b": 2}))

    def test_snapshot_hashes_payload_only(self) -> None:
        payload = {"title": "Тест", "value": 1}
        envelope = snapshot_envelope(source_url="https://example.invalid", observed_at="2026-01-01T00:00:00Z", payload=payload)
        self.assertEqual(envelope["payload_sha256"], sha256_json(payload))


class RuleTests(unittest.TestCase):
    def test_source_drift_consistent(self) -> None:
        self.assertEqual(source_drift(subject="p:status", left_value="a", right_value="a", left_label="api", right_label="portal").state, FindingState.CONSISTENT)

    def test_source_drift_contradictory_is_not_misconduct_claim(self) -> None:
        finding = source_drift(subject="p:status", left_value="a", right_value="b", left_label="api", right_label="portal")
        self.assertEqual(finding.state, FindingState.CONTRADICTORY)
        self.assertIn("representation-level", finding.interpretation)

    def test_orphan_relationship(self) -> None:
        self.assertEqual(orphan_relationship(subject="p:rel", related_id="missing", resolvable_ids={"other"}).state, FindingState.UNRESOLVED)

    def test_finance_chain_consistent(self) -> None:
        self.assertEqual(finance_chain(subject="p:finance", expected=100, available=90, disbursed=80, spent=70).state, FindingState.CONSISTENT)

    def test_finance_chain_violation_requires_review(self) -> None:
        self.assertEqual(finance_chain(subject="p:finance", expected=100, available=90, disbursed=80, spent=95).state, FindingState.REQUIRES_HUMAN_REVIEW)

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
