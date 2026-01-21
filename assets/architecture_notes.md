# Architecture Notes

## Overview
Log Sentinel is a small CLI pipeline with clear stages: input parsing, aggregation, spike detection, and report rendering.

## Data flow
1) Read log lines from a file.
2) Parse timestamp, level, service, and message with a regex.
3) Aggregate counts by level and error message.
4) Detect error spikes per minute (>5 errors).
5) Emit a Markdown report suitable for sharing.

## Design choices
- Pure standard library for portability.
- Deterministic outputs for sample data to support portfolio demos.
- Simple, auditable logic rather than opaque heuristics.
