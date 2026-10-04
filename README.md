# Trustworthy Orchestration Integrative Review

This repository contains the public evidence and reproducibility package for an
integrative review of trustworthy orchestration across cyber, physical, social,
human-authority, and governance interfaces.

## Frozen release scope

The analytical corpus and its supporting workbook were frozen on 4 October
2026. The principal counts are:

| Stage | Count |
|---|---:|
| Database occurrences identified | 20,930 |
| Occurrences within the date window | 16,962 |
| Unique records after deduplication | 14,597 |
| Records in the author-verified title/abstract queue | 757 |
| Full-text reports sought | 529 |
| Full-text reports assessed | 524 |
| Reports excluded after full text | 488 |
| Reports not retrieved | 5 |
| Studies included through the database-search amendment | 36 |
| Eligible studies reconciled through citation searching | 84 |
| Final analytical corpus | **120** |

The publication window is 1 January 2021 through 30 April 2026. The 757-record
set is the author-verified queue after structured relevance filtering; it is not
presented as duplicate human screening of all 14,597 unique retrieval records.

## Primary artifact

The public evidence workbook is:

`outputs/TRUSTWORTHY_ORCHESTRATION_REVIEW_EVIDENCE_WORKBOOK.xlsx`

It contains 16 sequential sheets (`00_READ_ME` through
`15_DATA_DICTIONARY`) covering the dashboard, PRISMA accounting, search
strategy, raw and deduplicated records, screening criteria, title/abstract and
full-text screening, the included-study register, codebook, evidence map,
quality appraisal, reliability analysis, validation case, and data dictionary.

## Repository structure

- `outputs/`: frozen evidence workbook and release manifests.
- `data/`: machine-readable public tables exported from the workbook.
- `protocol/`: eligibility, screening, sampling, and freeze documentation.
- `references/`: the merged authoritative BibTeX bibliography.
- `validation/`: executable bounded mobility-orchestration illustration,
  frozen outputs, verification script, and checksums.
- `code/`: scripts that export the public tables and validate the frozen
  workbook and release package.

Publisher full texts are not redistributed. Bibliographic metadata, persistent
identifiers, screening decisions, evidence locations, and study-level codes are
provided so that readers can audit the review using lawful institutional or
open-access routes.

## Reproduce the checks

Python 3.12 is recommended.

```bash
python -m pip install -r requirements.txt
python code/export_public_tables.py
python code/validate_workbook.py
python code/validate_release.py
(cd validation && python verify.py && sha256sum -c SHA256SUMS.txt)
```

The checks confirm the workbook sheet order, review-flow totals, unique study
keys, equality of the 120-study included register/evidence map/quality
appraisal, reliability totals, validation outputs, and SHA-256 manifest.

## Reliability and validation boundaries

The independent primary reliability sample contains 16 studies and 336 coded
decisions. Initial exact agreement was 301/336 (89.6%) before consensus
adjudication. The bounded validation case uses 100 paired seeds, 300 steps per
policy and seed, and 60,000 step-level observations. It establishes
reproducibility within the declared computational model, not external validity,
field safety, certification, or production superiority.

## Citation

Use the metadata in `CITATION.cff`. Replace the repository-owner alias with the
final author list before creating a DOI-backed archival release.

## Licensing

See `LICENSE`. The code is released under the MIT License. Original
documentation and non-copyrighted review metadata are released under CC BY 4.0.
Third-party bibliographic metadata remain subject to their source terms.
