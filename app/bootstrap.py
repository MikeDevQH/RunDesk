"""
Bootstrap de la aplicación.
Inicializa configuración, servicios y lanza la UI.
"""

import logging

from app.core.app_state import AppState
from app.core.commands.command_store import CommandStore
from app.core.config.config_store import ConfigStore
from app.core.hotkey.hotkey_manager import HotkeyManager
from app.core.input.alias_resolver import AliasResolver
from app.core.scenes.scene_store import SceneStore
from app.core.sounds.sound_player import SoundPlayer

logger = logging.getLogger(__name__)


class AppBootstrap:
    """Inicializador central de la aplicación."""

    def __init__(self):
        self.config: ConfigStore | None = None
        self.app_state: AppState | None = None
        self.commands: CommandStore | None = None
        self.scenes: SceneStore | None = None
        self.hotkey_manager: HotkeyManager | None = None
        self.alias_resolver: AliasResolver | None = None
        self.sound_player: SoundPlayer | None = None

    def initialize(self):
        """Ejecuta la secuencia de inicialización completa."""
        # 1. Config (crea directorio de datos, carga/crea config.json)
        self.config = ConfigStore()
        data_dir = self.config.data_dir

        # 2. Estado de la app (geometría de ventana, historial, etc.)
        self.app_state = AppState()

        # 3. Comandos (carga/crea commands.json, merge con defaults)
        self.commands = CommandStore(data_dir)

        # 4. Escenas (carga/crea scenes.json)
        self.scenes = SceneStore(data_dir)

        # 5. Hotkey Manager (atajo global configurable)
        hotkey = self.config.get("hotkey", "ctrl+space")
        self.hotkey_manager = HotkeyManager(hotkey)

        # 6. Sound player
        self.sound_player = SoundPlayer(config=self.config)

        logger.info(
            "Bootstrap completado: %d comandos, %d escenas, hotkey=%s",
            self.commands.count,
            self.scenes.count,
            hotkey,
        )

    def get_config(self) -> ConfigStore:
        """Retorna el store de configuración."""
        return self.config

    def get_app_state(self) -> AppState:
        """Retorna el store de estado de la app."""
        return self.app_state

    def get_commands(self) -> CommandStore:
        """Retorna el store de comandos."""
        return self.commands

    def get_scenes(self) -> SceneStore:
        """Retorna el store de escenas."""
        return self.scenes

    def get_hotkey_manager(self) -> HotkeyManager:
        """Retorna el gestor de hotkeys."""
        return self.hotkey_manager

    def get_alias_resolver(self) -> AliasResolver:
        """Retorna el alias resolver."""
        return self.alias_resolver

    def get_sound_player(self) -> SoundPlayer:
        """Retorna el reproductor de sonidos."""
        return self.sound_player

    def rebuild_parser_index(self):
        """Reconstruye el índice del parser con datos actuales de commands y scenes."""
        if self.alias_resolver and self.commands and self.scenes:
            self.alias_resolver.build_index(
                commands=self.commands.get_enabled(),
                scenes=self.scenes.get_enabled(),
            )
            logger.info("Índice del parser reconstruido")

    def shutdown(self):
        """Limpieza al cerrar la aplicación."""
        if self.hotkey_manager:
            self.hotkey_manager.stop()
