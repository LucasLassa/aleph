
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QPixmap, QScreen


def _has_wayland() -> bool:
    return QGuiApplication.platformName().startswith("wayland")

class ScreenGrabber:

    def grab(self) -> QPixmap | None:
        raise NotImplementedError

class QtGrabber(ScreenGrabber):

    def __init__(self, screen: QScreen | None = None) -> None:
        self.screen = screen or QGuiApplication.primaryScreen()

    def grab(self) -> QPixmap | None:
        if self.screen is None:
            return None
        pixmap = self.screen.grabWindow(0)
        if pixmap.isNull():
            return None
        return pixmap

class GrimGrabber(ScreenGrabber):

    BINARY = "grim"

    def __init__(self, binary: str | None = None) -> None:
        self.binary = binary or self.BINARY

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def grab(self) -> QPixmap | None:
        if not self.available():
            return None
        with tempfile.TemporaryDirectory(prefix="overlay-captura-") as tmp:
            name = "captura.png"
            try:
                result = subprocess.run(
                    [self.binary, name],
                    cwd=tmp,
                    capture_output=True,
                    timeout=30,
                )
            except (OSError, subprocess.SubprocessError):
                return None
            if result.returncode != 0:
                return None
            path = Path(tmp) / name
            if not path.exists():
                return None
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                return None
            return pixmap

def make_grabber(screen: QScreen | None = None) -> ScreenGrabber:
    if _has_wayland():
        return GrimGrabber()
    return QtGrabber(screen)
