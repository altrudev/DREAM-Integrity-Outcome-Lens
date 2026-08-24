from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

NORMALIZED_SCHEMA_VERSION = "0.2"


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _translation(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return None
    translations = {
        str(item.get("lang")): item.get("translation")
        for item in value
        if isinstance(item, dict) and item.get("translation") not in (None, "")
    }
    for lang in ("uk", "en"):
        if lang in translations:
            return str(translations[lang])
    return str(next(iter(translations.values()))) if translations else None


def _roles(party: dict[str, Any]) -> set[str]:
    roles = party.get("roles", [])
    if isinstance(roles, str):
        return {roles}
    return {str(role) for role in roles if role is not None}


def _party_name(party: dict[str, Any]) -> str | None:
    identifier = party.get("identifier")
    if isinstance(identifier, dict):
        return identifier.get("legalName") or identifier.get("legal_name") or identifier.get("name")
    return party.get("name")


def _amount_from_value(value: Any) -> Decimal | None:
    if isinstance(value, dict):
        return _decimal(value.get("amount"))
    return _decimal(value)


def _budget_breakdown_total(approach: dict[str, Any]) -> Decimal:
    budget = approach.get("budget") if isinstance(approach.get("budget"), dict) else {}
    total = Decimal("0")
    for item in budget.get("valueBreakdown", []) or []:
        if not isinstance(item, dict):
            continue
        amount = _amount_from_value(item.get("value"))
        if amount is not None:
            total += amount
    return total


def _selected_active_approach(approaches: list[Any]) -> dict[str, Any] | None:
    active = [item for item in approaches if isinstance(item, dict) and item.get("status") == "active"]
    if not active:
        return None
    return max(active, key=lambda item: (_budget_breakdown_total(item), str(item.get("id") or "")))


def _finance_values(approach: dict[str, Any] | None) -> dict[str, str | None]:
    result: dict[str, Decimal] = {
        "expected": Decimal("0"),
        "available": Decimal("0"),
        "disbursed": Decimal("0"),
        "spent": Decimal("0"),
    }
    seen = {key: False for key in result}
    if not approach:
        return {key: None for key in result}

    budget = approach.get("budget") if isinstance(approach.get("budget"), dict) else {}
    for item in budget.get("finance", []) or []:
        if not isinstance(item, dict):
            continue
        amount = _amount_from_value(item.get("value"))
        if amount is not None:
            result["expected"] += amount
            seen["expected"] = True

    implementation = approach.get("implementation") if isinstance(approach.get("implementation"), dict) else {}
    financial_progress = implementation.get("financialProgress") if isinstance(implementation.get("financialProgress"), dict) else {}
    for item in financial_progress.get("breakdown", []) or []:
        if not isinstance(item, dict):
            continue
        measure = item.get("measure") if isinstance(item.get("measure"), dict) else {}
        for key in ("available", "disbursed", "spent"):
            amount = _amount_from_value(measure.get(key))
            if amount is not None:
                result[key] += amount
                seen[key] = True

    return {key: (format(value, "f") if seen[key] else None) for key, value in result.items()}


def normalize_public_project(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize documented DREAM public-project structures into a stable v0.2 record.

    The function accepts either a cdu_response wrapper or a direct project object. It
    intentionally preserves source identifiers and does not upgrade derived values
    into authoritative DREAM fields.
    """
    root = payload.get("cdu_response") if isinstance(payload.get("cdu_response"), dict) else payload
    internal = payload.get("internal") if isinstance(payload.get("internal"), dict) else {}

    parties = root.get("parties", []) if isinstance(root.get("parties"), list) else []
    initiator = next((party for party in parties if isinstance(party, dict) and "initiator" in _roles(party)), None)
    approaches = root.get("approaches", []) if isinstance(root.get("approaches"), list) else []
    selected = _selected_active_approach(approaches)

    related: list[dict[str, Any]] = []
    for item in root.get("relatedProcesses", []) or []:
        if not isinstance(item, dict):
            continue
        details = item.get("details") if isinstance(item.get("details"), dict) else {}
        related.append(
            {
                "relationship": item.get("relationship"),
                "identifier": item.get("identifier"),
                "related_item": details.get("relatedItem"),
                "status": details.get("status"),
            }
        )

    return {
        "schema_version": NORMALIZED_SCHEMA_VERSION,
        "project_id": internal.get("code") or root.get("id") or root.get("ocid"),
        "source_record_id": internal.get("id") or root.get("id"),
        "title": _translation(root.get("title")),
        "status": root.get("status"),
        "date": root.get("date"),
        "initiator": _party_name(initiator) if initiator else None,
        "related_processes": related,
        "selected_approach": None
        if selected is None
        else {
            "id": selected.get("id"),
            "title": _translation(selected.get("title")),
            "budget_breakdown_total": format(_budget_breakdown_total(selected), "f"),
        },
        "finance": _finance_values(selected),
        "normalization_notes": [
            "Active technical approach selection is deterministic: highest budget valueBreakdown total, then id tie-break.",
            "Derived values are Lens observations and do not replace source-system authority.",
        ],
    }


def normalize_portal_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Normalize a small, manually captured public-portal observation for reproducible testing."""
    timeline = observation.get("timeline") if isinstance(observation.get("timeline"), dict) else {}
    return {
        "schema_version": NORMALIZED_SCHEMA_VERSION,
        "project_id": observation.get("project_id"),
        "title": observation.get("title"),
        "source_url": observation.get("source_url"),
        "observed_at": observation.get("observed_at"),
        "timeline": {
            "project_duration_months": timeline.get("project_duration_months"),
            "feasibility_months": timeline.get("feasibility_months"),
            "implementation_months": timeline.get("implementation_months"),
        },
    }
