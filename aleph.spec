# -*- mode: python ; coding: utf-8 -*-
# La class de la ventana sale del nombre del binario: las reglas de
# Hyprland matchean por class:^(aleph)$.
# Spec de PyInstaller para aleph.
#
# Build:  pyinstaller aleph.spec
# Salida:
#   - Linux/Windows: dist/aleph(.exe)                   [onefile]
#   - macOS:         dist/aleph.app                      [onedir + bundle]
#
# El nombre del binario debe ser "aleph": en Wayland/Hyprland
# la class de la ventana se deriva del nombre del binario y las window rules
# del README (pin, no_blur) matchean por class:^(aleph)$.

import os
import sys
import tomllib

name = "aleph"

# SPECPATH = ruta absoluta de esta spec (la raíz del repo). Se usa para que
# el build no dependa del cwd: entry y pathex son absolutos y el paquete
# "src" (namespace package, sin __init__.py en su raíz) siempre se encuentra.
# pathex vacío solo funcionaba porque el cwd era el repo root: accidental.
entry = os.path.join(SPECPATH, "src", "main.py")

# Ícono maestro. En Windows EXE(icon=) lo convierte a .ico y en macOS
# BUNDLE(icon=) a .icns (ambos con Pillow, que va en las deps de dev).
# En Linux PyInstaller ignora el icono del binario: allá el ícono de la app
# sale del .desktop + theme de iconos (lo instala src/platform/desktop.py).
icon_png = os.path.join(SPECPATH, "src", "resources", "icon.png")

# La fuente del panel viaja como dato: si no, el binario depende de que
# la tenga instalada el sistema (en Windows no existe).
font_otf = os.path.join(SPECPATH, "src", "resources", "Orange Kid.otf")

# El PNG viaja como dato para que la app lo encuentre en runtime
# (ver src/ui/icons.py: sys._MEIPASS/resources/icon.png).
datas = [(icon_png, "resources"), (font_otf, "resources")]

with open(os.path.join(SPECPATH, "pyproject.toml"), "rb") as fh:
    version = tomllib.load(fh)["project"]["version"]

a = Analysis(
    [entry],
    pathex=[SPECPATH],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

if sys.platform == "darwin":
    # macOS: bundle .app (onedir). Onefile + bundle está deprecado en
    # PyInstaller ("will become an error in v7.0") porque un .app no puede
    # ser un archivo único.
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name=name,
    )
    app = BUNDLE(
        coll,
        name=f"{name}.app",
        icon=icon_png,
        bundle_identifier="com.lucas.aleph",
        version=version,
        info_plist={
            "CFBundleName": "Aleph",
            "NSHighResolutionCapable": True,
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,  # --windowed: sin consola (en Windows mata la terminal)
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_png if sys.platform == "win32" else None,
    )
