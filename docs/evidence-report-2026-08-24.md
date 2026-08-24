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

The Lens does not infer why the values are represented this way.

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

## Why this comparison matters

The control project demonstrates that the rule is not simply marking infrastructure timelines as unusual. The same rule accepts a 72-month project and routes the 48,576-month representation for source review.

The useful question is therefore narrow and reproducible:

> Is the represented duration and unit intentional, or should the public record be corrected or remapped?

## Reproducibility

Regression fixtures:

- `tests/fixtures/live/heal-040825-30fc5b9e.json`
- `tests/fixtures/live/ten-t-070825-07bff93a.json`

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/ddc_audit.py
```

## Authority boundary

DREAM remains authoritative for DREAM records. The Lens preserves public observations and deterministic rule output only. A `REQUIRES_HUMAN_REVIEW` state is a request to verify evidence, not a determination about the underlying project or any actor.
