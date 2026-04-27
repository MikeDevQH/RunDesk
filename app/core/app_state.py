"""
Gestión del estado no crítico de la aplicación.
Persiste en app_state.json: geometría de ventana, última página, historial, etc.
"""

import copy
import json
import os
from pathlib import Path


def _get_state_dir() -> Path:
    """Retorna el directorio de datos de la app en AppData."""
    base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    state_dir = Path(base) / "RunDesk"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


STATE_FILE = _get_state_dir() / "app_state.json"

DEFAULT_STATE = {
    "window": {
        "x": None,
        "y": None,
        "width": None,
        "height": None,
        "maximized": True,
    },
    "last_page": "dashboard",
    "onboarding_completed": False,
    "command_history": [],
    "usage_stats": {
        "total_executions": 0,
        "command_counts": {},
        "recent_activity": [],
    },
}


class AppState:
    """Lee y escribe el estado no crítico de la aplicación."""

    def __init__(self):
        self._state: dict = {}
        self._load()

    def _load(self):
        """Carga el estado desde disco. Si no existe, usa defaults."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, encoding="utf-8") as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._state = {}

        # Merge con defaults para asegurar que todas las claves existen
        for key, value in DEFAULT_STATE.items():
            if key not in self._state:
                self._state[key] = copy.deepcopy(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self._state[key]:
                        self._state[key][sub_key] = copy.deepcopy(sub_value)

    def save(self):
        """Persiste el estado actual a disco."""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # Fallo silencioso, no es crítico

    def get(self, key: str, default=None):
        """Obtiene un valor de primer nivel."""
        return self._state.get(key, default)

    def set(self, key: str, value):
        """Establece un valor de primer nivel."""
        self._state[key] = value

    # --- Helpers para geometría de ventana ---

    def get_window_geometry(self) -> dict:
        """Retorna la geometría guardada de la ventana."""
        return self._state.get("window", DEFAULT_STATE["window"])

    def save_window_geometry(self, x: int, y: int, width: int, height: int, maximized: bool):
        """Guarda la geometría actual de la ventana."""
        self._state["window"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "maximized": maximized,
        }
        self.save()

    def is_first_run(self) -> bool:
        """True si no hay estado previo guardado (primera vez)."""
        geom = self._state.get("window", {})
        return geom.get("x") is None and geom.get("width") is None

    # --- Helpers para usage stats ---

    def record_execution(self, command_id: str, command_name: str, success: bool):
        """Registra la ejecución de un comando para estadísticas."""
        from datetime import datetime

        stats = self._state.setdefault("usage_stats", DEFAULT_STATE["usage_stats"].copy())
        stats["total_executions"] = stats.get("total_executions", 0) + 1

        counts = stats.setdefault("command_counts", {})
        counts[command_id] = counts.get(command_id, 0) + 1

        activity = stats.setdefault("recent_activity", [])
        activity.insert(0, {
            "id": command_id,
            "name": command_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        })
        # Mantener máximo 50 entradas recientes
        stats["recent_activity"] = activity[:50]
        self.save()

    def get_usage_stats(self) -> dict:
        """Retorna las estadísticas de uso."""
        return self._state.get("usage_stats", DEFAULT_STATE["usage_stats"])

    def get_top_commands(self, limit: int = 5) -> list[tuple[str, int]]:
        """Retorna los comandos más usados como [(id, count), ...]."""
        stats = self.get_usage_stats()
        counts = stats.get("command_counts", {})
        sorted_cmds = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_cmds[:limit]

    def get_recent_activity(self, limit: int = 10) -> list[dict]:
        """Retorna la actividad reciente."""
        stats = self.get_usage_stats()
        return stats.get("recent_activity", [])[:limit]
