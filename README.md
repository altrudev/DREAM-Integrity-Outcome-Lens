# DREAM Integrity & Outcome Lens

Independent civic-tech tooling for deterministic evidence lineage, consistency checking, and outcome assurance over public Ukrainian reconstruction and public-investment data.

**Status: v0.2 normalization + real-data validation — research prototype.**

> This project is not an official DREAM component. It produces bounded, evidence-backed consistency findings for human review. An observed anomaly does not by itself establish cause, intent, responsibility, attribution, ownership, or a legal conclusion.

## Why this exists

DREAM exposes public investment and reconstruction data, while adjacent Ukrainian systems cover procurement, financing, implementation, monitoring, and risk management. The useful gap is a reproducible way to answer:

**Does the public evidence preserve the same project, authority, financing, state transition, implementation record, and measurable outcome across the chain?**

The Lens models observations and relationships without absorbing the authority of the systems it reads.

## Architecture

```text
public source adapters / observations (read-only)
        │
        ▼
immutable snapshot / captured observation
        │  canonical JSON + SHA-256
        ▼
v0.2 normalized project record
        │
        ▼
deterministic rule engine
        │
        ▼
evidence bundle
        │
        ▼
human review
```

Current source boundary:

- DREAM public API: `https://public-api.dream.gov.ua`
- documented project index: `/marketplace/public/dream/ideas`
- documented project detail: `/marketplace/public/dream/ideas/{id}`
- public DREAM project pages used for bounded real-data observations

The archived public API specification remains useful as an interface contract, while current DREAM Analytics issues document newer `publicprojects`, `cdu_response`, related-process, active-approach, and financing semantics. The Lens treats live upstream behavior as observed evidence rather than assuming archival documentation is current.

## v0.2 normalization

`dream_lens.normalization.normalize_public_project()` maps documented DREAM project structures into a stable internal record while preserving source identifiers. For multiple active technical approaches, the normalizer follows the currently documented DREAM Analytics selection method: choose the active approach with the largest `budget/valueBreakdown` total. A deterministic ID tie-break is used only inside the Lens.

Normalized values remain Lens observations; they are not represented as authoritative DREAM fields.

## Finding taxonomy

The engine emits only:

- `CONSISTENT`
- `INCOMPLETE`
- `STALE`
- `CONTRADICTORY`
- `UNRESOLVED`
- `OUTCOME_NOT_YET_MEASURABLE`
- `REQUIRES_HUMAN_REVIEW`

See [`docs/trust-model.md`](docs/trust-model.md) for the authority and inference boundary.

## Rules

| Rule | Purpose |
|---|---|
| `DIO-SOURCE-001` | Compare two representations of the same field |
| `DIO-REL-001` | Check whether an observed relationship resolves in the supplied evidence set |
| `DIO-FIN-001` | Flag finance-ordering differences for human review |
| `DIO-TIME-001` | Check duration arithmetic and route unusually large represented durations to review |
| `DIO-OUT-001` | Check expected outcome measurement coverage |
| `DIO-EVID-001` | Check required transition-evidence presence |

These rules classify evidence states. They do not determine why an anomaly exists or who is responsible for it. See [`docs/rule-catalog.md`](docs/rule-catalog.md).

## First real-data validation

Two public DREAM project observations are retained as regression fixtures:

- `DREAM-UA-040825-30FC5B9E` — HEAL Ukraine. The public project page represented project duration as **48,576 months**, with 24,264 months for full-feasibility development and 24,312 months for implementation. The arithmetic is internally consistent, but the magnitude crosses the Lens review threshold and yields `REQUIRES_HUMAN_REVIEW`.
- `DREAM-UA-070825-07BFF93A` — Development of the Trans-European Transport Network. The public project page represented 72 months total, with 24 + 48 months, and yields `CONSISTENT` under the same rule.

The comparison demonstrates that `DIO-TIME-001` does not flag all long infrastructure projects; it routes a bounded magnitude/unit question for review. See [`docs/evidence-report-2026-08-24.md`](docs/evidence-report-2026-08-24.md).

## Quick start

Python 3.11+ is sufficient; v0.2 has no runtime third-party dependencies.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Evaluate a normalized fixture:

```bash
dream-lens evaluate tests/fixtures/sample_record.json
```

Capture one public DREAM API project snapshot:

```bash
dream-lens snapshot-project <dream-project-id> --out snapshots/project.json
```

Hash JSON evidence deterministically:

```bash
dream-lens hash snapshots/project.json
```

## Local verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/ddc_audit.py
```

## Source references

- DREAM open-data/API announcement: https://dream.gov.ua/news/article-6
- Archived DREAM public API specification: https://github.com/open-contracting/dream-api-docs
- DREAM Analytics repository: https://github.com/open-contracting/bi.dream.gov.ua
- Public-project details methodology: https://github.com/open-contracting/bi.dream.gov.ua/issues/379
- Financing-field mapping: https://github.com/open-contracting/bi.dream.gov.ua/issues/403

## Roadmap

1. **v0.1 — integrity core:** deterministic bundles, bounded rule taxonomy, DREAM snapshot adapter. ✅
2. **v0.2 — DREAM normalization + real-data validation:** stable project normalization, live public observations, temporal evidence rule. ✅
3. **v0.3 — portal/API drift:** compare stable public representations without screen-scraping assumptions.
4. **v0.4 — Prozorro adapter:** connect procurement evidence while preserving Prozorro authority.
5. **v0.5 — financing and transition lineage:** model revision-aware decision → funding → disbursement → implementation chains.
6. **v0.6 — outcome lens:** connect completion evidence to declared measurable outcomes.
7. **v1.0 — reproducible public assurance reports:** Ukrainian/English evidence reports with human-review workflow.

## Language

Repository-authored user-facing content is Ukrainian or English. Russian-language repository-authored content is out of scope.

## Maintainer

Altru.dev — https://altru.dev — GitHub: `@altrudev`

## License

No open-source license has been declared yet. Licensing remains an explicit repository-owner decision.
