
from __future__ import annotations

import ctypes
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication, QScreen

from src.platform.base import Platform
from src.utils.logger import get_logger

log = get_logger(__name__)

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
CT_POLL_MS = 50


class QtGenericPlatform(Platform):

    def __init__(self, window=None) -> None:
        super().__init__(window)
        self._ct_timer: QTimer | None = None

    def set_click_through(self, enabled: bool) -> None:
        if sys.platform == "win32":
            self._win_set_click_through(enabled)
        else:
            # ponytail: X11/macOS quedan con el flag global de Qt (botón no
            # clicable en modo visualización); el mismo poll de QCursor.pos
            # serviría si algún día hay que arreglarlos.
            self.window.setWindowFlag(
                Qt.WindowType.WindowTransparentForInput, enabled
            )
        log.info("click_through=%s", enabled)

    def _win_set_click_through(self, enabled: bool) -> None:
        # Windows: setWindowFlag(WindowTransparentForInput) recrea/oculta la
        # ventana. Se alterna el bit WS_EX_TRANSPARENT (click-through entre
        # procesos, igual que hace Qt) y un poll abre input solo sobre el
        # botón cuando hay click-through.
        if enabled:
            self._apply_win_transparent(True)
            self._start_ct_poll()
        else:
            self._stop_ct_poll()
            self._apply_win_transparent(False)

    def _apply_win_transparent(self, on: bool) -> bool:
        if self.window is None:
            return False
        user32 = ctypes.windll.user32
        hwnd = int(self.window.winId())
        style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        if bool(style & WS_EX_TRANSPARENT) == on:
            return False
        new = style | WS_EX_TRANSPARENT if on else style & ~WS_EX_TRANSPARENT
        user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new)
        return True

    def _start_ct_poll(self) -> None:
        if self._ct_timer is None:
            self._ct_timer = QTimer()
            self._ct_timer.setInterval(CT_POLL_MS)
            self._ct_timer.timeout.connect(self._poll_click_through)
        self._ct_timer.start()

    def _stop_ct_poll(self) -> None:
        if self._ct_timer is not None:
            self._ct_timer.stop()

    def _poll_click_through(self) -> None:
        window = self.window
        if window is None:
            return
        inside = window._frame_on_button_rect().contains(
            window.mapFromGlobal(QCursor.pos())
        )
        changed = self._apply_win_transparent(not inside)
        if changed and not inside:
            window.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def set_always_on_top(self, enabled: bool) -> None:
        self.window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
        log.info("always_on_top=%s", enabled)

    def get_screen_geometry(self) -> QScreen | None:
        return self.window.screen() or QGuiApplication.primaryScreen()
