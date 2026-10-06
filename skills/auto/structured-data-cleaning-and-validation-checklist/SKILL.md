---
name: structured-data-cleaning-and-validation-checklist
description: Use whenever processing tabular data files requiring normalization, deduplication, date parsing, and output in canonical formats with metadata.
---
- Inspect input CSV or structured data for:
  - Multiple date formats; implement robust parsing converting all dates to a consistent timezone and naive datetime.
  - Region or categorical fields; normalize spelling, casing, and strip whitespace to canonical forms.
  - Missing or sentinel values; convert to None or appropriate null representation.
- Remove exact duplicate rows before analysis.
- Compute required aggregates or filters only on cleaned, deduplicated data.
- Write output CSV with specified header, normalized fields, and required formatting (e.g., timestamps in ISO 8601 UTC with 'Z', money as integer cents).
- Produce a metadata JSON object including:
  - Source input filename.
  - Total input rows count (including duplicates).
  - Number of distinct rows used in analysis.
- Validate output files and metadata for completeness and correctness before completion.
