#!/usr/bin/env python3
"""Validate the frozen release manifest and all recorded SHA-256 digests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs" / "release_manifest.json"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.exists():
            errors.append(f"Missing: {item['path']}")
            continue
        if path.stat().st_size != item["bytes"]:
            errors.append(f"Size mismatch: {item['path']}")
        if digest(path) != item["sha256"]:
            errors.append(f"SHA-256 mismatch: {item['path']}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "checked_files": len(manifest["files"])}
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
