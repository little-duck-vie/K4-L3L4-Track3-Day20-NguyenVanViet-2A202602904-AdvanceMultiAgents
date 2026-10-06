---
name: log-file-error-triage-checklist
description: Use whenever parsing service log files to extract error-level entries with normalized timestamps, service names, exceptions, repeat counts, and sorted output.
---
- Read the entire log file, preserving multi-line entries and tracebacks.
- Filter entries by log level ERROR or CRITICAL (case insensitive).
- Normalize timestamps to UTC in ISO 8601 format with 'Z' suffix; convert offset-aware timestamps accordingly.
- Normalize service names to lower-case with hyphens replaced by underscores.
- Extract the first line message after the service name.
- Extract the last line of the traceback as the exception field; null if no traceback.
- Detect and sum any following lines indicating repeated messages (e.g., "-- last message repeated N times --") to compute repeat_count.
- Aggregate counts of errors by normalized service name.
- Sort the final error list by service name ascending, then by timestamp ascending.
- Output a JSON object with schema_version=2 and generated_by="log-triage" including errors array and counts_by_service.
- Verify all required fields and sorting before claiming completion.
