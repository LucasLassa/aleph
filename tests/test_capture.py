
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import datetime
from pathlib import Path

from PySide6.QtGui import QColor, QImage

from src.core import capture as capture_core
from src.core import guides
from src.core.state import Rule, State
from src.platform.capture import ScreenGrabber


class FakeGrabber(ScreenGrabber):

    def __init__(self, color=QColor(30, 40, 60), size=(320, 180)):
        self.color = color
        self.size = size
        self.calls = 0

    def grab(self):
        self.calls += 1
        img = QImage(self.size[0], self.size[1], QImage.Format.Format_ARGB32)
        img.fill(self.color)
        return img

def test_capture_filename_has_timestamp():
    moment = datetime.datetime(2026, 10, 20, 14, 30, 12)
    name = capture_core.capture_filename(moment)
    assert name == "aleph-20261020-143012.png"
    assert name.endswith(".png")

def test_capture_dir_defaults_to_downloads():
    state = State()
    assert state.capture_dir == ""
    assert capture_core.capture_dir(state) == capture_core.default_capture_dir()

def test_capture_dir_uses_configured_path(tmp_path):
    state = State(capture_dir=str(tmp_path))
    assert capture_core.capture_dir(state) == tmp_path

def test_capture_dir_is_persisted():
    state = State(capture_dir="/tmp/capturas")
    d = state.to_dict()
    assert d["capture_dir"] == "/tmp/capturas"
    assert State.from_dict(d).capture_dir == "/tmp/capturas"

def test_capture_saves_file_with_guides(tmp_path):
    state = State(capture_dir=str(tmp_path), guide_index=guides.POOL.index("Regla de tercios"))
    grabber = FakeGrabber()
    image, path = capture_core.capture_with_guides(grabber, state)
    assert path is not None and path.exists()
    assert path.suffix == ".png"
    assert image is not None
    assert grabber.calls == 1

def test_capture_has_guide_lines_over_the_photo(tmp_path):
    state = State(capture_dir=str(tmp_path), guide_index=guides.POOL.index("Regla de tercios"))
    grabber = FakeGrabber(color=QColor(0, 0, 0))
    image, path = capture_core.capture_with_guides(grabber, state)
    assert path is not None
    saved = QImage(str(path))
    blancos = sum(
        1
        for x in range(0, saved.width(), 2)
        for y in range(0, saved.height(), 2)
        if saved.pixelColor(x, y).red() > 200
    )
    assert blancos > 0, "la captura no tiene las líneas de la guía"

def test_capture_has_no_dark_veil(tmp_path):
    state = State(capture_dir=str(tmp_path), guide_index=guides.POOL.index("Centro"))
    base = QColor(100, 100, 100)
    grabber = FakeGrabber(color=base)
    image, path = capture_core.capture_with_guides(grabber, state)
    assert path is not None
    saved = QImage(str(path))
    corner = saved.pixelColor(2, 2)
    assert abs(corner.red() - base.red()) <= 2, "la foto tiene el velo oscuro encima"

def test_capture_includes_user_rules(tmp_path):
    state = State(capture_dir=str(tmp_path), guide_index=guides.POOL.index("Centro"))
    state.rules.append(Rule(kind="h", x=0.5, y=0.5))
    grabber = FakeGrabber(color=QColor(0, 0, 0))
    image, path = capture_core.capture_with_guides(grabber, state)
    assert path is not None
    saved = QImage(str(path))
    fila = saved.height() // 2
    blancos = sum(
        1 for x in range(saved.width()) if saved.pixelColor(x, fila).red() > 200
    )
    assert blancos > saved.width() // 2, "la regla horizontal del usuario no aparece"

def test_capture_returns_none_when_grab_fails(tmp_path):

    class FailingGrabber(ScreenGrabber):
        def grab(self):
            return None

    state = State(capture_dir=str(tmp_path))
    image, path = capture_core.capture_with_guides(FailingGrabber(), state)
    assert image is None and path is None
    assert list(Path(tmp_path).iterdir()) == []

def test_config_migrates_from_the_old_name(tmp_path, monkeypatch):
    from src.config import manager

    viejo = tmp_path / "overlay-composicion"
    viejo.mkdir()
    (viejo / "config.json").write_text('{"opacity": 0.42}', encoding="utf-8")
    nuevo = tmp_path / "aleph"
    monkeypatch.setattr(manager, "LEGACY_CONFIG_DIR", viejo)
    monkeypatch.setattr(manager, "CONFIG_DIR", nuevo)
    monkeypatch.setattr(manager, "CONFIG_PATH", nuevo / "config.json")

    assert manager.migrate_legacy() is True
    assert (nuevo / "config.json").exists()
    assert manager.load()["opacity"] == 0.42

def test_config_migration_does_not_overwrite_the_new_one(tmp_path, monkeypatch):
    from src.config import manager

    viejo = tmp_path / "overlay-composicion"
    viejo.mkdir()
    (viejo / "config.json").write_text('{"opacity": 0.42}', encoding="utf-8")
    nuevo = tmp_path / "aleph"
    nuevo.mkdir()
    (nuevo / "config.json").write_text('{"opacity": 0.9}', encoding="utf-8")
    monkeypatch.setattr(manager, "LEGACY_CONFIG_DIR", viejo)
    monkeypatch.setattr(manager, "CONFIG_DIR", nuevo)
    monkeypatch.setattr(manager, "CONFIG_PATH", nuevo / "config.json")

    assert manager.migrate_legacy() is False
    assert manager.load()["opacity"] == 0.9
