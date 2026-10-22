
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication

from src.core import rules
from src.core.state import Rule, State
from src.platform.base import Platform
from src.ui.overlay_window import OverlayWindow


class FakePlatform(Platform):

    def set_click_through(self, enabled: bool) -> None:
        pass

    def set_always_on_top(self, enabled: bool) -> None:
        pass

    def get_screen_geometry(self):
        return None

@pytest.fixture(scope="module")
def app() -> QApplication:
    yield QApplication.instance() or QApplication([])

def _render(rule_list, w=200, h=120):
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0))
    p = QPainter(img)
    rules.draw(p, w, h, rule_list, QColor(255, 255, 255))
    p.end()
    return img

def _white_at(img, x, y):
    return img.pixelColor(x, y).red() > 200

def _white_near(img, x, y, radius=3):
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            px, py = x + dx, y + dy
            if 0 <= px < img.width() and 0 <= py < img.height():
                if _white_at(img, px, py):
                    return True
    return False

def test_diagonal_desc_runs_from_top_left_to_bottom_right():
    img = _render([Rule(kind="desc", x=0, y=0, corner=0)])
    w, h = img.width(), img.height()
    assert _white_near(img, 2, 2), "no pasa por la esquina superior izquierda"
    assert _white_near(img, w - 3, h - 3), "no pasa por la inferior derecha"
    assert not _white_near(img, 2, h - 3)

def test_diagonal_asc_runs_from_bottom_left_to_top_right():
    img = _render([Rule(kind="asc", x=0.5, y=0.5, corner=0)])
    w, h = img.width(), img.height()
    assert _white_near(img, 2, h - 3), "no pasa por la esquina inferior izquierda"
    assert _white_near(img, w - 3, 2), "no pasa por la esquina superior derecha"
    assert _white_near(img, w // 2, h // 2), "no pasa por el centro"

def test_diagonals_cross_at_the_center():
    img = _render([Rule(kind="desc", x=0, y=0, corner=0), Rule(kind="asc", x=0, y=0, corner=0)])
    w, h = img.width(), img.height()
    assert _white_at(img, w // 2, h // 2)

def test_diagonals_slide_with_their_point():
    a = _render([Rule(kind="desc", x=0.25, y=0.50, corner=0)])
    b = _render([Rule(kind="desc", x=0.75, y=0.50, corner=0)])
    assert a != b, "el punto de paso debería mover la diagonal"
    img = _render([Rule(kind="desc", x=0.5, y=0.5, corner=0)])
    w, h = img.width(), img.height()
    assert _white_near(img, w // 2, h // 2), "la diagonal debería pasar por su punto"

def test_panel_buttons_include_the_two_diagonals():
    from src.ui.overlay_window import RULE_KINDS

    kinds = [kind for kind, _corner in RULE_KINDS.values()]
    assert "asc" in kinds
    assert "desc" in kinds

def test_guillemet_glyph_matches_the_diagonal_it_draws():
    from src.ui.overlay_window import PANEL_ROWS

    textos = {
        name: text
        for _label, buttons in PANEL_ROWS
        for name, text in buttons
    }
    assert textos["rule_asc"].startswith("╱")
    assert textos["rule_desc"].startswith("╲")

def test_unlocking_fullscreen_centers_on_its_own_screen(app: QApplication):
    from PySide6.QtCore import QRect

    class FakeScreen:
        def __init__(self, x, y, w, h):
            self._g = QRect(x, y, w, h)

        def geometry(self):
            return self._g

    class TwoMonitorPlatform(FakePlatform):
        def get_screen_geometry(self):
            return FakeScreen(1920, 0, 2560, 1440)

    state = State()
    window = OverlayWindow(state, TwoMonitorPlatform(None))
    window.resize(1920, 1080)
    window.showFullScreen()

    state.fullscreen = True
    window.toggle_fullscreen()

    geom = window.geometry()
    assert geom.left() >= 1920, f"la ventana quedó en el monitor equivocado: {geom}"
    esperado_izq = 1920 + (2560 - geom.width()) // 2
    assert abs(geom.left() - esperado_izq) <= 1, f"no está centrada: {geom}"
    assert geom.width() <= 2560 and geom.height() <= 1440
