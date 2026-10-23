
from __future__ import annotations

from PySide6.QtGui import QRegion

from src.platform.qt_generic import QtGenericPlatform
from src.utils.logger import get_logger

log = get_logger(__name__)


# La class de la ventana sale del nombre del binario: las reglas de
# Hyprland matchean por class:^(aleph)$.
class LinuxWaylandPlatform(QtGenericPlatform):

    def __init__(self, window=None) -> None:
        super().__init__(window)
        self._click_through = False

    def set_click_through(self, enabled: bool) -> None:
        # Wayland: setWindowFlag(WindowTransparentForInput) oculta la ventana.
        # setMask mapea a wl_surface.set_input_region: solo limita input (no
        # recorta el pintado), así el botón sigue siendo clicable.
        self._click_through = enabled
        self.refresh_click_through()
        log.info("click_through=%s (máscara de input)", enabled)

    def refresh_click_through(self) -> None:
        if self.window is None:
            return
        if self._click_through:
            region = QRegion(self.window._frame_on_button_rect())
        else:
            region = QRegion(self.window.rect())
        self.window.setMask(region)
