# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para RunDesk.
Genera un ejecutable único (.exe) con todos los recursos bundled.

Uso:
    pyinstaller rundesk.spec
"""

import sys
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / "app" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Icono de la app (usado en sidebar y about)
        (str(ROOT / "assets" / "icon.png"), "assets"),
        (str(ROOT / "assets" / "icon.ico"), "assets"),
        # Sonidos de feedback (si existen)
        (str(ROOT / "app" / "core" / "sounds" / "assets"), "app/core/sounds/assets"),
    ],
    hiddenimports=[
        "app.main",
        "app.bootstrap",
        "app.i18n",
        "app.i18n.translator",
        "app.i18n.catalog_es",
        "app.i18n.catalog_en",
        "app.core.config.config_store",
        "app.core.config.schemas",
        "app.core.config.migrations",
        "app.core.commands.command_store",
        "app.core.scenes.scene_store",
        "app.core.hotkey.hotkey_manager",
        "app.core.input.alias_resolver",
        "app.core.input.command_parser",
        "app.core.input.fuzzy_matcher",
        "app.core.actions.action_executor",
        "app.core.actions.command_router",
        "app.core.sounds.sound_player",
        "app.core.app_state",
        "app.core.log_capture",
        "app.ui.shell",
        "app.ui.styles",
        "app.ui.pages.dashboard_page",
        "app.ui.pages.commands_page",
        "app.ui.pages.scenes_page",
        "app.ui.pages.launcher_settings_page",
        "app.ui.pages.appearance_page",
        "app.ui.pages.languages_page",
        "app.ui.pages.tutorials_page",
        "app.ui.pages.diagnostics_page",
        "app.ui.pages.about_page",
        "app.ui.overlay.input_overlay",
        "keyboard",
        "rapidfuzz",
        "screeninfo",
        "win32api",
        "win32gui",
        "win32con",
        "win32process",
        "pywintypes",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "unittest",
        "email",
        "html",
        "http",
        "xml",
        "xmlrpc",
        "pydoc",
        "doctest",
        "test",
        "multiprocessing",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="RunDesk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "icon.ico"),
    version_file=None,
)
