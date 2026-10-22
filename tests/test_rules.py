
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter

from src.core import keymap, rules
from src.core.state import Rule, State


def _render(rule_list, w=200, h=100):
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    rules.draw(p, w, h, rule_list, QColor(255, 255, 255))
    p.end()
    return img

def _opaque_columns(img, row):
    return [x for x in range(img.width()) if img.pixelColor(x, row).alpha() > 0]

def test_horizontal_rule_spans_full_width():
    img = _render([Rule(kind="h", x=0.5, y=0.5)])
    cols = _opaque_columns(img, 50)
    assert cols, "no se dibujó nada"
    assert min(cols) <= 1, "no llega al borde izquierdo"
    assert max(cols) >= img.width() - 2, "no llega al borde derecho"

def test_vertical_rule_spans_full_height():
    img = _render([Rule(kind="v", x=0.5, y=0.5)])
    rows = [y for y in range(img.height()) if img.pixelColor(100, y).alpha() > 0]
    assert rows, "no se dibujó nada"
    assert min(rows) <= 1
    assert max(rows) >= img.height() - 2

def test_rect_rule_lines_stop_at_vertex():
    img = _render([Rule(kind="rect", x=0.5, y=0.5, corner=0)])
    vx, vy = 100, 50
    row = _opaque_columns(img, vy)
    assert row, "no se dibujó la línea horizontal"
    assert min(row) <= 1, "la horizontal debería llegar al borde izquierdo"
    assert max(row) <= vx + 2, f"la horizontal no debería pasar del vértice: {max(row)}"
    col = [y for y in range(img.height()) if img.pixelColor(vx, y).alpha() > 0]
    assert col, "no se dibujó la línea vertical"
    assert min(col) <= 1
    assert max(col) <= vy + 2, f"la vertical no debería pasar del vértice: {max(col)}"

def test_rect_rule_grows_toward_opposite_diagonal():
    img = _render([Rule(kind="rect", x=0.5, y=0.5, corner=3)])
    vx, vy = 100, 50
    row = _opaque_columns(img, vy)
    assert min(row) >= vx - 2, "la horizontal debería ir a la derecha"
    assert max(row) >= img.width() - 2
    col = [y for y in range(img.height()) if img.pixelColor(vx, y).alpha() > 0]
    assert min(col) >= vy - 2
    assert max(col) >= img.height() - 2

def test_rule_line_thickness_matches_guides():
    assert rules.LINE_WIDTH == 1.5
    assert rules.OUTLINE_WIDTH == 3.0
    from src.core import guides

    src = open(guides.__file__, encoding="utf-8").read()
    assert "3.0" in src and "1.5" in src

def test_rule_vertex_stored_as_fraction():
    rule = Rule(kind="rect", x=0.25, y=0.75, corner=0)
    assert 0.0 <= rule.x <= 1.0
    assert 0.0 <= rule.y <= 1.0

def test_shift_backspace_clears_only_user_rules():
    indice = 4
    state = State(guide_index=indice)
    state.rules.append(Rule(kind="h", x=0.5, y=0.5))
    state.rules.append(Rule(kind="rect", x=0.3, y=0.3, corner=1))
    assert len(state.rules) == 2

    action = keymap.handle("Backspace", state, shift=True)
    assert action == "clear_rules"
    assert state.rules == []
    assert state.guide_index == indice

def test_plain_backspace_does_nothing():
    state = State()
    state.rules.append(Rule(kind="h", x=0.5, y=0.5))
    assert keymap.handle("Backspace", state, shift=False) is None
    assert len(state.rules) == 1
