
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.core import guides
from src.core.state import State


def _app():
    import sys

    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication(sys.argv)

def _render(index, w=200, h=120):
    from PySide6.QtGui import QColor, QImage, QPainter

    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0))
    p = QPainter(img)
    guides.draw(p, w, h, State(guide_index=index))
    p.end()
    return img

def _has_white(img):
    return any(
        img.pixelColor(x, y).red() > 200 for x in range(img.width()) for y in range(img.height())
    )

def test_pool_has_11_unique_names():
    assert len(guides.POOL) == 11
    assert len(set(guides.POOL)) == 11
    assert all(name.strip() for name in guides.POOL)

def test_pool_names_match_expected():
    expected = [
        "Espacio vacío",
        "Regla de tercios",
        "Triángulo áureo (sup-izq)",
        "Triángulo áureo (sup-der)",
        "Espiral Fibonacci (inf-izq)",
        "Espiral Fibonacci (sup-izq)",
        "Espiral Fibonacci (sup-der)",
        "Espiral Fibonacci (inf-der)",
        "Centro",
        "Diagonales",
        "Rejilla áurea (Phi Grid)",
    ]
    assert guides.POOL == expected

def test_pool_has_eleven_guides():
    assert len(guides.POOL) == 11

def test_default_guide_is_thirds():
    assert State().guide_index == guides.POOL.index("Regla de tercios")
    assert State().guide_index != guides.EMPTY_INDEX

def test_fibonacci_guides_are_contiguous():
    for i in range(guides.FIBONACCI_COUNT):
        assert "Fibonacci" in guides.POOL[guides.FIBONACCI_FIRST + i]

def test_fibonacci_corners_match_their_labels():
    from src.utils import geometry

    w, h = 400, 300
    for i in range(guides.FIBONACCI_COUNT):
        nombre = guides.POOL[guides.FIBONACCI_FIRST + i]
        corner = guides.FIBONACCI_CORNERS[i]
        pts = geometry.fibonacci_spiral_points(w, h, corner)
        grande = pts[:81]
        cx = sum(p[0] for p in grande) / len(grande)
        cy = sum(p[1] for p in grande) / len(grande)
        vertical = "inf" if cy > h / 2 else "sup"
        horizontal = "izq" if cx < w / 2 else "der"
        assert f"({vertical}-{horizontal})" in nombre, (
            f"la guía {nombre} se dibuja en {vertical}-{horizontal}"
        )

def test_two_golden_triangle_variants():

    w, h = 200, 120
    img = _render(guides.GOLDEN_TRIANGLE_FIRST, w, h)
    medio = img.pixelColor(w // 2, h // 2)
    assert medio.red() > 200, "la diagonal del primer triángulo no pasa por el centro"

    img2 = _render(guides.GOLDEN_TRIANGLE_FIRST + 1, w, h)
    medio2 = img2.pixelColor(w // 2, h // 2)
    assert medio2.red() > 200, "la diagonal del segundo triángulo no pasa por el centro"

    arriba_izq = img.pixelColor(w // 4, h // 4)
    arriba_izq2 = img2.pixelColor(w // 4, h // 4)
    assert (arriba_izq.red() > 200) != (arriba_izq2.red() > 200), (
        "las dos diagonales deberían ser distintas"
    )

def test_draw_handles_all_indices():
    import sys

    from PySide6.QtGui import QPainter, QPixmap
    from PySide6.QtWidgets import QApplication

    QApplication.instance() or QApplication(sys.argv)
    pm = QPixmap(200, 120)
    pm.fill()
    p = QPainter(pm)
    for idx in range(-1, 11):
        s = State(guide_index=idx)
        guides.draw(p, 200, 120, s)
    p.end()

def test_empty_guide_draws_nothing():
    _app()
    img = _render(guides.EMPTY_INDEX)
    assert not _has_white(img), "la guía 'Espacio vacío' no debería dibujar nada"

def test_other_guides_do_draw():
    _app()
    for idx in range(len(guides.POOL)):
        if idx == guides.EMPTY_INDEX:
            continue
        img = _render(idx)
        assert _has_white(img), f"la guía {idx} debería dibujar algo"
