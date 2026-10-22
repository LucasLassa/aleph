
from src.config.defaults import DEFAULTS
from src.core.state import Rule, State
from src.utils import geometry


def test_state_roundtrip():
    s = State(opacity=0.4)
    d = s.to_dict()
    s2 = State.from_dict(d)
    assert s2.opacity == 0.4

def test_from_dict_ignores_unknown_keys():
    s = State.from_dict({"opacity": 0.5, "clave_inventada": 123})
    assert s.opacity == 0.5

def test_guide_index_not_persisted():
    s = State(guide_index=5, opacity=0.4)
    d = s.to_dict()
    assert "guide_index" not in d
    assert set(d) <= set(DEFAULTS)

def test_from_dict_ignores_legacy_guide_index():
    from src.core import guides

    s = State.from_dict({"guide_index": 3, "opacity": 0.5})
    assert s.guide_index == guides.POOL.index("Regla de tercios")
    assert s.opacity == 0.5

def test_defaults_cover_state_fields():
    assert set(State().to_dict()) <= set(DEFAULTS)

def test_line_dark_is_persisted():
    s = State(line_dark=True, opacity=0.4)
    d = s.to_dict()
    assert d["line_dark"] is True
    s2 = State.from_dict(d)
    assert s2.line_dark is True
    assert s2.opacity == 0.4

def test_fullscreen_and_rules_are_not_persisted():
    s = State(fullscreen=False, rules=[Rule(kind="h", x=0.5, y=0.5)])
    d = s.to_dict()
    assert "fullscreen" not in d
    assert "rules" not in d
    s2 = State.from_dict(d)
    assert s2.fullscreen is True
    assert s2.rules == []

def test_frame_mode_not_persisted():
    s = State(frame_mode=False, click_through=True)
    d = s.to_dict()
    assert "frame_mode" not in d
    assert "click_through" not in d
    assert set(d) <= set(DEFAULTS)

def test_from_dict_ignores_legacy_frame_mode():
    s = State.from_dict({"guide_index": 3, "frame_mode": False, "click_through": True})
    assert s.frame_mode is True
    assert s.click_through is False

def test_foot_of_perpendicular():
    fx, fy = geometry.foot_of_perpendicular(50, 10, 0, 0, 100, 0)
    assert abs(fx - 50) < 1e-9
    assert abs(fy - 0) < 1e-9

def test_fibonacci_radii_are_exact():
    radii = geometry.FIBONACCI_RADII
    assert radii == (21, 13, 8, 5, 3, 2, 1, 1)
    for i in range(len(radii) - 2):
        assert radii[i] == radii[i + 1] + radii[i + 2]

def test_fibonacci_spiral_is_continuous():
    pts = geometry.fibonacci_spiral_points(1920, 1080, 0)
    assert len(pts) > 100
    for i in range(1, len(pts)):
        jump = ((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][1] - pts[i - 1][1]) ** 2) ** 0.5
        assert jump < 60, f"corte en el punto {i}: salto de {jump:.1f}px"

def test_fibonacci_spiral_fits_frame():
    for corner in range(4):
        pts = geometry.fibonacci_spiral_points(1920, 1080, corner)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert min(xs) >= -1 and max(xs) <= 1921, f"esquina {corner} se sale en X"
        assert min(ys) >= -1 and max(ys) <= 1081, f"esquina {corner} se sale en Y"

def test_fibonacci_spiral_corners_differ():
    shapes = []
    for corner in range(4):
        pts = geometry.fibonacci_spiral_points(1920, 1080, corner)
        shapes.append(tuple(pts[0]))
    assert len(set(shapes)) == 4

def test_fibonacci_spiral_fills_frame_equally():
    areas = []
    for corner in range(4):
        pts = geometry.fibonacci_spiral_points(1920, 1080, corner)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        areas.append((max(xs) - min(xs), max(ys) - min(ys)))
    assert len(set(areas)) == 1, f"las 4 esquinas difieren en tamaño: {areas}"

def test_fibonacci_spiral_scales_to_any_aspect():
    for w, h in [(1920, 1080), (1440, 1080), (2560, 1080), (1080, 1080), (1080, 1920)]:
        for corner in range(4):
            pts = geometry.fibonacci_spiral_points(w, h, corner)
            assert len(pts) > 100
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            assert min(xs) >= -1 and max(xs) <= w + 1
            assert min(ys) >= -1 and max(ys) <= h + 1
