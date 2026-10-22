
from __future__ import annotations

import math

FIBONACCI_RADII: tuple[int, ...] = (21, 13, 8, 5, 3, 2, 1, 1)

_CORNER_NAMES: tuple[str, ...] = ("inf-izq", "inf-der", "sup-izq", "sup-der")


def _fibonacci_spiral_local() -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    cx, cy = 0.0, 0.0
    theta = math.pi
    for i, radius in enumerate(FIBONACCI_RADII):
        next_radius = FIBONACCI_RADII[i + 1] if i + 1 < len(FIBONACCI_RADII) else 0
        end_theta = theta - math.pi / 2
        for k in range(80):
            t = theta + (end_theta - theta) * k / 79
            pts.append((cx + radius * math.cos(t), cy + radius * math.sin(t)))
        step = radius - next_radius
        cx += step * math.cos(end_theta)
        cy += step * math.sin(end_theta)
        theta = end_theta
    return pts

def _transform(points: list[tuple[float, float]], corner: int) -> list[tuple[float, float]]:
    if corner == 1:
        return [(-x, y) for x, y in points]
    if corner == 2:
        return [(x, -y) for x, y in points]
    if corner == 3:
        return [(-x, -y) for x, y in points]
    return points

def fibonacci_spiral_points(
    width: float, height: float, corner: int = 0
) -> list[tuple[float, float]]:
    local = _transform(_fibonacci_spiral_local(), corner)
    xs = [p[0] for p in local]
    ys = [p[1] for p in local]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    scale = min(width / (max_x - min_x), height / (max_y - min_y))
    if corner in (0, 2):
        offset_x = -min_x * scale
    else:
        offset_x = width - max_x * scale
    if corner in (0, 1):
        offset_y = height - max_y * scale
    else:
        offset_y = -min_y * scale
    return [(x * scale + offset_x, y * scale + offset_y) for x, y in local]

def foot_of_perpendicular(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> tuple[float, float]:
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    return ax + t * dx, ay + t * dy
