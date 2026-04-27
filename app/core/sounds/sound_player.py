"""
Reproductor de sonidos de feedback para RunDesk.
Usa winsound (incluido en Python en Windows) para reproducir .wav de forma asíncrona.
"""

import logging
import threading
import winsound
from pathlib import Path

logger = logging.getLogger(__name__)

# Directorio de sonidos bundled
_SOUNDS_DIR = Path(__file__).parent / "assets"

# Mapeo de eventos a archivos por defecto
_DEFAULT_SOUNDS = {
    "activation": "activation.wav",
    "confirm": "confirm.wav",
    "error": "error.wav",
}


class SoundPlayer:
    """Reproduce sonidos de feedback de forma no bloqueante."""

    def __init__(self, config=None):
        self._config = config
        self._enabled = True
        self._sync_config()

    def _sync_config(self):
        """Lee la configuración de sonidos."""
        if self._config:
            sounds_cfg = self._config.get("sounds", {})
            self._enabled = sounds_cfg.get("enabled", True)

    def play(self, event: str):
        """Reproduce el sonido asociado al evento (activation, confirm, error).

        Si el archivo .wav no existe, reproduce un beep del sistema.
        """
        self._sync_config()
        if not self._enabled:
            return

        threading.Thread(
            target=self._play_sound, args=(event,), daemon=True
        ).start()

    def _play_sound(self, event: str):
        """Reproduce el sonido en un thread separado."""
        try:
            filename = _DEFAULT_SOUNDS.get(event)
            if filename:
                filepath = _SOUNDS_DIR / filename
                if filepath.exists():
                    winsound.PlaySound(
                        str(filepath), winsound.SND_FILENAME | winsound.SND_NODEFAULT
                    )
                    return

            # Fallback: beep del sistema según evento
            if event == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif event == "confirm":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            logger.debug("No se pudo reproducir sonido: %s", event)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
