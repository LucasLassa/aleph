import os
import sys
import tomllib

name = "aleph"
entry = os.path.join(SPECPATH, "src", "main.py")
icon_png = os.path.join(SPECPATH, "src", "resources", "icon.png")
font_otf = os.path.join(SPECPATH, "src", "resources", "Orange Kid.otf")
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
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_png if sys.platform == "win32" else None,
    )
