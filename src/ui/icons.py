
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon

ICON_FILENAME = "icon.png"


def icon_path() -> Path:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base = Path(meipass)
            candidates.append(base / "resources" / ICON_FILENAME)
            candidates.append(base.parent / "Resources" / "resources" / ICON_FILENAME)
    candidates.append(Path(__file__).resolve().parent.parent / "resources" / ICON_FILENAME)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]

def window_icon() -> QIcon:
    path = icon_path()
    if not path.exists():
        return QIcon()
    return QIcon(str(path))
