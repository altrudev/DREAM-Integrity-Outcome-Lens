# DREAM Integrity & Outcome Lens

Independent civic-tech tooling for deterministic evidence lineage, consistency checking, and outcome assurance over public Ukrainian reconstruction and public-investment data.

**Status: v0.1 integrity core — research prototype.**

> This project is not an official DREAM component. It does not infer corruption, fraud, criminality, ownership, attribution, or legal liability from anomalies. It produces bounded, evidence-backed consistency findings for human review.

## Why this exists

DREAM exposes public investment and reconstruction data, while adjacent Ukrainian systems cover procurement, financing, implementation, monitoring, and risk management. The useful gap is not another opaque risk score. It is a reproducible way to answer:

**Does the public evidence preserve the same project, authority, financing, state transition, implementation record, and measurable outcome across the chain?**

The Lens therefore models observations and relationships without absorbing the authority of the systems it reads.

## v0.1 architecture

```text
public source adapters (read-only)
        │
        ▼
immutable snapshot envelope
        │  canonical JSON + SHA-256
        ▼
normalized audit record
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

Current source adapter:

- DREAM public API: `https://public-api.dream.gov.ua`
- documented project index: `/marketplace/public/dream/ideas`
- documented project detail: `/marketplace/public/dream/ideas/{id}`

The archived public API specification remains useful as an interface contract, but the Lens treats live upstream behavior as observed evidence rather than assuming archival documentation is current.

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

## Initial rules

| Rule | Purpose |
|---|---|
| `DIO-SOURCE-001` | Compare two representations of the same field |
| `DIO-REL-001` | Check whether an observed relationship resolves in the supplied evidence set |
| `DIO-FIN-001` | Flag finance-ordering differences for human review |
| `DIO-OUT-001` | Check expected outcome measurement coverage |
| `DIO-EVID-001` | Check required transition-evidence presence |

These rules deliberately detect evidence states, not wrongdoing. See [`docs/rule-catalog.md`](docs/rule-catalog.md).

## Quick start

Python 3.11+ is sufficient; v0.1 has no runtime third-party dependencies.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Evaluate the supplied normalized fixture:

```bash
dream-lens evaluate tests/fixtures/sample_record.json
```

Capture one public DREAM project snapshot:

```bash
dream-lens snapshot-project <dream-project-id> --out snapshots/project.json
```

Hash any JSON evidence deterministically:

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
- Current financing-field mapping reference: https://github.com/open-contracting/bi.dream.gov.ua/issues/403

## Roadmap

1. **v0.1 — integrity core:** deterministic bundles, bounded rule taxonomy, DREAM snapshot adapter.
2. **v0.2 — DREAM normalization:** map current public project fields and related-process edges into a stable internal record.
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
