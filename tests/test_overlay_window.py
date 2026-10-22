
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from src.core import keymap
from src.core.state import State
from src.platform.base import Platform
from src.ui.overlay_window import OverlayWindow


class FakePlatform(Platform):

    def __init__(self) -> None:
        super().__init__(window=None)
        self.click_through: list[bool] = []

    def set_click_through(self, enabled: bool) -> None:
        self.click_through.append(enabled)

    def set_always_on_top(self, enabled: bool) -> None:
        pass

    def get_screen_geometry(self):
        return None

@pytest.fixture(scope="module")
def app() -> QApplication:
    yield QApplication.instance() or QApplication([])

def _toggle(window: OverlayWindow, state: State) -> None:
    assert keymap.handle("M", state) == "toggle_frame"
    window.apply_frame_mode()

def test_frame_toggle_keeps_visible_and_fullscreen(app: QApplication):
    state = State()
    platform = FakePlatform()
    window = OverlayWindow(state, platform)
    window.showFullScreen()
    assert window.isVisible()
    assert window.isFullScreen()

    for click_through in (True, False, True, False):
        _toggle(window, state)
        assert window.isVisible(), "setWindowFlag oculta la ventana: falta show()"
        assert window.isFullScreen(), "alternar el marco no debe salir de fullscreen"
        assert state.frame_mode is not click_through
        assert platform.click_through[-1] is click_through

    assert platform.click_through == [True, False, True, False]
