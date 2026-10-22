
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.ui import icons
from src.utils.logger import get_logger

log = get_logger(__name__)

APP_TITLE = "Aleph"
DESKTOP_ID = "aleph"
ICON_SIZE = 512

DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name={title}
Comment=Guías de composición sobre cualquier contenido multimedia
Exec={exec_line}
Icon={icon}
Terminal=false
Categories=Graphics;Video;Utility;
"""


def _write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def _exec_line() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    script = shutil.which(DESKTOP_ID)
    if script:
        return f'"{script}"'
    return f'"{sys.executable}" -m src.main'

_CLSID_SHELL_LINK = "{00021401-0000-0000-C000-000000000046}"
_IID_SHELL_LINK_W = "{000214F9-0000-0000-C000-000000000046}"
_IID_PERSIST_FILE = "{0000010B-0000-0000-C000-000000000046}"

_VT_SET_DESCRIPTION = 7
_VT_SET_ICON_LOCATION = 17
_VT_SET_PATH = 20
_VT_SAVE = 3


class _GUID(ctypes.Structure):

    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_ubyte * 8),
    ]

def _guid(text: str) -> _GUID:
    guid = _GUID()
    ctypes.windll.ole32.CLSIDFromString(ctypes.c_wchar_p(text), ctypes.byref(guid))
    return guid

def _vtable(obj: int, index: int):
    vtbl = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return vtbl[index]

def _windows_desktop_dir() -> Path:
    try:
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf) == 0:
            return Path(buf.value)
    except Exception:
        pass
    return Path.home() / "Desktop"

def _create_windows_shortcut(link: Path, target: str, icon: str, description: str) -> None:
    ole32 = ctypes.windll.ole32

    ole32.CoInitializeEx.restype = ctypes.c_long
    ole32.CoInitializeEx(ctypes.c_void_p(None), 2)

    ole32.CoCreateInstance.restype = ctypes.c_long
    ole32.CoCreateInstance.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    shell_link = ctypes.c_void_p()
    hr = ole32.CoCreateInstance(
        ctypes.byref(_guid(_CLSID_SHELL_LINK)),
        None,
        1,
        ctypes.byref(_guid(_IID_SHELL_LINK_W)),
        ctypes.byref(shell_link),
    )
    if hr != 0 or not shell_link.value:
        raise OSError(f"CoCreateInstance(IShellLinkW) falló: 0x{hr:08x}")

    set_path = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_wchar_p)(
        _vtable(shell_link.value, _VT_SET_PATH)
    )
    set_icon = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int
    )(_vtable(shell_link.value, _VT_SET_ICON_LOCATION))
    set_desc = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_wchar_p)(
        _vtable(shell_link.value, _VT_SET_DESCRIPTION)
    )

    set_path(shell_link, target)
    set_icon(shell_link, icon, 0)
    set_desc(shell_link, description)

    query_interface = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    )(_vtable(shell_link.value, 0))
    persist = ctypes.c_void_p()
    query_interface(
        shell_link,
        ctypes.byref(_guid(_IID_PERSIST_FILE)),
        ctypes.byref(persist),
    )
    if not persist.value:
        raise OSError("QueryInterface(IPersistFile) devolvió NULL")

    save = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_wchar_p)(
        _vtable(persist.value, _VT_SAVE)
    )
    hr = save(persist, str(link))
    if hr != 0:
        raise OSError(f"IPersistFile::Save falló: 0x{hr:08x}")

def _windows_icon_file() -> str:
    from PySide6.QtGui import QIcon

    ico_dir = Path.home() / ".config" / DESKTOP_ID
    ico_dir.mkdir(parents=True, exist_ok=True)
    ico = ico_dir / "icon.ico"
    if not ico.exists():
        QIcon(str(icons.icon_path())).pixmap(256, 256).save(str(ico), "ICO")
    return str(ico)

def _install_windows_desktop() -> None:
    link = _windows_desktop_dir() / f"{DESKTOP_ID}.lnk"
    frozen = getattr(sys, "frozen", False)
    target = sys.executable if frozen else _exec_line().strip('"')
    icon = f"{sys.executable},0" if frozen else _windows_icon_file()
    _create_windows_shortcut(link, target, icon, "Guías de composición sobre cualquier video")
    log.info("acceso directo de escritorio creado: %s", link)

def _linux_desktop_dir() -> Path:
    try:
        out = subprocess.run(
            ["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, timeout=5
        ).stdout.strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return Path.home() / "Desktop"

def _install_linux_icon() -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    icons_dir = data_home / "icons" / "hicolor" / f"{ICON_SIZE}x{ICON_SIZE}" / "apps"
    icons_dir.mkdir(parents=True, exist_ok=True)
    dest = icons_dir / f"{DESKTOP_ID}.png"
    src = icons.icon_path()
    if src.exists() and (not dest.exists() or dest.read_bytes() != src.read_bytes()):
        shutil.copyfile(src, dest)
        subprocess.run(
            ["gtk-update-icon-cache", "-f", "-t", str(data_home / "icons" / "hicolor")],
            capture_output=True,
            timeout=30,
            check=False,
        )
        log.info("ícono instalado en el theme: %s", dest)
    return dest

def _install_linux_desktop() -> None:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    exec_line = _exec_line()

    apps_entry = data_home / "applications" / f"{DESKTOP_ID}.desktop"
    _write_if_changed(
        apps_entry, DESKTOP_ENTRY.format(title=APP_TITLE, exec_line=exec_line, icon=DESKTOP_ID)
    )

    dest_icon = _install_linux_icon()
    desktop_entry = _linux_desktop_dir() / f"{DESKTOP_ID}.desktop"
    if _write_if_changed(
        desktop_entry,
        DESKTOP_ENTRY.format(title=APP_TITLE, exec_line=exec_line, icon=str(dest_icon)),
    ):
        try:
            desktop_entry.chmod(0o755)
            subprocess.run(
                ["gio", "set", str(desktop_entry), "metadata::trusted", "true"],
                capture_output=True,
                timeout=10,
                check=False,
            )
        except Exception:
            pass
    log.info("acceso directo de escritorio creado: %s", desktop_entry)

def install_desktop_shortcut() -> None:
    try:
        if sys.platform == "win32":
            _install_windows_desktop()
        elif sys.platform.startswith("linux"):
            _install_linux_desktop()
    except Exception as exc:
        log.warning("no se pudo crear el acceso directo de escritorio: %s", exc)
