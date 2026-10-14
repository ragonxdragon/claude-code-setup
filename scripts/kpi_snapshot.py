#!/usr/bin/env python3
"""Append one KPI trend row computed from recent Claude Code session
transcripts, and print a summary.

KPIs:
  - session count and assistant message count
  - model mix: share of assistant messages per model family
  - tool errors per 1,000 assistant messages
  - session length p90 in hours (first to last timestamp per transcript)

A model-mix gate checks that one family stays under a ceiling share, for
example that the most expensive tier stays under 40 percent of messages. Set
it with --gate-family and --gate-max.

Transcripts are read from <root>/projects/*/*.jsonl, where <root> is
CLAUDE_HOME or the parent of this scripts/ directory. Run it from the
installed ~/.claude (or set CLAUDE_HOME=~/.claude) for real data. Output rows
go to <root>/artifacts/kpi/kpi-trend.csv.

Streams lines with regular expressions instead of parsing each line as JSON,
so a large transcript tree scans in seconds. Standard library only.

Usage:
    python scripts/kpi_snapshot.py [--days 7] [--gate-family opus] [--gate-max 40]
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from claude_home import CLAUDE_DIR, utf8_stdout

PROJECTS = CLAUDE_DIR / "projects"
OUT_DIR = CLAUDE_DIR / "artifacts" / "kpi"

MODEL_RE = re.compile(rb'"model"\s*:\s*"claude-([a-z]+)[a-z0-9.\[\]-]*"')
ERROR_RE = re.compile(rb'"is_error"\s*:\s*true')
TS_RE = re.compile(rb'"timestamp"\s*:\s*"(20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+)')


def scan(files: list[Path]) -> tuple[dict[str, int], int, list[float]]:
    families: dict[str, int] = {}
    errors = 0
    durations_h: list[float] = []
    for f in files:
        first_ts = last_ts = None
        try:
            with open(f, "rb") as fh:
                for line in fh:
                    for m in MODEL_RE.finditer(line):
                        family = m.group(1).decode(errors="replace")
                        families[family] = families.get(family, 0) + 1
                    errors += len(ERROR_RE.findall(line))
                    t = TS_RE.search(line)
                    if t:
                        last_ts = t.group(1).decode()
                        if first_ts is None:
                            first_ts = last_ts
        except OSError:
            continue
        if first_ts and last_ts and first_ts != last_ts:
            try:
                span = datetime.fromisoformat(last_ts) - datetime.fromisoformat(first_ts)
                durations_h.append(span.total_seconds() / 3600)
            except ValueError:
                pass
    return families, errors, durations_h


def recent_transcripts(days: int) -> list[Path]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    files = []
    for f in PROJECTS.glob("*/*.jsonl"):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime, timezone.utc) >= cutoff:
                files.append(f)
        except OSError:
            continue
    return files


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Append a KPI trend row from recent transcripts.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--gate-family", default="opus", help="model family the gate limits")
    parser.add_argument("--gate-max", type=float, default=40.0, help="maximum share in percent")
    args = parser.parse_args()

    files = recent_transcripts(args.days)
    families, errors, durations_h = scan(files)
    msgs = sum(families.values())
    pct = {k: (100.0 * v / msgs if msgs else 0.0) for k, v in families.items()}
    err_per_1k = 1000.0 * errors / msgs if msgs else 0.0
    durations_h.sort()
    p90 = durations_h[int(0.9 * (len(durations_h) - 1))] if durations_h else 0.0
    mix = ";".join(f"{k}={pct[k]:.1f}" for k in sorted(pct))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    trend = OUT_DIR / "kpi-trend.csv"
    new = not trend.exists()
    with open(trend, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if new:
            writer.writerow(
                ["date", "days", "sessions", "assistant_msgs", "model_mix_pct", "errors_per_1k", "session_p90_h"]
            )
        writer.writerow(
            [
                datetime.now(timezone.utc).date().isoformat(),
                args.days,
                len(files),
                msgs,
                mix,
                f"{err_per_1k:.1f}",
                f"{p90:.1f}",
            ]
        )

    print(f"KPI last {args.days}d: {len(files)} sessions, {msgs} assistant msgs")
    print("  model mix: " + (" | ".join(f"{k} {pct[k]:.1f}%" for k in sorted(pct)) or "no data"))
    print(f"  errors/1k msgs: {err_per_1k:.1f} | session p90: {p90:.1f}h")
    share = pct.get(args.gate_family, 0.0)
    verdict = "PASS" if share < args.gate_max else "FAIL"
    print(f"  model-mix gate ({args.gate_family} under {args.gate_max:g}%): {verdict} ({share:.1f}%)")
    print(f"  trend: {trend}")


if __name__ == "__main__":
    main()
