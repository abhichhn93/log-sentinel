# log-sentinel

## What it does
Log Sentinel analyzes a server log file and produces a concise Markdown report with totals, log-level counts, top error messages, and error spike detection by minute.

## Business value
- Surfaces operational hotspots fast without needing a full observability stack.
- Produces a shareable report for incident reviews and client updates.
- Highlights recurring errors and sudden spikes for rapid triage.

## How to run
Generate a sample log file and then produce a report:

```bash
python dummy_log_generator.py
python sentinel.py --input logs/dummy_server_log.txt --out report.md
```

Notes:
- `sample_logs/` contains static demo data for review.
- `logs/` is generated at runtime by `dummy_log_generator.py`.
Demo uses small sample logs for clarity; the same analysis scales to large logs.

## Demo artifacts
- `assets/report_sample.md` is generated from `sample_logs/sample_server_log.txt`.
- `assets/console_output.txt` captures the CLI output for the same run.
- `assets/architecture_notes.md` summarizes the design.

## Sample output
```text
# Log Sentinel Report

## Summary
- Total log lines: 127

## Log Level Counts
- INFO: 89
- WARNING: 26
- ERROR: 12

## Top Errors
- Database connection failed (3)
- Upstream service unavailable (2)

## Error Spikes
- 2024-04-18 10:45: 7 errors
```
