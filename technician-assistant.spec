import importlib.util

from PyInstaller.utils.hooks import collect_all

if importlib.util.find_spec("PySide6.QtWebEngineWidgets"):
    webengine_data, webengine_binaries, webengine_hidden = collect_all(
        "PySide6.QtWebEngineWidgets"
    )
else:
    webengine_data, webengine_binaries, webengine_hidden = [], [], []

analysis = Analysis(
    ["app.py"],
    pathex=["src"],
    binaries=webengine_binaries,
    datas=webengine_data,
    hiddenimports=webengine_hidden + ["keyring.backends.Windows"],
)
pyz = PYZ(analysis.pure)
executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="TechnicianVoiceAssistant",
    console=False,
)
