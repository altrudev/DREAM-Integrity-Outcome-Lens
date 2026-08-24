from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for evidence hashing."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def snapshot_envelope(*, source_url: str, observed_at: str, payload: Any) -> dict[str, Any]:
    """Create a provenance envelope without mutating the upstream payload."""
    return {
        "snapshot_version": "1",
        "source_url": source_url,
        "observed_at": observed_at,
        "payload_sha256": sha256_json(payload),
        "payload": payload,
    }
