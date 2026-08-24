from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FindingState(StrEnum):
    CONSISTENT = "CONSISTENT"
    INCOMPLETE = "INCOMPLETE"
    STALE = "STALE"
    CONTRADICTORY = "CONTRADICTORY"
    UNRESOLVED = "UNRESOLVED"
    OUTCOME_NOT_YET_MEASURABLE = "OUTCOME_NOT_YET_MEASURABLE"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


@dataclass(frozen=True)
class EvidenceRef:
    source: str
    source_id: str | None = None
    authority_scope: str | None = None
    observed_at: str | None = None
    sha256: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "authority_scope": self.authority_scope,
            "observed_at": self.observed_at,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    state: FindingState
    subject: str
    observation: str
    interpretation: str
    evidence: tuple[EvidenceRef, ...] = field(default_factory=tuple)
    next_evidence: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "state": self.state.value,
            "subject": self.subject,
            "observation": self.observation,
            "interpretation": self.interpretation,
            "evidence": [item.as_dict() for item in self.evidence],
            "next_evidence": list(self.next_evidence),
        }
