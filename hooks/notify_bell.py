#!/usr/bin/env python3
"""Notification hook: audible alert when Claude needs input. Writes a terminal
bell (BEL) and, on Windows, plays the system beep so the alert is heard even
when the terminal swallows BEL.

Always exits 0. Fails open. ASCII-only output.
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        sys.stdin.read()  # consume the payload
    except Exception:  # noqa: BLE001
        pass
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:  # noqa: BLE001
        pass
    try:
        import winsound

        winsound.MessageBeep()
    except Exception:  # noqa: BLE001 - not Windows, or no sound device
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
