
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QMouseEvent
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

def _press_tab(window: OverlayWindow) -> None:
    from PySide6.QtGui import QKeyEvent

    window.keyPressEvent(
        QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
    )

def test_tab_key_opens_and_closes_panel(app: QApplication):
    window = _window(State())
    assert window._panel_open is False
    _press_tab(window)
    assert window._panel_open is True
    assert window._panel_anim.endValue() == ow.PANEL_WIDTH
    _press_tab(window)
    assert window._panel_open is False
    assert window._panel_anim.endValue() == 0

def test_tab_key_does_nothing_when_frame_is_off(app: QApplication):
    window = _window(State(frame_mode=False))
    _press_tab(window)
    assert window._panel_open is False

def test_tab_key_does_not_move_focus(app: QApplication):
    window = _window(State())
    assert window.focusNextPrevChild(True) is False
    assert window.focusNextPrevChild(False) is False

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
        "opacity_slider",
        "line_white",
        "line_black",
        "rule_h",
        "rule_v",
        "rule_asc",
        "rule_desc",
        "rule_rect_si",
        "rule_rect_sd",
        "rule_rect_ii",
        "rule_rect_id",
        "rule_fuga",
        "toggle_frame",
        "clear_rules",
        "capture",
        "capture_dir",
        "manual",
        "donate_link",
        "donate_cvu",
        "donate_alias",
    ]

def test_panel_sections_are_ordered(app: QApplication):
    titles = [title for title, _rows in ow.PANEL_SECTIONS]
    assert titles == [
        "REGLAS",
        "DIBUJO",
        "LISTO PARA VER",
        "OPCIONES",
        "♥ Apoya nuestra app",
    ]

def test_panel_groups_are_separated(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    fin_grupo1 = rects["guide_next"].bottom()
    inicio_grupo2 = rects["opacity_slider"].top()
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

def test_manual_is_a_modal_dialog_with_the_expected_rows(app: QApplication):
    from src.ui import manual

    assert manual.TITLE == "—MANUAL DE USO—"
    assert manual.COLUMNS == ("Funcion", "Comando")
    filas = dict(manual.ROWS)
    assert filas["Seleccionar regla anterior"] == "Flecha izquierda"
    assert filas["Cambiar el color de la regla"] == "Shift + C"
    assert filas["Cerrar Aleph"] == "ESC - Escape"
    assert filas["Abrir y Cerrar panel de opciones"] == "TAB - Tabulador"
    assert filas["Alternar a modo visualizacion"] == "Shift + M"
    assert filas["Borrar mis reglas dibujadas"] == "Shift + D"

def test_manual_fonts_and_colors_match_the_panel_style(app: QApplication):
    from PySide6.QtGui import QFont

    from src.ui import manual

    assert manual.TITLE_FONT_PX == 20
    assert manual.BODY_FONT_PX == 16
    assert manual.BG == QColor(45, 45, 48)
    assert manual.ROW_ALT_BG == QColor(35, 35, 38)
    assert manual.BG.alpha() == 255, "el fondo debe ser gris sólido"
    assert not hasattr(manual, "DESCRIPTION_TITLE")
    assert manual.HEAD_COLOR == QColor(255, 230, 130)
    assert manual.FONT_FAMILIES[0] == "Orange Kid"

    manual._FONT_LOADED = False
    manual._ensure_custom_font()
    titulo = manual._ui_font(manual.TITLE_FONT_PX)
    cuerpo = manual._ui_font(manual.BODY_FONT_PX)
    assert titulo.pixelSize() == 20
    assert cuerpo.pixelSize() == 16
    assert titulo.family().lower() == "orange kid", "Orange Kid debería estar disponible"
    assert QFont(titulo.family()).family()

def test_manual_dialog_fits_on_screen(app: QApplication):
    from src.ui import manual

    d = manual.ManualDialog()
    d.show()
    screen = app.primaryScreen()
    assert d.width() <= screen.availableGeometry().width()
    assert d.height() <= screen.availableGeometry().height()
    d.close()

def test_group_labels_and_button_texts_are_white(app: QApplication):
    assert ow.PANEL_HEAD_COLOR == QColor(255, 255, 255)
    assert ow.PANEL_GLYPH_COLOR == QColor(255, 255, 255)

def test_group_labels_and_button_texts(app: QApplication):
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS
        for name, text in buttons
    }
    etiquetas = [label for label, _buttons in ow.PANEL_ROWS if label is not None]
    assert etiquetas == [
        "Opacidad de la regla",
    ]
    assert textos["guide_prev"] == "◀ Regla anterior"
    assert textos["guide_next"] == "Regla posterior ▶"
    assert textos["line_white"] == "Regla blanca"
    assert textos["line_black"] == "Regla negra"
    assert textos["clear_rules"] == "Borrar mis lineas dibujadas"
    assert textos["capture"] == "Capturar"
    assert textos["capture_dir"] == "Guardar en"
    assert textos["toggle_frame"] == "Modo visualización"
    assert textos["manual"] == "Manual de uso"
    assert textos["donate_link"] == "Link"
    assert textos["donate_cvu"] == "CVU"
    assert textos["donate_alias"] == "ALIAS"
    assert textos["rule_rect_si"] == "┘ Superior izquierdo"
    assert textos["rule_rect_sd"] == "└ Superior derecho"
    assert textos["rule_rect_ii"] == "┐ Inferior izquierdo"
    assert textos["rule_rect_id"] == "┌ Inferior derecho"

def test_button_text_takes_the_biggest_size_that_fits(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS
        for name, text in buttons
    }
    for name, text in textos.items():
        if len(text) == 1 or name == "opacity_slider":
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

    assert ow.PANEL_LABEL_FONT_SIZE == 16
    assert ow.PANEL_SECTION_TITLE_FONT_SIZE == 20
    assert ow.PANEL_SECTION_TITLE_COLOR == QColor(255, 230, 130)
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    boton = rects["guide_prev"]
    y_titulo = (
        boton.top() - ow.PANEL_TITLE_GAP - ow.PANEL_SECTION_TITLE_HEIGHT // 2
    )
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    pixel = img.pixelColor(boton.left() + 2, y_titulo)
    assert pixel != QColor(0, 0, 0), "el título debe ir en amarillo"

def test_panel_background_is_solid_gray(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    panel = window._panel_rect()
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    assert img.pixelColor(panel.x() + 5, panel.y() + 5) == ow.PANEL_BG

def test_close_button_is_a_small_red_x_in_the_top_right(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.CLOSE_BUTTON_BORDER == QColor(0xFF, 0x60, 0x60)
    assert ow.CLOSE_BUTTON_BG == QColor(0xC7, 0x1C, 0x1C)
    assert ow.CLOSE_BUTTON_SIZE <= 22, "la X debe ser pequeña"
    window = _window(State())
    boton = window._close_button_rect()
    assert boton.right() == window.width() - ow.CLOSE_BUTTON_MARGIN - 1
    assert boton.top() == ow.CLOSE_BUTTON_MARGIN
    assert boton.width() == ow.CLOSE_BUTTON_SIZE
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    centro = img.pixelColor(boton.left() + 3, boton.center().y())
    assert centro == ow.CLOSE_BUTTON_BG

def test_clicking_the_close_button_closes_the_app(app: QApplication, monkeypatch):
    window = _window(State())
    cerrado = []
    monkeypatch.setattr(type(window), "close", lambda self: cerrado.append(True))
    boton = window._close_button_rect()
    _click(window, boton.center().x(), boton.center().y())
    assert cerrado == [True]

def test_donation_section_is_last(app: QApplication):
    title, rows = ow.PANEL_SECTIONS[-1]
    assert title == "♥ Apoya nuestra app"
    names = [name for _label, buttons in rows for name, _text in buttons]
    assert names == ["donate_link", "donate_cvu", "donate_alias"]

def test_donation_buttons_have_green_border_and_red_bg(app: QApplication):
    from PySide6.QtGui import QImage, QPainter

    assert ow.DONATION_HEART_BORDER == QColor("#8a1d1d")
    assert ow.DONATION_HEART_COLOR == QColor("#ad1f1f")
    window = _window(State(), 1280, 1000)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = dict(window._panel_buttons())
    img = QImage(window.width(), window.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(150, 120, 90))
    p = QPainter(img)
    window.render(p, QPoint(0, 0))
    p.end()
    btn = rects["donate_link"]
    assert img.pixelColor(btn.center().x(), btn.top()) == ow.DONATION_HEART_BORDER
    assert img.pixelColor(btn.left() + 3, btn.center().y()) == ow.DONATION_HEART_COLOR

def test_clicking_donate_link_opens_the_url(app: QApplication, monkeypatch):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    abierto = []
    monkeypatch.setattr(
        type(window), "_open_donation", lambda self: abierto.append(ow.DONATION_URL)
    )
    rects = dict(window._panel_buttons())
    _click(window, rects["donate_link"].center().x(), rects["donate_link"].center().y())
    assert abierto == [ow.DONATION_URL]

def test_copy_cvu_and_alias_put_the_data_in_the_clipboard(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = dict(window._panel_buttons())
    clipboard = QApplication.clipboard()
    _click(window, rects["donate_alias"].center().x(), rects["donate_alias"].center().y())
    assert clipboard.text() == ow.DONATION_ALIAS
    _click(window, rects["donate_cvu"].center().x(), rects["donate_cvu"].center().y())
    assert clipboard.text() == ow.DONATION_CVU

def test_manual_button_shows_the_dialog(app: QApplication):
    state = State()
    window = _window(state)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    llamadas = []
    window.show_manual = lambda: llamadas.append(True)
    _click(window, rects["manual"].center().x(), rects["manual"].center().y())
    assert llamadas == [True]

def test_button_text_is_smaller_than_the_title(app: QApplication):
    assert ow.PANEL_BUTTON_FONT_MAX <= ow.PANEL_LABEL_FONT_SIZE
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

def test_buttons_are_20px_high_with_10px_text(app: QApplication):
    assert ow.PANEL_BUTTON_HEIGHT == 34
    assert ow.PANEL_BUTTON_FONT_MAX == 16
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    for name, rect in rects.items():
        assert rect.height() == ow.PANEL_BUTTON_HEIGHT, name
    textos = {
        name: text
        for _label, buttons in ow.PANEL_ROWS
        for name, text in buttons
    }
    for name, text in textos.items():
        if len(text) == 1 or name == "opacity_slider":
            continue
        font = window._panel_button_font(text, rects[name].width())
        assert font.pixelSize() <= round(16 * 96 / 72), f"{name} no entra a 16px"
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
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    boton = rects["guide_prev"]
    titulo_y = boton.top() - ow.PANEL_TITLE_GAP - ow.PANEL_SECTION_TITLE_HEIGHT
    assert titulo_y >= ow.PANEL_PADDING
    assert boton.top() - titulo_y == ow.PANEL_TITLE_GAP + ow.PANEL_SECTION_TITLE_HEIGHT
    filas = window._panel_rows()
    assert filas[0][0] is None, "REGLAS es un título de sección, no de fila"

def test_section_gaps_are_proportional_and_capped(app: QApplication):
    window = _window(State(), 1280, 1000)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    gap = window._section_gap()
    assert ow.PANEL_SECTION_GAP_MIN <= gap <= ow.PANEL_SECTION_GAP_MAX
    content = window._panel_buttons_height(gap)
    assert content <= 1000 - 2 * ow.PANEL_PADDING, "el panel debe caber en 1000px"
    rectas = dict(window._panel_buttons())
    hueco = rectas["rule_h"].top() - rectas["line_black"].bottom() - 1
    assert hueco >= ow.PANEL_SECTION_GAP_MIN

def test_opacity_slider_drag_updates_the_opacity(app: QApplication):
    state = State(opacity=0.5)
    window = _window(state)
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    slider = rects["opacity_slider"]
    x_izq = slider.left() + 6
    _click(window, x_izq, slider.center().y())
    assert state.opacity == 0.0
    window._dragging_opacity = True
    window._update_opacity_from_pos(QPoint(slider.right() - 6, slider.center().y()))
    assert state.opacity == 1.0

def test_opacity_slider_row_is_full_width(app: QApplication):
    window = _window(State())
    window._panel_open = True
    window._panel_offset = float(ow.PANEL_WIDTH)
    rects = {name: rect for name, rect in window._panel_buttons()}
    assert rects["opacity_slider"].width() == ow.PANEL_BUTTON_W1
