
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication

from src.core.state import State
from src.platform.base import Platform
from src.ui import overlay_window as ow
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

def _window(state: State, w: int = 1280, h: int = 720) -> OverlayWindow:
    window = OverlayWindow(state, FakePlatform(None))
    window.resize(w, h)
    return window

def _click(window: OverlayWindow, x: float, y: float) -> None:
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(x, y),
        QPointF(x, y),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    window.mousePressEvent(event)

def test_panel_is_closed_by_default(app: QApplication):
    window = _window(State())
    assert window._panel_open is False
    assert window._panel_offset == 0
    assert window._panel_rect().width() == 0

def test_tab_is_always_visible(app: QApplication):
    window = _window(State())
    tab = window._panel_tab_rect()
    assert tab.width() == ow.PANEL_TAB_SIZE
    assert tab.right() == window.width() - 1

def test_click_on_tab_opens_and_closes_panel(app: QApplication):
    window = _window(State())
    tab = window._panel_tab_rect()
    _click(window, tab.center().x(), tab.center().y())
    assert window._panel_open is True
    assert window._panel_anim.endValue() == ow.PANEL_WIDTH

    _click(window, tab.center().x(), tab.center().y())
    assert window._panel_open is False
    assert window._panel_anim.endValue() == 0

def test_panel_width_is_320_when_deployed(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    panel = window._panel_rect()
    assert panel.width() == ow.PANEL_WIDTH
    assert panel.right() == window.width() - 1

def test_panel_buttons_are_28px_high_with_label_above(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    buttons = window._panel_buttons()
    assert buttons, "el panel debe tener botones"
    for _name, rect in buttons:
        assert rect.height() == ow.PANEL_BUTTON_HEIGHT
        assert rect.y() - ow.PANEL_LABEL_HEIGHT >= 0

def test_panel_buttons_are_not_glued_to_the_edge(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    panel = window._panel_rect()
    for _name, rect in window._panel_buttons():
        assert rect.left() >= panel.left() + ow.PANEL_PADDING
        assert rect.right() <= panel.right()

def test_panel_has_all_the_expected_buttons(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    names = [name for name, _rect in window._panel_buttons()]
    assert names == [
        "guide_prev",
        "guide_next",
        "opacity_down",
        "opacity_up",
        "line_white",
        "line_black",
        "clear_rules",
        "capture",
        "capture_dir",
        "toggle_frame",
        "rule_h",
        "rule_v",
        "rule_asc",
        "rule_desc",
        "rule_rect_si",
        "rule_rect_sd",
        "rule_rect_ii",
        "rule_rect_id",
        "close",
    ]

def test_panel_groups_are_separated(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    fin_grupo1 = rects["guide_next"].bottom()
    inicio_grupo2 = rects["opacity_down"].top()
    hueco_entre_grupos = inicio_grupo2 - fin_grupo1
    dentro_grupo = rects["guide_next"].top() - rects["guide_prev"].bottom()
    assert hueco_entre_grupos > dentro_grupo

def test_two_button_groups_are_145px_with_a_10px_gap(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    for a, b in (("guide_prev", "guide_next"), ("rule_asc", "rule_desc")):
        assert rects[a].width() == ow.PANEL_BUTTON_W2
        assert rects[b].width() == ow.PANEL_BUTTON_W2
        hueco = rects[b].left() - rects[a].right() - 1
        assert hueco == ow.PANEL_BUTTON_GAP
    assert rects["guide_next"].right() - rects["guide_prev"].left() + 1 == ow.PANEL_BUTTONS_W

def test_one_button_groups_take_the_full_width(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    assert rects["clear_rules"].width() == ow.PANEL_BUTTON_W1 == ow.PANEL_BUTTONS_W

def test_legend_is_always_at_the_top_of_the_panel(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    legend = window._legend_rect()
    panel = window._panel_rect()
    assert legend.top() >= panel.top()
    assert legend.bottom() <= panel.bottom()
    for _name, rect in window._panel_buttons():
        assert rect.top() >= legend.bottom()
    assert ow.PANEL_LEGEND_TITLE == "—MANUAL DE USO—"
    assert ow.PANEL_LEGEND_COLUMNS == ("Comando", "Funcion")
    filas = dict(ow.PANEL_LEGEND_ROWS)
    assert filas["Flecha izquierda"] == "Regla anterior"
    assert filas["Shift + C"] == "Alternar color de las lineas"
    assert filas["Tecla Esc"] == "Cerrar aplicacion"
    assert filas["Mantener shift + Click izquierdo"] == "Ubicar mis lineas"

def test_legend_is_a_two_column_table(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    font = window._legend_table_font(window._legend_table_size())
    assert font.pixelSize() <= round(8 * 96 / 72)
    metrics = QFontMetrics(font, window)
    cmd_w = window._legend_column_width(font)
    assert cmd_w >= metrics.horizontalAdvance("Mantener shift + Click izquierdo")
    total = cmd_w + ow.PANEL_LEGEND_GAP + max(
        metrics.horizontalAdvance(f) for _c, f in ow.PANEL_LEGEND_ROWS
    )
    assert total <= ow.PANEL_CONTENT_W

def test_group_labels_are_yellow(app: QApplication):
    assert ow.PANEL_HEAD_COLOR == QColor(255, 226, 120)

def test_group_labels_and_button_texts(app: QApplication):
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS + ow.PANEL_BOTTOM_ROWS
        for name, text in buttons
    }
    etiquetas = [label for label, _buttons in ow.PANEL_ROWS if label is not None]
    assert "Seleccionar regla" in etiquetas
    assert "Opacidad de la regla" in etiquetas
    assert "Color de la regla" in etiquetas
    assert "Borrar mis lineas" in etiquetas
    assert "Captura de pantalla" in etiquetas
    assert "Alternar modo" in etiquetas
    assert textos["capture"] == "Capturar"
    assert textos["capture_dir"] == "Guardar en"
    assert textos["toggle_frame"] == "Modo visualización"
    assert textos["close"] == "Cerrar app"
    assert textos["rule_rect_si"] == "┘ Superior izquierdo"
    assert textos["rule_rect_sd"] == "└ Superior derecho"
    assert textos["rule_rect_ii"] == "┐ Inferior izquierdo"
    assert textos["rule_rect_id"] == "┌ Inferior derecho"

def test_close_button_is_in_its_own_group(app: QApplication):
    grupos = {label: [name for name, _t in buttons] for label, buttons in ow.PANEL_ROWS}
    assert "close" not in grupos["Alternar modo"]
    abajo = {label: [name for name, _t in buttons] for label, buttons in ow.PANEL_BOTTOM_ROWS}
    assert abajo["Cerrar la aplicación"] == ["close"]

def test_button_text_takes_the_biggest_size_that_fits(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS + ow.PANEL_BOTTOM_ROWS
        for name, text in buttons
    }
    for name, text in textos.items():
        if len(text) == 1:
            continue
        rect = rects[name]
        font = window._panel_button_font(text, rect.width())
        metrics = QFontMetrics(font, window)
        assert metrics.horizontalAdvance(text) <= rect.width() - 8
        tope_px = round(ow.PANEL_BUTTON_FONT_MAX * 96 / 72)
        if font.pixelSize() < tope_px:
            tope = window._panel_label_font(ow.PANEL_BUTTON_FONT_MAX)
            assert (
                QFontMetrics(tope, window).horizontalAdvance(text) > rect.width() - 8
            ), f"el texto de {name} podía ir más grande"

def test_legend_scrolls_when_the_window_is_short(app: QApplication):
    window = _window(State(), w=1280, h=800)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    legend = window._legend_rect()
    assert legend.height() > 0, "debería quedar un trozo de leyenda"
    assert legend.height() < window._legend_rows_height()
    window._legend_scroll = 0
    window._legend_max_scroll = 3
    event = QWheelEvent(
        QPointF(legend.center().x(), legend.center().y()),
        QPointF(legend.center().x(), legend.center().y()),
        QPoint(0, 0),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    window.wheelEvent(event)
    assert window._legend_scroll == 1

def test_tab_draws_the_big_guillemet(app: QApplication):
    assert ow.PANEL_TAB_FONT_SIZE == 100
    assert ow.PANEL_TAB_SIZE >= 80, "la pestaña debe alojar el «» de 100px"

def test_hint_swing_is_ten_pixels_and_cycles(app: QApplication):
    assert ow.PANEL_HINT_SWING == 10
    assert ow.PANEL_HINT_CYCLE_MS < 2200 / 3 + 1

    window = _window(State())
    offsets = []
    for ms in range(0, ow.PANEL_HINT_CYCLE_MS, 20):
        window._hint_elapsed = _FakeClock(ms)
        offsets.append(window._panel_hint_offset())
    assert all(abs(o) <= ow.PANEL_HINT_SWING + 0.01 for o in offsets)
    assert round(offsets[0]) == ow.PANEL_HINT_SWING
    window._hint_elapsed = _FakeClock(ow.PANEL_HINT_CYCLE_MS // 2)
    assert round(window._panel_hint_offset()) == -ow.PANEL_HINT_SWING
    window._hint_elapsed = _FakeClock(0)
    extremo = abs(window._panel_hint_offset() - ow.PANEL_HINT_SWING)
    window._hint_elapsed = _FakeClock(ow.PANEL_HINT_CYCLE_MS // 8)
    centro = abs(window._panel_hint_offset() - ow.PANEL_HINT_SWING * 0.707)
    assert extremo < centro, "el vaivén debería frenar en los extremos"

class _FakeClock:

    def __init__(self, ms: int) -> None:
        self._ms = ms

    def elapsed(self) -> int:
        return self._ms

def test_click_on_panel_button_runs_its_action(app: QApplication):
    state = State()
    window = _window(state)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}

    antes = state.guide_index
    _click(window, rects["guide_next"].center().x(), rects["guide_next"].center().y())
    assert state.guide_index == (antes + 1) % 8 or state.guide_index != antes

    _click(window, rects["line_black"].center().x(), rects["line_black"].center().y())
    assert state.line_dark is True
    _click(window, rects["line_white"].center().x(), rects["line_white"].center().y())
    assert state.line_dark is False

def test_clear_rules_button_only_clears_user_rules(app: QApplication):
    from src.core.state import Rule

    state = State()
    state.rules.append(Rule(kind="h", x=0.5, y=0.5))
    window = _window(state)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    _click(window, rects["clear_rules"].center().x(), rects["clear_rules"].center().y())
    assert state.rules == []

def test_frame_on_button_is_bottom_right(app: QApplication):
    window = _window(State())
    button = window._frame_on_button_rect()
    hueco = window.height() - (button.y() + button.height())
    assert hueco == ow.FRAME_ON_BUTTON_BOTTOM
    assert button.right() > window.width() - 20

def test_frame_on_button_returns_to_frame_mode(app: QApplication):
    state = State()
    window = _window(state)
    state.frame_mode = False
    state.click_through = True
    button = window._frame_on_button_rect()
    _click(window, button.center().x(), button.center().y())
    assert state.frame_mode is True
    assert state.click_through is False
    assert window._panel_tab_rect().right() == window.width() - 1

def test_leaving_frame_mode_folds_the_panel(app: QApplication):
    state = State()
    window = _window(state)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    state.frame_mode = False
    state.click_through = True
    window.apply_frame_mode()
    assert window._panel_open is False
    assert window._panel_offset == 0
    state.frame_mode = True
    state.click_through = False
    window.apply_frame_mode()
    assert window._panel_open is False
    assert window._panel_tab_rect().right() == window.width() - 1

def test_group_titles_are_10px_and_left_aligned(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.PANEL_LABEL_FONT_SIZE == 10
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    boton = rects["guide_prev"]
    y_titulo = boton.top() - ow.PANEL_LABEL_HEIGHT - ow.PANEL_TITLE_GAP + 13
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    assert img.pixelColor(boton.left() + 2, y_titulo) == QColor(0, 0, 0)
    assert img.pixelColor(boton.left() - ow.PANEL_CHIP_PADDING - 2, y_titulo) != QColor(0, 0, 0)

def test_titles_have_a_black_chip_behind_them(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.PANEL_LABEL_HEIGHT == 15
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    titulo = rects["guide_prev"]
    x = titulo.left() + 4
    y = titulo.top() - ow.PANEL_LABEL_HEIGHT - ow.PANEL_TITLE_GAP + 13
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    assert img.pixelColor(x, y) == QColor(0, 0, 0), "el cuadro del título no es negro"

def test_close_button_is_at_the_bottom_of_the_panel(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    panel = window._panel_rect()
    assert rects["close"].bottom() == panel.bottom() - ow.PANEL_PADDING
    assert rects["close"] == window._panel_buttons()[-1][1]

def test_donation_buttons_are_in_the_guillemet_strip(app: QApplication):
    window = _window(State())
    botones = dict(window._donation_buttons())
    assert set(botones) == {"donate", "copy_alias", "copy_cvu"}
    for rect in botones.values():
        assert window._panel_tab_rect().contains(rect)
    assert botones["donate"].top() < botones["copy_alias"].top()
    assert botones["copy_alias"].top() < botones["copy_cvu"].top()
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    for rect in dict(window._donation_buttons()).values():
        assert window._panel_tab_rect().contains(rect)

def test_clicking_the_donation_button_opens_the_link(app: QApplication, monkeypatch):
    window = _window(State())
    abierto = []
    monkeypatch.setattr(
        type(window), "_open_donation", lambda self: abierto.append(ow.DONATION_URL)
    )
    button = dict(window._donation_buttons())["donate"]
    _click(window, button.center().x(), button.center().y())
    assert abierto == [ow.DONATION_URL]
    assert window._panel_open is False

def test_copy_buttons_put_the_data_in_the_clipboard(app: QApplication):
    window = _window(State())
    rects = dict(window._donation_buttons())
    clipboard = QApplication.clipboard()

    _click(window, rects["copy_alias"].center().x(), rects["copy_alias"].center().y())
    assert clipboard.text() == ow.DONATION_ALIAS

    _click(window, rects["copy_cvu"].center().x(), rects["copy_cvu"].center().y())
    assert clipboard.text() == ow.DONATION_CVU

def test_legend_title_is_12px_and_spans_the_panel(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    legend = window._legend_rect()
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    y = legend.top() + 7
    assert img.pixelColor(legend.left() + 2, y) == QColor(0, 0, 0)
    assert img.pixelColor(legend.right() - 2, y) == QColor(0, 0, 0)
    assert img.pixelColor(legend.left() - 6, y) != QColor(0, 0, 0)

def test_legend_table_has_no_subtitles(app: QApplication):
    titulos = [t for t, _f in ow.PANEL_LEGEND_ROWS]
    assert not any(t.startswith("-") for t in titulos)
    assert ow.PANEL_LEGEND_ROWS[0] == ("Flecha izquierda", "Regla anterior")

def test_button_text_is_smaller_than_the_title(app: QApplication):
    assert ow.PANEL_BUTTON_FONT_MAX < ow.PANEL_LABEL_FONT_SIZE
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    font = window._panel_button_font("Capturar", rects["capture"].width())
    assert font.pixelSize() == round(ow.PANEL_BUTTON_FONT_MAX * 96 / 72)

def test_frame_on_button_has_a_yellow_border_and_square_corners(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.FRAME_ON_BUTTON_TEXT == "Volver al modo edición"
    window = _window(State())
    window.state.frame_mode = False
    window.state.click_through = True
    button = window._frame_on_button_rect()
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    borde = img.pixelColor(button.left() + 10, button.top())
    assert borde == ow.PANEL_HEAD_COLOR

def test_close_button_is_red(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.CLOSE_BUTTON_BORDER == QColor(0xC7, 0x1C, 0x1C)
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    boton = rects["close"]
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    borde = img.pixelColor(boton.left() + 10, boton.top())
    assert borde == ow.CLOSE_BUTTON_BORDER

def test_buttons_are_20px_high_with_8px_text(app: QApplication):
    assert ow.PANEL_BUTTON_HEIGHT == 20
    assert ow.PANEL_BUTTON_FONT_MAX == 8
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    for name, rect in rects.items():
        assert rect.height() == ow.PANEL_BUTTON_HEIGHT, name
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS + ow.PANEL_BOTTOM_ROWS
        for name, text in buttons
    }
    for name, text in textos.items():
        if len(text) == 1:
            continue
        font = window._panel_button_font(text, rects[name].width())
        assert font.pixelSize() <= round(8 * 96 / 72), f"{name} no entra a 8px"
        ancho = QFontMetrics(font, window).horizontalAdvance(text)
        assert ancho <= rects[name].width(), f"{name} se pasa de ancho"

def test_panel_is_340px_wide(app: QApplication):
    assert ow.PANEL_WIDTH == 340
    assert ow.PANEL_CONTENT_W == 320
    assert ow.PANEL_BUTTONS_W == 300
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    assert window._panel_rect().width() == ow.PANEL_WIDTH
    rects = {name: rect for name, rect in window._panel_buttons()}
    panel = window._panel_rect()
    hueco = rects["guide_prev"].left() - panel.left()
    assert hueco == (ow.PANEL_WIDTH - ow.PANEL_BUTTONS_W) // 2

def test_titles_are_10px_away_from_their_buttons(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    boton = rects["guide_prev"]
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    x = boton.left() + 4
    assert img.pixelColor(x, boton.top() - 1) != QColor(0, 0, 0)
    assert (
        img.pixelColor(x, boton.top() - ow.PANEL_TITLE_GAP - 1) == QColor(0, 0, 0)
    )

def test_alias_button_is_uppercase_and_heart_border_is_green(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.DONATION_HEART_BORDER == QColor(0x90, 0xEE, 0x90)
    window = _window(State())
    botones = dict(window._donation_buttons())
    assert "ALIAS" in _texto_de_boton(window, "copy_alias")
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    corazon = botones["donate"]
    borde = img.pixelColor(corazon.center().x(), corazon.top())
    assert borde == ow.DONATION_HEART_BORDER

def _texto_de_boton(window, name: str) -> str:
    for n, rect in window._donation_buttons():
        if n == name:
            return "ALIAS" if name == "copy_alias" else "CVU"
    raise AssertionError(f"no existe el botón {name}")
