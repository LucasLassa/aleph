
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QScreen

from src.platform.base import Platform
from src.utils.logger import get_logger

log = get_logger(__name__)


class QtGenericPlatform(Platform):

    def set_click_through(self, enabled: bool) -> None:
        self.window.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
        log.info("click_through=%s", enabled)

    def set_always_on_top(self, enabled: bool) -> None:
        self.window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
        log.info("always_on_top=%s", enabled)

    def get_screen_geometry(self) -> QScreen | None:
        return self.window.screen() or QGuiApplication.primaryScreen()
