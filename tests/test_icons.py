
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

from src.platform import desktop
from src.ui import icons


def test_icon_path_exists_in_source_tree():
    path = icons.icon_path()
    assert path.exists(), f"el ícono no está en {path}"
    assert path.name == "icon.png"

def test_icon_path_uses_mepass_when_frozen(monkeypatch, tmp_path):
    meipass = tmp_path / "MEI"
    (meipass / "resources").mkdir(parents=True)
    (meipass / "resources" / "icon.png").write_bytes(b"x")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    assert icons.icon_path() == meipass / "resources" / "icon.png"

def test_icon_path_falls_back_to_package(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    expected = Path(icons.__file__).resolve().parent.parent / "resources" / "icon.png"
    assert icons.icon_path() == expected

def test_window_icon_is_not_null():
    assert not icons.window_icon().isNull()

def test_font_exists_in_source_tree():
    path = icons.resource_path("Orange Kid.otf")
    assert path.exists(), f"la fuente no está en {path}"
    assert path.name == "Orange Kid.otf"

def test_font_path_uses_mepass_when_frozen(monkeypatch, tmp_path):
    meipass = tmp_path / "MEI"
    (meipass / "resources").mkdir(parents=True)
    (meipass / "resources" / "Orange Kid.otf").write_bytes(b"x")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    assert icons.resource_path("Orange Kid.otf") == meipass / "resources" / "Orange Kid.otf"

def test_panel_font_is_the_bundled_one():
    from PySide6.QtGui import QFontDatabase

    from src.ui import overlay_window as ow

    ow._FONT_LOADED = False
    ow._ensure_custom_font()
    assert ow.resource_path(ow.ORANGE_KID_FILENAME).exists()
    assert "Orange Kid" in QFontDatabase.families()

def test_package_data_includes_icon():
    import tomllib

    root = Path(__file__).resolve().parent.parent
    with open(root / "pyproject.toml", "rb") as fh:
        cfg = tomllib.load(fh)
    assert cfg["tool"]["setuptools"]["package-data"]["src"] == [
        "resources/*.png",
        "resources/*.otf",
    ]

def test_desktop_entry_content():
    entry = desktop.DESKTOP_ENTRY.format(
        title=desktop.APP_TITLE, exec_line="'/bin/true'", icon="aleph"
    )
    assert "[Desktop Entry]" in entry
    assert "Type=Application" in entry
    assert "Exec='/bin/true'" in entry
    assert "Icon=aleph" in entry
    assert "Terminal=false" in entry

def test_write_if_changed_is_idempotent(tmp_path):
    target = tmp_path / "sub" / "file.desktop"
    assert desktop._write_if_changed(target, "a") is True
    assert desktop._write_if_changed(target, "a") is False
    assert desktop._write_if_changed(target, "b") is True
    assert target.read_text() == "b"

def test_exec_line_quotes_path(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", "/opt/My Apps/overlay.exe")
    assert desktop._exec_line() == '"/opt/My Apps/overlay.exe"'

def test_install_desktop_never_raises(monkeypatch):

    def boom():
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(desktop, "_install_linux_desktop", boom)
    monkeypatch.setattr(sys, "platform", "linux")
    desktop.install_desktop_shortcut()
