from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).parent
streamlit_datas, streamlit_binaries, streamlit_hidden = collect_all("streamlit")
datas = streamlit_datas + copy_metadata("streamlit") + [
    (str(ROOT / "app"), "app"),
    (str(ROOT / "README.md"), "."),
    (str(ROOT / "LICENSE"), "."),
]
hiddenimports = streamlit_hidden + collect_submodules("commlab")

a = Analysis(
    [str(ROOT / "desktop" / "launcher.py")],
    pathex=[str(ROOT), str(ROOT / "src")],
    binaries=streamlit_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CommLab",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="CommLab",
)
