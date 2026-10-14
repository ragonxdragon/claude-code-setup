#!/usr/bin/env python3
"""PostToolUse (Glob|Grep) hook: strip build-artifact paths (node_modules,
target, vcpkg_installed, build, dist, gen, .git) from Glob and Grep results
before the model sees them, by returning updatedToolOutput.

NOT REGISTERED in settings.example.json. When this was written, Claude Code
honored PostToolUse output replacement only for MCP tools
(updatedMCPToolOutput), not for built-in tools such as Glob and Grep; see
anthropics/claude-code issue 32105. The filtering logic is covered by
hooks_selftest.py. Register it on a `Glob|Grep` PostToolUse matcher once
built-in output replacement ships, then confirm with one real Glob call.

Never blocks. On any error the output passes through unfiltered.
"""

from __future__ import annotations

import json
import sys

from hookutil import read_payload

NOISE_SEGMENTS = {"node_modules", "target", "vcpkg_installed", "build", "dist", "gen", ".git"}


def is_noise_path(path: str) -> bool:
    segments = {seg.lower() for seg in path.replace("\\", "/").split("/") if seg}
    return bool(segments & NOISE_SEGMENTS)


def filter_glob(resp: dict) -> str:
    filenames = resp.get("filenames", []) or []
    kept = [f for f in filenames if not is_noise_path(f)]
    removed = len(filenames) - len(kept)
    lines = list(kept) if kept else ["No files found"]
    if resp.get("truncated"):
        total = resp.get("totalMatches")
        shown = len(filenames)
        if isinstance(total, int):
            lines.append(
                f"(Showing {shown} of {total} matching files; {total - shown} more are "
                "not listed. Narrow the pattern or path to see the rest.)"
            )
    if removed:
        lines.append(
            f"[noise-filter] Removed {removed} build-artifact matches "
            "(node_modules/target/vcpkg_installed/build/dist/gen/.git)."
        )
    return "\n".join(lines)


def _split_lines(resp: dict) -> list[str]:
    content = resp.get("content", "") or ""
    return content.split("\n") if content else []


def filter_grep(resp: dict) -> str | None:
    mode = resp.get("mode")

    if mode == "files_with_matches":
        filenames = resp.get("filenames", []) or []
        kept = [f for f in filenames if not is_noise_path(f)]
        removed = len(filenames) - len(kept)
        header = f"Found {len(kept)} files"
        if "appliedLimit" in resp:
            header += f" limit: {resp['appliedLimit']}"
        lines = [header, *kept]
        if removed:
            lines.append(f"[noise-filter] Removed {removed} build-artifact matches.")
        return "\n".join(lines)

    if mode == "content":
        kept_lines = []
        removed = 0
        for line in _split_lines(resp):
            if is_noise_path(line.split(":", 1)[0]):
                removed += 1
            else:
                kept_lines.append(line)
        text = "\n".join(kept_lines)
        if removed:
            text += f"\n[noise-filter] Removed {removed} build-artifact match lines."
        return text

    if mode == "count":
        kept_lines = []
        removed = 0
        removed_matches = 0
        for line in _split_lines(resp):
            if not line:
                continue
            path_part, _, count_part = line.rpartition(":")
            if is_noise_path(path_part):
                removed += 1
                if count_part.strip().isdigit():
                    removed_matches += int(count_part)
            else:
                kept_lines.append(line)
        text = "\n".join(kept_lines)
        if removed:
            text += f"\n[noise-filter] Removed {removed} files ({removed_matches} matches) from build-artifact dirs."
        return text

    return None


def main() -> None:
    data = read_payload()
    tool_name = data.get("tool_name", "")
    resp = data.get("tool_response", {}) or {}

    if tool_name == "Glob":
        updated = filter_glob(resp)
    elif tool_name == "Grep":
        updated = filter_grep(resp)
    else:
        updated = None

    if updated is not None:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "updatedToolOutput": updated,
                    },
                }
            )
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - never break the tool call on a hook bug
        pass
    sys.exit(0)
