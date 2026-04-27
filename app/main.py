"""
Punto de entrada principal de RunDesk.
"""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QMenu,
    QMessageBox,
    QSpinBox,
    QSystemTrayIcon,
)

from app.bootstrap import AppBootstrap
from app.core.actions.action_executor import ActionExecutor
from app.core.actions.command_router import CommandRouter
from app.core.input.alias_resolver import AliasResolver
from app.core.input.command_parser import CommandParser
from app.core.input.fuzzy_matcher import FuzzyMatcher
from app.i18n import set_language, t
from app.ui.overlay.input_overlay import InputOverlay
from app.ui.shell import AppShell
from app.ui.styles import Fonts

logger = logging.getLogger(__name__)


def _setup_logging():
    """Configura logging básico para la aplicación."""
    from app.core.log_capture import get_handler

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt="%H:%M:%S",
    )
    # Agregar captura en memoria para el visor de diagnóstico
    capture = get_handler()
    capture.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    logging.getLogger().addHandler(capture)


class RunDeskApplication(QApplication):
    """QApplication personalizada que bloquea scroll wheel en combos/spinboxes sin foco."""

    def notify(self, obj, event):
        if (
            event.type() == QEvent.Type.Wheel
            and isinstance(obj, (QComboBox, QSpinBox))
            and not obj.hasFocus()
        ):
            return True
        return super().notify(obj, event)


def _set_language(lang: str, config):
    """Cambia el idioma de la UI en la configuración."""
    set_language(lang)
    config.set("ui_language", lang)
    config.save()
    logger.info("Idioma cambiado a: %s", lang)


def main():
    """Arranca la aplicación."""
    _setup_logging()

    start_minimized = "--minimized" in sys.argv

    app = RunDeskApplication(sys.argv)

    # Fuente global
    default_font = QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
    app.setFont(default_font)

    # Inicializar servicios
    bootstrap = AppBootstrap()
    bootstrap.initialize()

    # Configurar idioma desde config
    config = bootstrap.get_config()
    set_language(config.get("ui_language", "es"))

    # Sincronizar inicio con Windows según config
    from app.core.startup_manager import sync_startup
    sync_startup(config.get("start_with_windows", True))

    # Construir parser de comandos
    fuzzy_cfg = config.get("fuzzy_matching", {})
    fuzzy_enabled = fuzzy_cfg.get("enabled", True)
    fuzzy_threshold = fuzzy_cfg.get("threshold", 0.65)

    alias_resolver = AliasResolver()
    alias_resolver.build_index(
        commands=bootstrap.get_commands().get_enabled(),
        scenes=bootstrap.get_scenes().get_enabled(),
    )
    bootstrap.alias_resolver = alias_resolver

    fuzzy_matcher = FuzzyMatcher(threshold=fuzzy_threshold if fuzzy_enabled else 1.0)
    parser = CommandParser(alias_resolver, fuzzy_matcher)

    # Crear executor y router
    executor = ActionExecutor()
    router = CommandRouter(parser, executor)

    # Confirmación para acciones críticas
    def _confirm_critical(cmd_name: str) -> bool:
        reply = QMessageBox.warning(
            None,
            t("general.confirm_action"),
            t("general.confirm_critical").replace("{name}", cmd_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    router.set_confirm_callback(_confirm_critical)

    # Crear overlay del launcher con parser y config conectados
    overlay = InputOverlay()
    overlay.set_parser(parser)
    overlay.set_config(config)

    # Conectar hotkey global → toggle overlay
    hotkey_mgr = bootstrap.get_hotkey_manager()
    hotkey_mgr.hotkey_triggered.connect(overlay.toggle)
    hotkey_mgr.start()

    # Icono de la app
    icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
    app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

    # Lanzar ventana principal
    window = AppShell(bootstrap=bootstrap)
    window.setWindowIcon(app_icon)
    if not start_minimized:
        window.show()

    # --- System tray (bandeja del sistema) ---
    tray = QSystemTrayIcon(app_icon, app)
    tray.setToolTip("RunDesk")

    tray_menu = QMenu()
    tray_menu.setStyleSheet("""
        QMenu {
            font-size: 12px;
            padding: 4px 0;
        }
        QMenu::item {
            padding: 4px 24px 4px 12px;
        }
    """)
    action_open = tray_menu.addAction(t("tray.open"))
    tray_menu.addSeparator()
    action_quit = tray_menu.addAction(t("tray.quit"))

    action_open.triggered.connect(window.show_from_tray)
    action_quit.triggered.connect(lambda: (window.quit_app(), app.quit()))
    tray.setContextMenu(tray_menu)

    # Click izquierdo en el icono → mostrar menú contextual
    def _on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            tray_menu.popup(tray.geometry().center())

    tray.activated.connect(_on_tray_activated)
    tray.show()

    # No cerrar la app cuando se cierran todas las ventanas
    app.setQuitOnLastWindowClosed(False)

    # Registrar acciones internas del launcher (después de crear window)
    executor.register_launcher_action(
        "open_panel", lambda: window.show_from_tray()
    )
    executor.register_launcher_action("pause_launcher", hotkey_mgr.pause)
    executor.register_launcher_action("resume_launcher", hotkey_mgr.resume)
    executor.register_launcher_action(
        "lang_es", lambda: _set_language("es", config)
    )
    executor.register_launcher_action(
        "lang_en", lambda: _set_language("en", config)
    )

    sound_player = bootstrap.get_sound_player()

    app_state = bootstrap.get_app_state()

    def _on_command_submitted(text: str):
        result = router.route(text)
        overlay.show_feedback(result.success, result.message)
        if sound_player:
            sound_player.play("confirm" if result.success else "error")
        # Registrar uso para estadísticas del dashboard
        if app_state:
            parsed = parser.parse(text)
            cmd_id = parsed.item["id"] if parsed.matched else text
            cmd_name = parsed.item["name"] if parsed.matched else text
            app_state.record_execution(cmd_id, cmd_name, result.success)

    overlay.command_submitted.connect(_on_command_submitted)

    # Limpieza al salir
    app.aboutToQuit.connect(bootstrap.shutdown)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
