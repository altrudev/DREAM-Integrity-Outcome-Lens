from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapters.dream import DreamPublicApiClient
from .engine import evaluate
from .evidence import sha256_json
from .normalization import normalize_public_project


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")


def _emit_json(value: Any, out: Path | None = None) -> None:
    if out:
        _write_json(out, value)
    else:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dream-lens")
    sub = parser.add_subparsers(dest="command", required=True)

    hash_parser = sub.add_parser("hash", help="print canonical SHA-256 for a JSON document")
    hash_parser.add_argument("file", type=Path)

    normalize_parser = sub.add_parser("normalize-project", help="normalize a captured DREAM public-project JSON document")
    normalize_parser.add_argument("file", type=Path)
    normalize_parser.add_argument("--out", type=Path)

    eval_parser = sub.add_parser("evaluate", help="evaluate a normalized audit record")
    eval_parser.add_argument("file", type=Path)
    eval_parser.add_argument("--out", type=Path)

    snap_parser = sub.add_parser("snapshot-project", help="capture one DREAM public project snapshot")
    snap_parser.add_argument("project_id")
    snap_parser.add_argument("--out", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "hash":
        print(sha256_json(_load_json(args.file)))
        return 0
    if args.command == "normalize-project":
        _emit_json(normalize_public_project(_load_json(args.file)), args.out)
        return 0
    if args.command == "evaluate":
        _emit_json(evaluate(_load_json(args.file)), args.out)
        return 0
    if args.command == "snapshot-project":
        snapshot = DreamPublicApiClient().snapshot_project(args.project_id)
        _write_json(args.out, snapshot)
        print(snapshot["payload_sha256"])
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
