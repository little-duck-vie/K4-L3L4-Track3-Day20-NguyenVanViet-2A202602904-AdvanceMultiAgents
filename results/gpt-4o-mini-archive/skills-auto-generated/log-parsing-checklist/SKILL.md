---
name: log-parsing-checklist
description: Use whenever you are parsing log files to ensure accurate extraction and formatting of log data.
---
1. Filter log entries to include only relevant levels (e.g., ERROR, CRITICAL).
2. Convert timestamps to the required UTC format (YYYY-MM-DDTHH:MM:SSZ).
3. Extract necessary fields from each log entry, including service name, log level, message, exception details, and repeat counts.
4. Ensure service names are formatted in lower-case with '-' replaced by '_'.
5. Sort the output by service name and timestamp in ascending order.
6. Validate the final output structure against the specified schema before finalizing the log parsing task.
