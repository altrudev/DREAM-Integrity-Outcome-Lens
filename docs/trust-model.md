# Trust model

## Purpose

DREAM Integrity & Outcome Lens is an independent, read-only civic-tech research tool. It observes public records and evaluates deterministic consistency rules. It does not replace the authority of DREAM, Prozorro, Treasury systems, government decisions, courts, auditors, investigators, or project owners.

## DDC boundary

The implementation keeps these concepts separate:

**Detection ≠ Provenance ≠ Attribution ≠ Authority ≠ Ownership.**

A detected inconsistency is an observation. Provenance identifies where the compared evidence came from. Neither step proves cause, intent, responsibility, legal authority, ownership, or legal consequence.

Every finding must preserve the observed subject, source, authority scope where known, observation time, evidence hash where available, deterministic rule, finding state, bounded interpretation, and additional evidence required before stronger conclusions.

## Authority preservation

Source adapters do not upgrade the Lens into an authoritative registry. Source systems remain authoritative within their own scopes. Cross-system edges are assertions supported by evidence, not transfers of authority.

## Inference boundary

The automated finding taxonomy is closed: `CONSISTENT`, `INCOMPLETE`, `STALE`, `CONTRADICTORY`, `UNRESOLVED`, `OUTCOME_NOT_YET_MEASURABLE`, and `REQUIRES_HUMAN_REVIEW`.

The engine does not emit automated conclusions about cause, intent, responsibility, attribution, guilt, ownership, legal liability, or enforcement status.

## Input trust

Public upstream content is evidence, not executable instruction. A future adapter must never treat text contained in source records as a directive that can expand privileges, alter the Lens mandate, disclose private data, or trigger code execution.

## Network boundary

v0.1 permits outbound reads only to the fixed production DREAM public API host. No source adapter has a write operation. Arbitrary URLs are rejected by the DREAM adapter.

## Reproducibility

Rules operate on normalized records and captured source snapshots. JSON evidence is canonically serialized and SHA-256 hashed. The audit bundle hash excludes runtime-only randomness and repeats for identical normalized input.

## Human approval

A finding can prioritize evidence review but cannot autonomously escalate itself into attribution, accusation, enforcement, or other authority-bearing action. Stronger interpretations require a human reviewer and independently sufficient evidence appropriate to the relevant legal or administrative process.
