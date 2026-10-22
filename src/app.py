
from __future__ import annotations

import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from src.config import manager
from src.core.state import State
from src.platform import desktop, get_platform
from src.ui import icons
from src.ui.overlay_window import OverlayWindow
from src.utils.logger import get_logger

log = get_logger(__name__)


class App(QApplication):

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("aleph")
        self.setDesktopFileName("aleph")
        self.setWindowIcon(icons.window_icon())
        data = manager.load()
        self.state = State.from_dict(data)
        self.platform = get_platform(window=None)
        self.window = OverlayWindow(self.state, self.platform)
        self.window.showFullScreen()
        self.aboutToQuit.connect(self._save)
        self._install_sigusr1()
        desktop.install_desktop_shortcut()
        log.info("overlay iniciada (pantalla completa)")

    def _install_sigusr1(self) -> None:
        if not hasattr(signal, "SIGUSR1"):
            log.info("SIGUSR1 no disponible en %s: toggle solo vía teclado/toolbar", sys.platform)
            return
        self._sigusr1_pending = False
        signal.signal(signal.SIGUSR1, self._mark_sigusr1)
        self._sigusr1_timer = QTimer(self)
        self._sigusr1_timer.setInterval(100)
        self._sigusr1_timer.timeout.connect(self._poll_sigusr1)
        self._sigusr1_timer.start()

    def _mark_sigusr1(self, *_: object) -> None:
        self._sigusr1_pending = True

    def _poll_sigusr1(self) -> None:
        if not self._sigusr1_pending:
            return
        self._sigusr1_pending = False
        self.state.frame_mode = not self.state.frame_mode
        self.state.click_through = not self.state.frame_mode
        self.window.apply_frame_mode()
        log.info("frame_mode=%s (vía SIGUSR1)", self.state.frame_mode)

    def _save(self) -> None:
        manager.save(self.state.to_dict())
