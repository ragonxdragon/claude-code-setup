#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell) hook: rewrite a recognized test-runner command
so its output reaches the context already filtered to failures, errors, and the
summary line, instead of the full log.

Keeps pass and summary markers as well as failures, so an all-green run still
shows a one-line confirmation. Filtering a green run down to nothing would look
the same as a broken pipeline.

Only plain, single test commands are rewritten. A command that chains other
work (`;`, `&&`, `||`, a pipe, command substitution, a newline) passes through
untouched, because the rewrite is returned with permissionDecision "allow" and
would otherwise auto-approve whatever was chained after the test runner.

Never blocks. Exit 0 in every case.
"""

from __future__ import annotations

import json
import re
import sys

from hookutil import read_payload, shell_command

TEST_RUNNERS = re.compile(
    r"^\s*("
    r"cargo\s+test|cargo\s+bench|"
    r"ctest|"
    r"npm\s+(run\s+)?test|yarn\s+test|pnpm\s+(run\s+)?test|"
    r"(npx\s+)?vitest|"
    r"(python3?\s+-m\s+|uv\s+run\s+)?pytest|"
    r"go\s+test|"
    r"dotnet\s+test"
    r")\b",
    re.IGNORECASE,
)

# Shell syntax that chains or embeds another command.
COMPOUND = re.compile(r"[;&|`\n]|\$\(")

KEEP_PATTERN = r"(FAIL|ERROR|error:|panicked|assertion|test result:|passed|failed|PASS)"


def build_filtered_command(tool_name: str, cmd: str) -> str:
    if tool_name == "PowerShell":
        return f"{cmd} 2>&1 | Select-String -Pattern '{KEEP_PATTERN}' | Select-Object -First 200"
    return f"{cmd} 2>&1 | grep -E -A 5 '{KEEP_PATTERN}' | head -200"


def main() -> None:
    data = read_payload()
    cmd = shell_command(data)
    if not cmd or not TEST_RUNNERS.search(cmd) or COMPOUND.search(cmd):
        sys.exit(0)

    filtered = build_filtered_command(data.get("tool_name", ""), cmd.strip())
    # Carry the other input fields (timeout, description) through unchanged.
    updated = dict(data.get("tool_input") or {})
    updated["command"] = filtered
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "updatedInput": updated,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
