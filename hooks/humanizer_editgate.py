#!/usr/bin/env python3
"""Edit/Write gate for mechanical writing-style patterns that read as
machine-generated: em and en dashes, curly quotes and emoji in source code,
and a spaced double hyphen used as prose punctuation in comments.

Register it under PreToolUse (matcher Edit|Write): exit 2 vetoes the write
before anything reaches disk, and stderr tells the model what to fix. It can
also be registered under PostToolUse as a backstop; there exit 2 returns the
same feedback after the write.

Checked: the text the tool call introduces (Write content, Edit new_string,
MultiEdit edits), for files with a source or text extension.
Skipped: generated and vendored directories, plus any path that contains a
substring listed in HUMANIZER_GATE_EXCLUDE (comma-separated), for example
"i18n/locales/,manuscript/". A line that ends with `humanizer-allow` is
skipped as well.

Any error, or a file type outside the list, exits 0 so editing never breaks.
"""

from __future__ import annotations

import os
import re
import sys

from hookutil import read_payload, utf8_stdio

CODE_EXT = (".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py")
TEXT_EXT = CODE_EXT + (".md", ".markdown", ".yaml", ".yml", ".json", ".toml")
DEFAULT_EXCLUDE = ("node_modules/", "target/", "dist/", "build/", ".git/", "vendor/", "third_party/")

DASH = re.compile("[\u2014\u2013]")
CURLY = re.compile("[\u201c\u201d\u2018\u2019]")
EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\U0001f1e6-\U0001f1ff\ufe0f\u2139]")
PROSE_DD = re.compile(r"(?<!-) -- (?!-)")
# Lines where " -- " is syntax, not punctuation: CLI separators, SQL, markers.
DD_SAFE = re.compile(
    r"nosemgrep|DROP TABLE|-{4,}|<!--|-->|"
    r"\b(cargo|npm|npx|pnpm|yarn|git|run|exec|sh|bash|uv|uvx|python3?)\b"
)


def excluded(path: str) -> bool:
    extra = os.environ.get("HUMANIZER_GATE_EXCLUDE", "")
    patterns = DEFAULT_EXCLUDE + tuple(p.strip() for p in extra.split(",") if p.strip())
    return any(p in path for p in patterns)


def is_comment(path: str, line: str) -> bool:
    if path.endswith((".md", ".markdown")):
        return True
    stripped = line.lstrip()
    return stripped.startswith(("//", "#", "*", "/*")) or "//" in line


def new_text(tool_input: dict) -> str:
    """The text this Edit, Write, or MultiEdit introduces."""
    if "content" in tool_input:  # Write
        return tool_input["content"] or ""
    if "edits" in tool_input:  # MultiEdit
        return "\n".join(e.get("new_string", "") for e in tool_input["edits"])
    return tool_input.get("new_string", "") or ""  # Edit


def violations(path: str, text: str) -> list[tuple[str, str]]:
    code = path.endswith(CODE_EXT)
    found = []
    for line in text.splitlines():
        if line.rstrip().endswith("humanizer-allow"):
            continue
        if DASH.search(line):
            found.append(("em/en dash", line))
        if code and CURLY.search(line):
            found.append(("curly quote", line))
        if code and EMOJI.search(line):
            found.append(("emoji", line))
        if is_comment(path, line) and PROSE_DD.search(line) and not DD_SAFE.search(line):
            found.append(("prose --", line))
    return found


def main() -> int:
    utf8_stdio()
    tool_input = read_payload().get("tool_input") or {}
    path = (tool_input.get("file_path") or "").replace("\\", "/")
    if not path or not path.endswith(TEXT_EXT) or excluded(path):
        return 0

    found = violations(path, new_text(tool_input))
    if not found:
        return 0
    out = [
        "Humanizer gate: this edit introduced patterns that read as machine-written.",
        "Fix them now, or end a line with 'humanizer-allow' to keep it:",
    ]
    for rule, line in found[:20]:
        out.append(f"  [{rule}]  {line.strip()[:100]}")
    out.append("Replace: em/en dashes with , . : or ( ); curly quotes with straight quotes;")
    out.append("remove emoji from source; turn ' -- ' into , . or : as a real clause.")
    sys.stderr.write("\n".join(out) + "\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - never break editing on a hook bug
        sys.exit(0)
