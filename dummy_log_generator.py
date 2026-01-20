from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "dummy_server_log.txt"
LEVELS = ["INFO", "WARNING", "ERROR"]
SERVICES = ["auth", "billing", "catalog", "search", "gateway"]
INFO_MESSAGES = [
    "User login successful",
    "Cache warmup completed",
    "Background job finished",
    "Health check passed",
    "Session refreshed",
]
WARNING_MESSAGES = [
    "Retrying request to upstream",
    "Slow response detected",
    "Disk usage above threshold",
    "Rate limit nearing cap",
    "Config value deprecated",
]
ERROR_MESSAGES = [
    "Database connection failed",
    "Timeout while calling payment service",
    "Null reference in handler",
    "Failed to write to cache",
    "Authentication token invalid",
    "Upstream service unavailable",
    "Permission denied while reading file",
]


def build_log_lines(start_time: datetime, count: int) -> list[str]:
    lines: list[str] = []
    current_time = start_time
    for _ in range(count):
        level = random.choices(LEVELS, weights=[70, 20, 10], k=1)[0]
        service = random.choice(SERVICES)
        if level == "INFO":
            message = random.choice(INFO_MESSAGES)
        elif level == "WARNING":
            message = random.choice(WARNING_MESSAGES)
        else:
            message = random.choice(ERROR_MESSAGES)
        lines.append(
            f"{current_time:%Y-%m-%d %H:%M:%S} {level} {service}: {message}"
        )
        current_time += timedelta(seconds=random.randint(5, 25))
    return lines


def inject_error_spike(base_time: datetime, count: int) -> list[str]:
    lines: list[str] = []
    spike_time = base_time.replace(second=0)
    for _ in range(count):
        service = random.choice(SERVICES)
        message = random.choice(ERROR_MESSAGES)
        lines.append(
            f"{spike_time:%Y-%m-%d %H:%M:%S} ERROR {service}: {message}"
        )
        spike_time += timedelta(seconds=random.randint(1, 8))
    return lines


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    random.seed(42)
    start = datetime.now().replace(microsecond=0) - timedelta(hours=2)

    lines = build_log_lines(start, 120)

    spike_time = start + timedelta(minutes=45)
    lines.extend(inject_error_spike(spike_time, 7))

    lines.sort()

    LOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
