from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"

ALLOWED_FINDING_STATES = {
    "CONSISTENT",
    "INCOMPLETE",
    "STALE",
    "CONTRADICTORY",
    "UNRESOLVED",
    "OUTCOME_NOT_YET_MEASURABLE",
    "REQUIRES_HUMAN_REVIEW",
}
EXPECTED_INFERENCE_BOUNDARY = (
    "Findings describe evidence state and deterministic consistency only; "
    "they do not establish cause, intent, responsibility, attribution, ownership, or legal conclusions."
)
EXPECTED_DREAM_HOSTS = {"public-api.dream.gov.ua"}
PUBLIC_POSITIONING_DOCS = (
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "rule-catalog.md",
    ROOT / "docs" / "trust-model.md",
    ROOT / "docs" / "evidence-report-2026-08-24.md",
)
DOMAIN_SPECIFIC_FOREGROUNDING_TERMS = ("corruption", "fraud", "theft", "criminality", "misconduct")
DISALLOWED_HTTP_WRITE_MARKERS = ('method="POST"', "method='POST'", 'method="PUT"', "method='PUT'", 'method="PATCH"', "method='PATCH'", 'method="DELETE"', "method='DELETE'")
REAL_DATA_EXPECTATIONS = {
    "heal-040825-30fc5b9e.json": "REQUIRES_HUMAN_REVIEW",
    "ten-t-070825-07bff93a.json": "CONSISTENT",
}


def main() -> int:
    failures: list[str] = []

    python_paths = list(SRC.rglob("*.py")) + list(TESTS.rglob("*.py")) + [Path(__file__)]
    for path in python_paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax: {path}: {exc}")

    from dream_lens.adapters.dream import ALLOWED_HOSTS
    from dream_lens.engine import evaluate
    from dream_lens.models import FindingState

    actual_states = {state.value for state in FindingState}
    if actual_states != ALLOWED_FINDING_STATES:
        failures.append(f"finding taxonomy drift: {sorted(actual_states)}")

    if set(ALLOWED_HOSTS) != EXPECTED_DREAM_HOSTS:
        failures.append(f"network authority drift: {sorted(ALLOWED_HOSTS)}")

    fixture_path = TESTS / "fixtures" / "sample_record.json"
    record = json.loads(fixture_path.read_text(encoding="utf-8"))
    first = evaluate(record)
    second = evaluate(record)
    if first != second:
        failures.append("determinism: identical normalized input produced different bundles")
    if first.get("inference_boundary") != EXPECTED_INFERENCE_BOUNDARY:
        failures.append("inference boundary drift")
    emitted_states = {item.get("state") for item in first.get("findings", [])}
    if not emitted_states.issubset(ALLOWED_FINDING_STATES):
        failures.append(f"emitted state outside closed taxonomy: {sorted(emitted_states - ALLOWED_FINDING_STATES)}")

    live_dir = TESTS / "fixtures" / "live"
    for filename, expected_state in REAL_DATA_EXPECTATIONS.items():
        live_record = json.loads((live_dir / filename).read_text(encoding="utf-8"))
        parsed = urlparse(str(live_record.get("source_url") or ""))
        if parsed.scheme != "https" or parsed.hostname != "dream.gov.ua":
            failures.append(f"real-data provenance: {filename} must point to https://dream.gov.ua")
        if not live_record.get("observed_at") and not any(item.get("observed_at") for item in live_record.get("evidence", []) if isinstance(item, dict)):
            failures.append(f"real-data provenance: {filename} lacks observation time")
        live_bundle = evaluate(live_record)
        states = [item.get("state") for item in live_bundle.get("findings", [])]
        if states != [expected_state]:
            failures.append(f"real-data regression: {filename} emitted {states}, expected {[expected_state]}")
        if live_bundle.get("inference_boundary") != EXPECTED_INFERENCE_BOUNDARY:
            failures.append(f"real-data inference boundary drift: {filename}")

    adapter_text = (SRC / "dream_lens" / "adapters" / "dream.py").read_text(encoding="utf-8")
    for marker in DISALLOWED_HTTP_WRITE_MARKERS:
        if marker in adapter_text:
            failures.append(f"write-capable HTTP method marker found in DREAM adapter: {marker}")

    rule_text = (SRC / "dream_lens" / "rules.py").read_text(encoding="utf-8")
    if "REQUIRES_HUMAN_REVIEW" not in rule_text or "max_review_months" not in rule_text:
        failures.append("temporal review policy drift: review threshold no longer routes through human review")

    for path in PUBLIC_POSITIONING_DOCS:
        text = path.read_text(encoding="utf-8").lower()
        for term in DOMAIN_SPECIFIC_FOREGROUNDING_TERMS:
            if term in text:
                failures.append(f"positioning drift: {path.relative_to(ROOT)} foregrounds '{term}'")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("PASS DDC audit")
    print("  syntax: pass")
    print("  closed finding taxonomy: pass")
    print("  deterministic evidence bundle: pass")
    print("  neutral inference boundary: pass")
    print("  fixed DREAM network authority: pass")
    print("  read-only HTTP boundary: pass")
    print("  public positioning boundary: pass")
    print("  real-data provenance: pass")
    print("  real-data regression expectations: pass")
    print("  temporal review-policy boundary: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
