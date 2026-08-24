from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from ..evidence import snapshot_envelope

DEFAULT_BASE_URL = "https://public-api.dream.gov.ua"
ALLOWED_HOSTS = frozenset({"public-api.dream.gov.ua"})
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


class DreamAdapterError(RuntimeError):
    pass


class DreamPublicApiClient:
    """Minimal read-only client for the documented DREAM public API."""

    def __init__(self, *, base_url: str = DEFAULT_BASE_URL, timeout: float = 20.0) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.path not in ("", "/"):
            raise ValueError("DREAM base URL must be the allow-listed HTTPS production host")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, path: str, query: dict[str, str] | None = None) -> tuple[str, Any]:
        if not path.startswith("/"):
            raise ValueError("path must be absolute within the allow-listed DREAM host")
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        request = Request(url, method="GET", headers={"Accept": "application/json", "User-Agent": "DREAM-Integrity-Outcome-Lens/0.1 (+https://github.com/altrudev/DREAM-Integrity-Outcome-Lens)"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    raise DreamAdapterError(f"unexpected content type: {content_type}")
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise DreamAdapterError("response exceeds configured maximum size")
        except DreamAdapterError:
            raise
        except Exception as exc:
            raise DreamAdapterError(f"DREAM request failed: {exc}") from exc
        try:
            return url, json.loads(body)
        except json.JSONDecodeError as exc:
            raise DreamAdapterError("DREAM returned invalid JSON") from exc

    def list_project_ids(self, *, from_: str | None = None, order: str = "asc") -> tuple[str, Any]:
        if order not in {"asc", "desc"}:
            raise ValueError("order must be 'asc' or 'desc'")
        query = {"order": order}
        if from_ is not None:
            query["from"] = from_
        return self._get_json("/marketplace/public/dream/ideas", query)

    def get_project(self, project_id: str) -> tuple[str, Any]:
        if not project_id or "/" in project_id:
            raise ValueError("invalid DREAM project id")
        return self._get_json(f"/marketplace/public/dream/ideas/{quote(project_id, safe='')}")

    def snapshot_project(self, project_id: str) -> dict[str, Any]:
        url, payload = self.get_project(project_id)
        observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return snapshot_envelope(source_url=url, observed_at=observed_at, payload=payload)
