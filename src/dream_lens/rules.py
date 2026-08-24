from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

from .models import EvidenceRef, Finding, FindingState


RULE_SOURCE_DRIFT = "DIO-SOURCE-001"
RULE_ORPHAN_RELATIONSHIP = "DIO-REL-001"
RULE_FINANCE_CHAIN = "DIO-FIN-001"
RULE_OUTCOME_EVIDENCE = "DIO-OUT-001"
RULE_REQUIRED_EVIDENCE = "DIO-EVID-001"
RULE_TEMPORAL_PLAUSIBILITY = "DIO-TIME-001"


def _evidence_tuple(items: Iterable[EvidenceRef] | None) -> tuple[EvidenceRef, ...]:
    return tuple(items or ())


def source_drift(*, subject: str, left_value: Any, right_value: Any, left_label: str, right_label: str, evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    if left_value is None or right_value is None:
        missing = left_label if left_value is None else right_label
        return Finding(RULE_SOURCE_DRIFT, FindingState.INCOMPLETE, subject, f"Cannot compare representations because {missing} is absent.", "The consistency question is unresolved; absence does not establish cause, responsibility, or invalidity.", refs, (f"Acquire the missing {missing} representation.",))
    if left_value == right_value:
        return Finding(RULE_SOURCE_DRIFT, FindingState.CONSISTENT, subject, f"{left_label} and {right_label} represent the same value.", "No source-representation inconsistency was observed for this field.", refs)
    return Finding(RULE_SOURCE_DRIFT, FindingState.CONTRADICTORY, subject, f"{left_label} and {right_label} represent different values.", "This is a representation-level contradiction only. Synchronization delay, revision, mapping differences, or data error remain possible explanations.", refs, ("Check authoritative revision history and source timestamps.",))


def orphan_relationship(*, subject: str, related_id: str | None, resolvable_ids: set[str], evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    if not related_id:
        return Finding(RULE_ORPHAN_RELATIONSHIP, FindingState.INCOMPLETE, subject, "The relationship identifier is absent.", "The relationship cannot be evaluated.", refs, ("Acquire the relationship identifier.",))
    if related_id in resolvable_ids:
        return Finding(RULE_ORPHAN_RELATIONSHIP, FindingState.CONSISTENT, subject, f"Relationship {related_id} resolves in the supplied evidence set.", "The relationship is internally resolvable for this snapshot.", refs)
    return Finding(RULE_ORPHAN_RELATIONSHIP, FindingState.UNRESOLVED, subject, f"Relationship {related_id} does not resolve in the supplied evidence set.", "The relationship is unresolved in this evidence set. This does not establish that the upstream relationship is invalid or improperly created.", refs, ("Check the authoritative related-process source and synchronization state.",))


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def finance_chain(*, subject: str, expected: Any, available: Any, disbursed: Any, spent: Any, evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    raw = {"expected": expected, "available": available, "disbursed": disbursed, "spent": spent}
    parsed = {name: _decimal(value) for name, value in raw.items()}
    if any(value is None for value in parsed.values()):
        missing = [name for name, value in parsed.items() if value is None]
        return Finding(RULE_FINANCE_CHAIN, FindingState.INCOMPLETE, subject, f"Financial chain cannot be evaluated for fields: {', '.join(missing)}.", "Missing or non-numeric values prevent a deterministic comparison.", refs, ("Acquire numeric values for all compared finance fields from the same observation scope.",))
    if any(value < 0 for value in parsed.values() if value is not None):
        return Finding(RULE_FINANCE_CHAIN, FindingState.REQUIRES_HUMAN_REVIEW, subject, "At least one financing value is negative.", "The value requires semantic review because adjustments or accounting conventions may explain it. No cause, responsibility, or legal conclusion is inferred.", refs, ("Verify finance-field semantics and authoritative adjustment records.",))
    exp, avail, disb, used = parsed["expected"], parsed["available"], parsed["disbursed"], parsed["spent"]
    assert exp is not None and avail is not None and disb is not None and used is not None
    violations: list[str] = []
    if avail > exp: violations.append("available > expected")
    if disb > avail: violations.append("disbursed > available")
    if used > disb: violations.append("spent > disbursed")
    if violations:
        return Finding(RULE_FINANCE_CHAIN, FindingState.REQUIRES_HUMAN_REVIEW, subject, "Financial ordering differs from the provisional comparison model: " + "; ".join(violations) + ".", "This rule is a consistency lens, not an accounting judgment. Timing, revisions, classification, or field semantics can legitimately produce these relationships.", refs, ("Check funding revisions, field definitions, and observation timestamps before interpretation.",))
    return Finding(RULE_FINANCE_CHAIN, FindingState.CONSISTENT, subject, "The observed finance values satisfy expected ≥ available ≥ disbursed ≥ spent.", "No inconsistency was found under the provisional finance-ordering rule.", refs)


def temporal_plausibility(*, subject: str, project_duration_months: Any, feasibility_months: Any = None, implementation_months: Any = None, max_review_months: int = 1200, evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    project = _decimal(project_duration_months)
    feasibility = _decimal(feasibility_months)
    implementation = _decimal(implementation_months)
    if project is None:
        return Finding(RULE_TEMPORAL_PLAUSIBILITY, FindingState.INCOMPLETE, subject, "Project duration is absent or non-numeric.", "The timeline cannot be evaluated.", refs, ("Acquire the represented project duration and unit.",))
    if project < 0 or (feasibility is not None and feasibility < 0) or (implementation is not None and implementation < 0):
        return Finding(RULE_TEMPORAL_PLAUSIBILITY, FindingState.REQUIRES_HUMAN_REVIEW, subject, "At least one represented duration is negative.", "The duration requires source-semantic review; no cause or responsibility is inferred.", refs, ("Verify source duration values and units.",))
    if feasibility is not None and implementation is not None and feasibility + implementation != project:
        return Finding(RULE_TEMPORAL_PLAUSIBILITY, FindingState.CONTRADICTORY, subject, f"Project duration {project} months does not equal feasibility + implementation ({feasibility + implementation} months).", "This is a numeric representation contradiction only; source definitions or stage overlap may explain it.", refs, ("Verify authoritative duration definitions and whether stages overlap.",))
    if project > Decimal(max_review_months):
        return Finding(RULE_TEMPORAL_PLAUSIBILITY, FindingState.REQUIRES_HUMAN_REVIEW, subject, f"Project duration is represented as {project} months, above the review threshold of {max_review_months} months.", "The value is internally arithmetic-consistent where subperiods are supplied, but its unit or magnitude warrants source review. No cause, intent, responsibility, or legal conclusion is inferred.", refs, ("Verify the source unit, data-entry value, and authoritative project schedule.",))
    return Finding(RULE_TEMPORAL_PLAUSIBILITY, FindingState.CONSISTENT, subject, f"Project duration {project} months is within the configured review threshold.", "No timeline plausibility issue was observed under this rule.", refs)


def outcome_evidence(*, subject: str, completed: bool, expected_outcomes: list[str] | None, measured_outcomes: dict[str, Any] | None, evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    if not completed:
        return Finding(RULE_OUTCOME_EVIDENCE, FindingState.OUTCOME_NOT_YET_MEASURABLE, subject, "The project is not represented as completed in the supplied record.", "Completion-dependent outcome evidence is not required by this rule yet.", refs)
    if not expected_outcomes:
        return Finding(RULE_OUTCOME_EVIDENCE, FindingState.INCOMPLETE, subject, "The completed project has no expected outcomes in the supplied normalized record.", "Outcome assurance cannot determine what should be measured.", refs, ("Acquire the authoritative expected-outcome definition.",))
    measured_outcomes = measured_outcomes or {}
    missing = [name for name in expected_outcomes if name not in measured_outcomes]
    if missing:
        return Finding(RULE_OUTCOME_EVIDENCE, FindingState.INCOMPLETE, subject, "Measured outcome evidence is absent for: " + ", ".join(missing) + ".", "An evidence gap is not evidence that the project failed to achieve the outcome.", refs, tuple(f"Acquire measurement evidence for {name}." for name in missing))
    return Finding(RULE_OUTCOME_EVIDENCE, FindingState.CONSISTENT, subject, "Each expected outcome has a supplied measurement value.", "Outcome evidence is present; this rule does not independently validate measurement quality.", refs)


def required_evidence(*, subject: str, required_keys: list[str], evidence_record: dict[str, Any], evidence: Iterable[EvidenceRef] | None = None) -> Finding:
    refs = _evidence_tuple(evidence)
    missing = [key for key in required_keys if evidence_record.get(key) in (None, "", [])]
    if missing:
        return Finding(RULE_REQUIRED_EVIDENCE, FindingState.INCOMPLETE, subject, "Required evidence fields are absent: " + ", ".join(missing) + ".", "The represented transition is not fully evidenced in the supplied record.", refs, tuple(f"Acquire {key}." for key in missing))
    return Finding(RULE_REQUIRED_EVIDENCE, FindingState.CONSISTENT, subject, "All required evidence fields are present.", "Presence is established; authenticity and legal sufficiency remain source-authority questions.", refs)
