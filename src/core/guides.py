"""Guías de composición.

Propósito:
Dibujo de las 11 guías de composición sobre un QPainter: tercios, centro,
diagonales, espiral de Fibonacci, triángulo áureo (dos variantes), rejilla
áurea (Phi Grid) y vacía.
Funciones: draw(), draw_thirds(), draw_center(), draw_diagonals(),
draw_fibonacci(), draw_golden_triangle(), draw_phi_grid()
Constantes: POOL, FIBONACCI_*, EMPTY_INDEX, GOLDEN_TRIANGLE_*, CENTER_INDEX,
DIAGONALS_INDEX, PHI, PHI_SMALL, PHI_LARGE, PHI_GRID_INDEX
"""

from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from src.core.state import State
from src.utils import geometry

PHI = 1.618033988749895
PHI_SMALL = 1.0 / (1.0 + PHI)  # ≈ 0.381966
PHI_LARGE = PHI / (1.0 + PHI)  # ≈ 0.618034


def _line(painter: QPainter, x1: float, y1: float, x2: float, y2: float, color: QColor) -> None:
    painter.setPen(QPen(QColor(0, 0, 0, 160), 3.0))
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    painter.setPen(QPen(color, 1.5))
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

def draw(
    painter: QPainter,
    width: int,
    height: int,
    state: State,
    color: QColor | None = None,
) -> None:
    if color is None:
        color = QColor(0, 0, 0) if state.line_dark else QColor(255, 255, 255)
    index = state.guide_index
    if index == EMPTY_INDEX:
        return
    if index == 1:
        draw_thirds(painter, width, height, color)
    elif GOLDEN_TRIANGLE_FIRST <= index < GOLDEN_TRIANGLE_FIRST + GOLDEN_TRIANGLE_COUNT:
        draw_golden_triangle(
            painter, width, height, color, corner=index - GOLDEN_TRIANGLE_FIRST
        )
    elif FIBONACCI_FIRST <= index < FIBONACCI_FIRST + FIBONACCI_COUNT:
        draw_fibonacci(
            painter,
            width,
            height,
            color,
            corner=FIBONACCI_CORNERS[index - FIBONACCI_FIRST],
        )
    elif index == CENTER_INDEX:
        draw_center(painter, width, height, color)
    elif index == DIAGONALS_INDEX:
        draw_diagonals(painter, width, height, color)
    elif index == PHI_GRID_INDEX:
        draw_phi_grid(painter, width, height, color)

def draw_thirds(painter: QPainter, width: int, height: int, color: QColor) -> None:
    _line(painter, width / 3, 0, width / 3, height, color)
    _line(painter, 2 * width / 3, 0, 2 * width / 3, height, color)
    _line(painter, 0, height / 3, width, height / 3, color)
    _line(painter, 0, 2 * height / 3, width, 2 * height / 3, color)

def draw_center(painter: QPainter, width: int, height: int, color: QColor) -> None:
    _line(painter, width / 2, 0, width / 2, height, color)
    _line(painter, 0, height / 2, width, height / 2, color)

def draw_diagonals(painter: QPainter, width: int, height: int, color: QColor) -> None:
    _line(painter, 0, 0, width, height, color)
    _line(painter, width, 0, 0, height, color)

def draw_phi_grid(painter: QPainter, width: int, height: int, color: QColor) -> None:
    """Rejilla Áurea / Phi Grid: divide el lienzo en 1:0.618:1."""
    _line(painter, width * PHI_SMALL, 0, width * PHI_SMALL, height, color)
    _line(painter, width * PHI_LARGE, 0, width * PHI_LARGE, height, color)
    _line(painter, 0, height * PHI_SMALL, width, height * PHI_SMALL, color)
    _line(painter, 0, height * PHI_LARGE, width, height * PHI_LARGE, color)

def draw_fibonacci(
    painter: QPainter,
    width: int,
    height: int,
    color: QColor,
    corner: int = 0,
) -> None:
    poly = [QPointF(x, y) for x, y in geometry.fibonacci_spiral_points(width, height, corner)]
    if len(poly) < 2:
        return
    painter.setPen(QPen(QColor(0, 0, 0, 160), 3.0))
    painter.drawPolyline(poly)
    painter.setPen(QPen(color, 1.5))
    painter.drawPolyline(poly)

def draw_golden_triangle(
    painter: QPainter, width: int, height: int, color: QColor, corner: int = 0
) -> None:
    if corner == 0:
        ax, ay = 0.0, 0.0
        bx, by = float(width), float(height)
        others = ((float(width), 0.0), (0.0, float(height)))
    else:
        ax, ay = float(width), 0.0
        bx, by = 0.0, float(height)
        others = ((0.0, 0.0), (float(width), float(height)))
    _line(painter, ax, ay, bx, by, color)
    for px, py in others:
        fx, fy = geometry.foot_of_perpendicular(px, py, ax, ay, bx, by)
        _line(painter, px, py, fx, fy, color)
        painter.setPen(QPen(QColor(0, 0, 0, 200), 4.0))
        painter.drawPoint(QPointF(fx, fy))
        painter.setPen(QPen(color, 2.5))
        painter.drawPoint(QPointF(fx, fy))

POOL: list[str] = [
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

FIBONACCI_FIRST = 4
FIBONACCI_COUNT = 4

FIBONACCI_CORNERS: tuple[int, ...] = (0, 2, 3, 1)

EMPTY_INDEX = 0

GOLDEN_TRIANGLE_FIRST = 2
GOLDEN_TRIANGLE_COUNT = 2

CENTER_INDEX = 8
DIAGONALS_INDEX = 9

PHI_GRID_INDEX = 10
