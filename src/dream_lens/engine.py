from __future__ import annotations

from typing import Any

from .evidence import sha256_json
from .models import EvidenceRef, Finding
from .rules import finance_chain, orphan_relationship, outcome_evidence, required_evidence, source_drift

BUNDLE_VERSION = "0.1"


def _refs(record: dict[str, Any]) -> tuple[EvidenceRef, ...]:
    refs: list[EvidenceRef] = []
    for item in record.get("evidence", []):
        refs.append(EvidenceRef(source=str(item["source"]), source_id=item.get("source_id"), authority_scope=item.get("authority_scope"), observed_at=item.get("observed_at"), sha256=item.get("sha256")))
    return tuple(refs)


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a normalized audit record into a deterministic evidence bundle."""
    project_id = str(record.get("project_id") or "unknown-project")
    refs = _refs(record)
    findings: list[Finding] = []
    for comparison in record.get("source_comparisons", []):
        findings.append(source_drift(subject=f"{project_id}:{comparison['field']}", left_value=comparison.get("left_value"), right_value=comparison.get("right_value"), left_label=str(comparison.get("left_label", "left source")), right_label=str(comparison.get("right_label", "right source")), evidence=refs))
    for relationship in record.get("relationships", []):
        findings.append(orphan_relationship(subject=f"{project_id}:{relationship.get('relationship', 'relationship')}", related_id=relationship.get("related_id"), resolvable_ids=set(relationship.get("resolvable_ids", [])), evidence=refs))
    finance = record.get("finance")
    if isinstance(finance, dict):
        findings.append(finance_chain(subject=f"{project_id}:finance", expected=finance.get("expected"), available=finance.get("available"), disbursed=finance.get("disbursed"), spent=finance.get("spent"), evidence=refs))
    outcome = record.get("outcome")
    if isinstance(outcome, dict):
        findings.append(outcome_evidence(subject=f"{project_id}:outcome", completed=bool(outcome.get("completed", False)), expected_outcomes=outcome.get("expected_outcomes"), measured_outcomes=outcome.get("measured_outcomes"), evidence=refs))
    transition_evidence = record.get("transition_evidence")
    if isinstance(transition_evidence, dict):
        findings.append(required_evidence(subject=f"{project_id}:transition-evidence", required_keys=list(transition_evidence.get("required_keys", [])), evidence_record=dict(transition_evidence.get("record", {})), evidence=refs))
    bundle_core = {
        "bundle_version": BUNDLE_VERSION,
        "project_id": project_id,
        "record_sha256": sha256_json(record),
        "findings": [finding.as_dict() for finding in findings],
        "inference_boundary": "Findings describe evidence state and deterministic consistency only; they do not establish cause, intent, responsibility, attribution, ownership, or legal conclusions.",
    }
    return {**bundle_core, "bundle_sha256": sha256_json(bundle_core)}
