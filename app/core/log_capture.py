"""
Captura de logs en memoria para el visor de diagnóstico.
Mantiene los últimos N registros de log disponibles para la UI.
"""

import logging
from collections import deque


class LogCaptureHandler(logging.Handler):
    """Handler que almacena registros de log en memoria."""

    def __init__(self, max_records: int = 500):
        super().__init__()
        self._records: deque[str] = deque(maxlen=max_records)

    def emit(self, record: logging.LogRecord):
        self._records.append(self.format(record))

    def get_lines(self) -> list[str]:
        """Retorna todas las líneas capturadas."""
        return list(self._records)

    def clear(self):
        """Limpia los registros."""
        self._records.clear()


# Singleton
_handler = LogCaptureHandler()


def get_handler() -> LogCaptureHandler:
    """Retorna el handler singleton para agregarlo al root logger."""
    return _handler


def get_log_lines() -> list[str]:
    """Retorna las líneas de log capturadas."""
    return _handler.get_lines()
