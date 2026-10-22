
from __future__ import annotations

import datetime
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QColor, QImage, QPainter

from src.core import guides, rules
from src.core.state import State
from src.platform.capture import ScreenGrabber

FILENAME_FORMAT = "aleph-%Y%m%d-%H%M%S.png"


def default_capture_dir() -> Path:
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
    return Path(loc) if loc else Path.home() / "Downloads"

def capture_dir(state: State) -> Path:
    if state.capture_dir:
        return Path(state.capture_dir)
    return default_capture_dir()

def capture_filename(moment: datetime.datetime | None = None) -> str:
    moment = moment or datetime.datetime.now()
    return moment.strftime(FILENAME_FORMAT)

def overlay_on_image(
    image: QImage, state: State, color: QColor | None = None
) -> QImage:
    if color is None:
        color = QColor(0, 0, 0) if state.line_dark else QColor(255, 255, 255)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    guides.draw(painter, image.width(), image.height(), state, color=color)
    rules.draw(painter, image.width(), image.height(), state.rules, color)
    painter.end()
    return image

def capture_with_guides(
    grabber: ScreenGrabber, state: State
) -> tuple[QImage | None, Path | None]:
    pixmap = grabber.grab()
    if pixmap is None:
        return None, None
    image = pixmap if isinstance(pixmap, QImage) else pixmap.toImage()
    if image.isNull():
        return None, None
    overlay_on_image(image, state)
    target_dir = capture_dir(state)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None, None
    path = target_dir / capture_filename()
    if not image.save(str(path), "PNG"):
        return None, None
    return image, path
