from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ALLOWED_FINDING_STATES = {"CONSISTENT", "INCOMPLETE", "STALE", "CONTRADICTORY", "UNRESOLVED", "OUTCOME_NOT_YET_MEASURABLE", "REQUIRES_HUMAN_REVIEW"}
FORBIDDEN_AUTOMATED_STATES = {"CORRUPT", "FRAUD", "CRIMINAL", "THEFT", "GUILTY"}


def main() -> int:
    failures: list[str] = []
    for path in list(SRC.rglob("*.py")) + list((ROOT / "tests").rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax: {path}: {exc}")
    from dream_lens.models import FindingState
    actual = {state.value for state in FindingState}
    if actual != ALLOWED_FINDING_STATES: failures.append(f"finding taxonomy drift: {sorted(actual)}")
    if actual & FORBIDDEN_AUTOMATED_STATES: failures.append(f"forbidden automated conclusion states: {sorted(actual & FORBIDDEN_AUTOMATED_STATES)}")
    if failures:
        for failure in failures: print(f"FAIL {failure}")
        return 1
    print("PASS DDC audit: syntax, closed finding taxonomy, inference boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
