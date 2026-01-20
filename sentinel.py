from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import Iterable


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(?P<level>INFO|WARNING|ERROR) "
    r"(?P<service>[\w-]+): (?P<message>.+)$"
)


class LogParseError(Exception):
    pass


def parse_log_lines(lines: Iterable[str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.match(line)
        if not match:
            raise LogParseError(f"Malformed log line at {line_number}: {line}")
        entries.append(match.groupdict())
    return entries


def compute_error_spikes(entries: list[dict[str, str]]) -> dict[str, int]:
    error_by_minute: dict[str, int] = defaultdict(int)
    for entry in entries:
        if entry["level"] != "ERROR":
            continue
        timestamp = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
        minute_key = timestamp.strftime("%Y-%m-%d %H:%M")
        error_by_minute[minute_key] += 1

    return {
        minute: count
        for minute, count in sorted(error_by_minute.items())
        if count > 5
    }


def format_report(
    total_lines: int,
    level_counts: Counter[str],
    top_errors: list[tuple[str, int]],
    error_spikes: dict[str, int],
    generated_at: str,
    input_path: str,
    command: str,
) -> str:
    lines: list[str] = ["# Log Sentinel Report", ""]

    lines.extend([
        "## Summary",
        f"- Generated at: {generated_at}",
        f"- Input file: {input_path}",
        f"- Command: {command}",
        f"- Total log lines: {total_lines}",
        "",
        "## Log Level Counts",
    ])
    for level in ("INFO", "WARNING", "ERROR"):
        lines.append(f"- {level}: {level_counts.get(level, 0)}")

    lines.extend(["", "## Top Errors"])
    if top_errors:
        for message, count in top_errors:
            lines.append(f"- {message} ({count})")
    else:
        lines.append("- No ERROR entries found")

    lines.extend(["", "## Error Spikes"])
    if error_spikes:
        for minute, count in error_spikes.items():
            lines.append(f"- {minute}: {count} errors")
    else:
        lines.append("- No error spikes detected")

    lines.append("")
    return "\n".join(lines)


def load_log_file(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Input path is not a file: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze server logs and generate a report.")
    parser.add_argument("--input", required=True, help="Path to the log file")
    parser.add_argument("--out", required=True, help="Path to the output report")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.out)

    try:
        raw_lines = load_log_file(input_path)
        entries = parse_log_lines(raw_lines)
    except (FileNotFoundError, LogParseError) as exc:
        print(f"Error: {exc}")
        return 1

    total_lines = len(entries)
    level_counts = Counter(entry["level"] for entry in entries)
    error_messages = [entry["message"] for entry in entries if entry["level"] == "ERROR"]
    top_errors = Counter(error_messages).most_common(5)
    error_spikes = compute_error_spikes(entries)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = " ".join(sys.argv)
    report = format_report(
        total_lines,
        level_counts,
        top_errors,
        error_spikes,
        generated_at,
        str(input_path),
        command,
    )
    output_path.write_text(report, encoding="utf-8")

    print(f"Report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
