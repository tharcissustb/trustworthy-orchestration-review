#!/usr/bin/env python3
"""Build a deterministic SHA-256 manifest for the public release files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "outputs/TRUSTWORTHY_ORCHESTRATION_REVIEW_EVIDENCE_WORKBOOK.xlsx",
    "data/title_abstract_screening.csv",
    "data/full_text_screening.csv",
    "data/included_studies.csv",
    "data/evidence_map.csv",
    "data/quality_appraisal.csv",
    "data/p1_p8_reliability_adjudication.xlsx",
    "references/references.bib",
    "validation/config.json",
    "validation/simulate.py",
    "validation/verify.py",
    "validation/outputs/per_seed_results.csv",
    "validation/outputs/per_step_trace.csv",
    "validation/outputs/seeds.csv",
    "validation/outputs/summary.csv",
    "validation/outputs/summary.json",
]


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> None:
    entries = [
        {"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": digest(ROOT / name)}
        for name in FILES
    ]
    result = {"status": "FROZEN", "version": "1.1.0", "corpus_size": 120, "files": entries}
    output = ROOT / "outputs" / "release_manifest.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    checksum = ROOT / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{item['sha256']}  {item['path']}\n" for item in entries), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
