# DREAM Integrity & Outcome Lens — public-data validation report

Date: 2026-08-24

Status: research observation for reproducibility and source review. This report does not establish cause, intent, responsibility, attribution, ownership, or a legal conclusion.

## Method

The v0.2 Lens compared two public DREAM project-page observations using the same deterministic temporal rule (`DIO-TIME-001`). The rule first checks arithmetic consistency where stage durations are supplied. It then routes unusually large represented durations to human review using a configurable Lens threshold of 1,200 months (100 years).

The threshold is not a DREAM validity rule. It is a review trigger intended to catch possible unit, mapping, migration, or data-entry questions without assuming why the represented value exists.

## Observation A — HEAL Ukraine

Project: `DREAM-UA-040825-30FC5B9E`

Public source: https://dream.gov.ua/ua/pip/DREAM-UA-040825-30FC5B9E?fromUri=%2Fspp-pipeline

Observed public representation:

- project duration: 48,576 months
- deadline for developing the full feasibility study: 24,264 months
- implementation period: 24,312 months
- arithmetic: 24,264 + 24,312 = 48,576

Lens finding:

- rule: `DIO-TIME-001`
- state: `REQUIRES_HUMAN_REVIEW`
- reason: the represented duration is internally arithmetic-consistent but substantially above the configured review threshold
- next evidence: verify the authoritative unit, source value, and project schedule
- deterministic bundle SHA-256: `3e3319b4b02cb1888d045b8b86e77d09559ad95f5f55dc7a4bb71b96591d5f7a`

The Lens does not infer why the values are represented this way.

### Externally confirmed resolution — 2026-08-28

In a written response, the DREAM team confirmed that the atypical HEAL Ukraine duration resulted from incorrect user data entry while completing the public investment project card. According to DREAM, an exact calendar year was entered where the form expected the number of years spent on a stage — for example, `2026` instead of `1`.

DREAM stated that this explains the unusually large represented duration and that the information was passed to the responsible team for follow-up with the user.

This confirmation closes the causal question for this observed case without changing the original deterministic finding. The original Lens bundle remains an immutable record of what was observable at the time of capture:

1. the public representation was internally arithmetic-consistent;
2. its magnitude crossed the bounded review threshold;
3. the Lens emitted `REQUIRES_HUMAN_REVIEW` rather than assigning a cause;
4. the source owner later supplied independent explanatory evidence identifying the data-entry cause;
5. remediation was handed to the responsible DREAM team.

The resolution therefore demonstrates the intended inference boundary in practice: **detection did not become attribution**. Source-owner confirmation is recorded as a later evidence event and does not retroactively rewrite the original observation or evidence-bundle hash.

## Observation B — Trans-European Transport Network

Project: `DREAM-UA-070825-07BFF93A`

Public source: https://dream.gov.ua/pip/DREAM-UA-070825-07BFF93A?fromUri=%2Fspp-pipeline

Observed public representation:

- project duration: 72 months
- deadline for developing the full feasibility study: 24 months
- implementation period: 48 months
- arithmetic: 24 + 48 = 72

Lens finding:

- rule: `DIO-TIME-001`
- state: `CONSISTENT`
- reason: represented duration is arithmetically consistent and within the configured review threshold
- deterministic bundle SHA-256: `d4870048e3e34ea2055d53573692c9512fb5e4d567dc67bd7ea626413089f17f`

## Why this comparison matters

The control project demonstrates that the rule is not simply marking infrastructure timelines as unusual. The same rule accepts a 72-month project and routes the 48,576-month representation for source review.

The useful question is therefore narrow and reproducible:

> Is the represented duration and unit intentional, or should the public record be corrected or remapped?

The subsequent DREAM confirmation resolved that question for the HEAL Ukraine observation as a user data-entry error while preserving the validity of the original bounded finding.

## Reproducibility

Regression fixtures:

- `tests/fixtures/live/heal-040825-30fc5b9e.json`
- `tests/fixtures/live/ten-t-070825-07bff93a.json`

Verification on the audited v0.2 branch:

- 20/20 unit tests passed
- Python compilation passed
- DDC audit passed all 10 gates
- real-data provenance checks passed
- real-data regression expectations passed

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/ddc_audit.py
```

## Authority boundary

DREAM remains authoritative for DREAM records. The Lens preserves public observations and deterministic rule output only. A `REQUIRES_HUMAN_REVIEW` state is a request to verify evidence, not a determination about the underlying project or any actor. Later source-owner confirmation can resolve the factual cause of a case, but it is recorded as additional evidence rather than as a retroactive alteration of the original bundle.
