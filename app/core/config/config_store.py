"""
Config Manager con persistencia a disco.
Lee/escribe config.json en %LOCALAPPDATA%/RunDesk.
Merge con defaults para asegurar que siempre existan todas las claves.
"""

import copy
import json
import logging
import os
import shutil
from pathlib import Path

from app.core.config.migrations import migrate, needs_migration
from app.core.config.schemas import (
    DEFAULT_CONFIG,
    validate_config,
)

logger = logging.getLogger(__name__)


def _get_data_dir() -> Path:
    """Retorna el directorio de datos de la app en AppData."""
    base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    data_dir = Path(base) / "RunDesk"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class ConfigStore:
    """Gestor de configuración con persistencia JSON.

    - Carga desde disco si existe, sino usa defaults.
    - Merge profundo: claves nuevas de defaults se añaden automáticamente.
    - Respaldo automático antes de sobrescribir.
    - Validación antes de cargar.
    """

    def __init__(self, config_dir: Path | None = None):
        self._dir = config_dir or _get_data_dir()
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "config.json"
        self._config: dict = {}
        self._load()

    def _load(self):
        """Carga config desde disco, merge con defaults."""
        if self._file.exists():
            try:
                with open(self._file, encoding="utf-8") as f:
                    loaded = json.load(f)

                # Migrar si es necesario
                if needs_migration(loaded):
                    loaded = migrate(loaded)

                errors = validate_config(loaded)
                if errors:
                    logger.warning("Config con errores de validación: %s", errors)

                self._config = self._deep_merge(
                    copy.deepcopy(DEFAULT_CONFIG), loaded
                )
                logger.info("Config cargada desde %s", self._file)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Error cargando config, usando defaults: %s", e)
                self._config = copy.deepcopy(DEFAULT_CONFIG)
                self._backup_corrupt()
        else:
            self._config = copy.deepcopy(DEFAULT_CONFIG)
            self.save()
            logger.info("Config creada con defaults en %s", self._file)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Merge profundo: base provee defaults, override sobreescribe valores."""
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    def _backup_corrupt(self):
        """Guarda respaldo del config corrupto para diagnóstico."""
        if self._file.exists():
            backup = self._file.with_suffix(".corrupt.json")
            try:
                shutil.copy2(self._file, backup)
                logger.info("Backup de config corrupto en %s", backup)
            except OSError:
                pass

    def save(self):
        """Persiste la configuración actual a disco con respaldo previo."""
        try:
            # Respaldo antes de sobrescribir
            if self._file.exists():
                backup = self._file.with_suffix(".bak.json")
                shutil.copy2(self._file, backup)

            self._dir.mkdir(parents=True, exist_ok=True)
            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error("Error guardando config: %s", e)

    def get(self, key: str, default=None):
        """Obtiene un valor de configuración de primer nivel."""
        return self._config.get(key, default)

    def get_nested(self, *keys, default=None):
        """Obtiene un valor anidado. Ej: get_nested('appearance', 'theme')"""
        current = self._config
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return default
            else:
                return default
        return current

    def set(self, key: str, value):
        """Establece un valor de primer nivel y guarda."""
        self._config[key] = value
        self.save()

    def set_nested(self, *keys_and_value):
        """Establece un valor anidado. Último argumento es el valor.
        Ej: set_nested('appearance', 'accent', '#FF0000')
        """
        if len(keys_and_value) < 2:
            return
        *keys, value = keys_and_value
        current = self._config
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.save()

    def reset_to_defaults(self):
        """Restaura toda la configuración a defaults de fábrica."""
        self._config = copy.deepcopy(DEFAULT_CONFIG)
        self.save()

    @property
    def config(self) -> dict:
        """Retorna una copia de la configuración completa."""
        return copy.deepcopy(self._config)

    @property
    def data_dir(self) -> Path:
        """Retorna el directorio de datos."""
        return self._dir
