# Rule catalog

The rules are intentionally narrow. Their purpose is to classify evidence state while preserving source authority and the inference boundary.

| Rule | Subject | Output on anomaly | Non-conclusion |
|---|---|---|---|
| `DIO-SOURCE-001` | Two representations of one field | `CONTRADICTORY` | Does not identify cause or responsible actor |
| `DIO-REL-001` | Related-process identifier | `UNRESOLVED` | Does not declare the upstream relation invalid |
| `DIO-FIN-001` | expected → available → disbursed → spent | `REQUIRES_HUMAN_REVIEW` | Does not determine accounting cause, intent, responsibility, or legal status |
| `DIO-TIME-001` | Represented project duration and stage durations | `CONTRADICTORY` or `REQUIRES_HUMAN_REVIEW` | Does not declare a project schedule invalid or identify why a value exists |
| `DIO-OUT-001` | Expected vs measured outcome evidence | `INCOMPLETE` | Does not conclude the outcome failed |
| `DIO-EVID-001` | Required transition evidence | `INCOMPLETE` | Does not conclude the transition was unlawful |

## DIO-SOURCE-001 — source drift

Compares a named field from two source representations. Equal values are `CONSISTENT`; a missing representation is `INCOMPLETE`; unequal values are `CONTRADICTORY`.

First intended application: DREAM public API vs the corresponding public portal representation where a stable extraction method is available.

## DIO-REL-001 — relationship resolution

Checks whether an observed related-process identifier resolves inside the evidence set supplied to the evaluator. The rule deliberately says `UNRESOLVED`, not `INVALID`, because incomplete synchronization or evidence collection can produce the same observation.

## DIO-FIN-001 — provisional finance ordering

Compares values using the provisional ordering `expected ≥ available ≥ disbursed ≥ spent`. The field semantics are based on currently documented DREAM Analytics mappings. Because timing, revisions and accounting semantics can legitimately break this ordering, a difference yields `REQUIRES_HUMAN_REVIEW`. The rule does not infer cause, intent, responsibility, or legal status.

## DIO-TIME-001 — temporal plausibility

Checks represented duration values without interpreting why they exist. If supplied stage durations do not add to the represented project duration, the rule emits `CONTRADICTORY`. If the arithmetic is internally consistent but the project duration exceeds the configured review threshold (1,200 months by default), it emits `REQUIRES_HUMAN_REVIEW`.

The threshold is a Lens review policy, not a DREAM validity rule. Crossing it means only that the represented magnitude or unit should be checked against authoritative schedule data.

## DIO-OUT-001 — outcome evidence coverage

If a project is not complete, the finding is `OUTCOME_NOT_YET_MEASURABLE`. If complete but an expected outcome lacks a supplied measurement, the finding is `INCOMPLETE`.

## DIO-EVID-001 — transition evidence coverage

Checks only whether configured evidence keys are present. Presence does not prove authenticity, legal sufficiency, correctness, or authority.
