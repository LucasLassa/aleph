
from __future__ import annotations

import os
import sys

from src.app import App


def _daemonize() -> bool:
    if sys.platform == "win32" or getattr(sys, "frozen", False):
        return False
    if not (hasattr(os, "fork") and hasattr(os, "setsid")):
        return False
    try:
        if os.fork() > 0:
            return True
        os.setsid()
        devnull = os.open(os.devnull, os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
    except OSError:
        return False
    return False

def main() -> int:
    if _daemonize():
        return 0
    app = App(sys.argv)
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
