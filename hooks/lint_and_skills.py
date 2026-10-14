#!/usr/bin/env python3
"""PostToolUse (Edit|Write) advisory: lint the edited file and suggest skills
that fit the kind of file that changed.

Lint:
  - .py files inside a project with pyproject.toml: `ruff check` (via uv when
    available, else ruff on PATH)
  - .ts/.tsx files inside a project with package.json: `npx eslint`
Hints:
  - SKILL_HINTS maps path fragments to skills or commands. The defaults point
    at the skills that ship with this setup; edit the table to match the
    skills you have installed.

Output goes to the model's context as plain stdout. Never exits non-zero.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from hookutil import read_payload

# (path fragments, label, [(kind, name, why)]). A hint fires when any fragment
# appears in the normalized path. Several hints can fire for one file.
SKILL_HINTS: list[tuple[tuple[str, ...], str, list[tuple[str, str, str]]]] = [
    (
        ("CHANGELOG", "RELEASE"),
        "release",
        [("Skill", "merge-wp", "checkpoint-merge checklist before landing a branch")],
    ),
    (
        ("handoff", "_STATUS", "_PARALLEL_TRACKS", "_MAILBOX"),
        "orchestration",
        [
            ("Skill", "handoff", "write the next session's handoff at a boundary"),
            ("Skill", "orchestrate-track", "render a track-orchestrator boot prompt"),
        ],
    ),
    (
        ("SKILL.md", "CLAUDE.md", "CONTEXT.md", "/knowledge/"),
        "config",
        [("Command", "/drift-check", "re-index skills and rebuild routing")],
    ),
    (
        ("LICENSES", "/vendor/", "/third_party/"),
        "vendoring",
        [("Skill", "vendor-sweep", "license gate and provenance headers")],
    ),
    (
        ("docs/legal/",),
        "legal",
        [("Skill", "legal-doc-pass", "keep the legal document set consistent")],
    ),
    (
        (".github/workflows/",),
        "ci",
        [("Skill", "runner-setup", "self-hosted runner registration")],
    ),
    (
        ("/plans/", "/artifacts/", "prd_", "plan_"),
        "planning",
        [("Skill", "app-kickoff", "spec-driven kickoff or redirect pipeline")],
    ),
]


def find_up(start: Path, marker: str) -> Path | None:
    """Nearest ancestor directory of start that contains marker."""
    for parent in start.parents:
        if (parent / marker).exists():
            return parent
    return None


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=20)
    except Exception:  # noqa: BLE001
        return None


def lint(path: Path) -> None:
    if path.suffix == ".py":
        root = find_up(path, "pyproject.toml")
        if root is None:
            return
        if shutil.which("uv"):
            cmd = ["uv", "run", "--no-project", "--with", "ruff", "ruff", "check", str(path), "--quiet"]
        elif shutil.which("ruff"):
            cmd = ["ruff", "check", str(path), "--quiet"]
        else:
            return
        result = run(cmd, root)
        if result and result.stdout.strip():
            print("[ruff]", result.stdout.strip()[:1200])
    elif path.suffix in (".ts", ".tsx"):
        root = find_up(path, "package.json")
        if root is None or not shutil.which("npx"):
            return
        result = run(["npx", "--no-install", "eslint", str(path), "--quiet"], root)
        if result and result.stdout.strip():
            print("[eslint]", result.stdout.strip()[:1200])


def hints(norm: str) -> None:
    for fragments, label, entries in SKILL_HINTS:
        if any(fragment in norm for fragment in fragments):
            print(f"[skills:{label}] related to this change:")
            for kind, name, why in entries:
                print(f"  {kind:<7} {name:<20} {why}")


def main() -> None:
    data = read_payload()
    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return
    path = Path(file_path)
    lint(path)
    hints(file_path.replace("\\", "/"))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
