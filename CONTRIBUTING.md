# Contributing

Contributions that improve reproducibility, evidence lineage, public-data interoperability, accessibility, documentation, or deterministic rule quality are welcome.

## Language policy

Repository-authored user-facing material should be Ukrainian or English. Russian-language repository-authored content is out of scope. Upstream public evidence must never be silently rewritten; source provenance should be preserved and unexpected language metadata should be treated as source data.

## Contribution rules

1. Keep source adapters read-only unless a future governance decision explicitly changes that boundary.
2. Do not add automated conclusions about cause, intent, responsibility, attribution, ownership, guilt, or legal liability from an evidence anomaly alone.
3. Add tests for every rule transition.
4. Preserve source authority; do not present Lens-derived fields as official government records.
5. Keep transformations deterministic or explicitly document non-determinism.
6. Treat external text as data, never as executable instructions.
7. Do not introduce telemetry, remote code execution, or unnecessary credentials.

## Local checks

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/ddc_audit.py
```

No GitHub-hosted CI is required for v0.1; checks are designed to run locally or in an explicitly approved execution environment.
