"""
Gestor de atajos de teclado globales.
Usa la librería keyboard para capturar hotkeys a nivel de sistema.
Emite señales Qt para comunicar con el hilo principal de la UI.
"""

import logging

import keyboard
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """Registra y gestiona atajos de teclado globales.

    Emite `hotkey_triggered` cuando se presiona el atajo configurado.
    La librería keyboard opera en un hilo de bajo nivel, por eso se
    usa una Signal de Qt para cruzar al hilo principal de forma segura.
    """

    hotkey_triggered = Signal()

    def __init__(self, hotkey: str = "ctrl+space", parent=None):
        super().__init__(parent)
        self._hotkey = hotkey.lower().strip()
        self._registered = False
        self._paused = False

    @property
    def hotkey(self) -> str:
        """Atajo configurado actualmente."""
        return self._hotkey

    def start(self):
        """Registra el atajo global."""
        if self._registered:
            return
        try:
            keyboard.add_hotkey(self._hotkey, self._on_hotkey, suppress=True)
            self._registered = True
            logger.info("Hotkey global registrado: %s", self._hotkey)
        except Exception:
            logger.exception("Error registrando hotkey '%s'", self._hotkey)

    def stop(self):
        """Des-registra el atajo global."""
        if not self._registered:
            return
        try:
            keyboard.remove_hotkey(self._hotkey)
            self._registered = False
            logger.info("Hotkey global eliminado: %s", self._hotkey)
        except Exception:
            logger.exception("Error eliminando hotkey '%s'", self._hotkey)

    def change_hotkey(self, new_hotkey: str):
        """Cambia el atajo de teclado en caliente."""
        was_registered = self._registered
        if was_registered:
            self.stop()
        self._hotkey = new_hotkey.lower().strip()
        if was_registered:
            self.start()

    def pause(self):
        """Pausa temporalmente el hotkey (no lo des-registra)."""
        self._paused = True
        logger.info("Hotkey pausado")

    def resume(self):
        """Reanuda el hotkey pausado."""
        self._paused = False
        logger.info("Hotkey reanudado")

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_registered(self) -> bool:
        return self._registered

    def _on_hotkey(self):
        """Callback interno de keyboard. Emite señal Qt si no está pausado."""
        if not self._paused:
            self.hotkey_triggered.emit()
