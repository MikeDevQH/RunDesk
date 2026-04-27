"""
Command Store con persistencia a disco.
Gestiona commands.json: carga, merge con defaults protegidos,
CRUD de comandos personalizados, protección de comandos por defecto.
"""

import contextlib
import copy
import json
import logging
import shutil
from pathlib import Path

from app.core.config.schemas import (
    COMMAND_TEMPLATE,
    DEFAULT_COMMANDS,
    validate_command,
)

logger = logging.getLogger(__name__)


class CommandStore:
    """Gestor del catálogo de comandos.

    - Comandos por defecto (default=True, locked=True): no se pueden eliminar.
    - El usuario puede: desactivar, cambiar aliases adicionales, cambiar confirm_required.
    - Comandos personalizados: CRUD completo.
    - Merge: al cargar, los defaults que falten se inyectan automáticamente.
    """

    def __init__(self, data_dir: Path):
        self._dir = data_dir
        self._file = self._dir / "commands.json"
        self._commands: list[dict] = []
        self._load()

    def _load(self):
        """Carga comandos desde disco y merge con defaults."""
        loaded = []
        if self._file.exists():
            try:
                with open(self._file, encoding="utf-8") as f:
                    loaded = json.load(f)
                if not isinstance(loaded, list):
                    logger.warning("commands.json no es una lista, usando defaults")
                    loaded = []
                logger.info("Comandos cargados desde %s (%d)", self._file, len(loaded))
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Error cargando commands.json: %s", e)
                self._backup_corrupt()
                loaded = []

        self._commands = self._merge_with_defaults(loaded)
        self.save()

    def _merge_with_defaults(self, user_commands: list[dict]) -> list[dict]:
        """Asegura que todos los comandos default existan.

        - Si un default ya está en user_commands, preserva los campos editables
          del usuario (enabled, confirm_required, aliases extra) pero restaura
          los campos protegidos (default, locked).
        - Si un default no existe, lo inyecta.
        - Los comandos personalizados del usuario se preservan intactos.
        """
        user_by_id = {cmd["id"]: cmd for cmd in user_commands if "id" in cmd}
        result = []

        # Primero los defaults
        for default_cmd in DEFAULT_COMMANDS:
            did = default_cmd["id"]
            if did in user_by_id:
                # Merge: usuario puede haber cambiado enabled, confirm_required, aliases
                merged = copy.deepcopy(default_cmd)
                user_version = user_by_id[did]
                # Campos editables por el usuario
                merged["enabled"] = user_version.get("enabled", default_cmd["enabled"])
                merged["confirm_required"] = user_version.get(
                    "confirm_required", default_cmd["confirm_required"]
                )
                # Aliases: base + extras del usuario
                base_aliases = set(default_cmd["aliases"])
                user_aliases = set(user_version.get("aliases", []))
                merged["aliases"] = list(base_aliases | user_aliases)
                # Forzar protección
                merged["default"] = True
                merged["locked"] = True
                result.append(merged)
                del user_by_id[did]
            else:
                result.append(copy.deepcopy(default_cmd))

        # Luego los personalizados del usuario
        for cmd in user_commands:
            if cmd.get("id") in {d["id"] for d in DEFAULT_COMMANDS}:
                continue  # Ya procesado arriba
            if "id" in cmd:
                result.append(copy.deepcopy(cmd))

        return result

    def _backup_corrupt(self):
        """Respaldo de archivo corrupto."""
        if self._file.exists():
            backup = self._file.with_suffix(".corrupt.json")
            with contextlib.suppress(OSError):
                shutil.copy2(self._file, backup)

    def save(self):
        """Persiste los comandos a disco."""
        try:
            if self._file.exists():
                backup = self._file.with_suffix(".bak.json")
                shutil.copy2(self._file, backup)

            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._commands, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error("Error guardando commands.json: %s", e)

    # --- Consultas ---

    def get_all(self) -> list[dict]:
        """Retorna copia de todos los comandos."""
        return copy.deepcopy(self._commands)

    def get_by_id(self, cmd_id: str) -> dict | None:
        """Busca un comando por id."""
        for cmd in self._commands:
            if cmd["id"] == cmd_id:
                return copy.deepcopy(cmd)
        return None

    def get_enabled(self) -> list[dict]:
        """Retorna solo los comandos habilitados."""
        return [copy.deepcopy(c) for c in self._commands if c.get("enabled", True)]

    def get_by_category(self, category: str) -> list[dict]:
        """Retorna comandos filtrados por categoría."""
        return [copy.deepcopy(c) for c in self._commands if c.get("category") == category]

    @property
    def count(self) -> int:
        """Número total de comandos."""
        return len(self._commands)

    @property
    def enabled_count(self) -> int:
        """Número de comandos habilitados."""
        return sum(1 for c in self._commands if c.get("enabled", True))

    # --- Mutaciones ---

    def add(self, command: dict) -> tuple[bool, str]:
        """Agrega un comando personalizado. Retorna (ok, mensaje)."""
        # Completar con template
        full_cmd = copy.deepcopy(COMMAND_TEMPLATE)
        full_cmd.update(command)
        full_cmd["default"] = False
        full_cmd["locked"] = False

        # Validar
        errors = validate_command(full_cmd)
        if errors:
            return False, "; ".join(errors)

        # Verificar id único
        if any(c["id"] == full_cmd["id"] for c in self._commands):
            return False, f"Ya existe un comando con id '{full_cmd['id']}'"

        self._commands.append(full_cmd)
        self.save()
        return True, "Comando creado"

    def update(self, cmd_id: str, changes: dict) -> tuple[bool, str]:
        """Actualiza un comando. Respeta protección de defaults."""
        for cmd in self._commands:
            if cmd["id"] == cmd_id:
                if cmd.get("locked"):
                    # Solo campos editables
                    allowed = {"enabled", "confirm_required", "aliases"}
                    blocked = set(changes.keys()) - allowed
                    if blocked:
                        return False, f"Comando protegido: no se puede cambiar {blocked}"
                    for key in allowed:
                        if key in changes:
                            cmd[key] = changes[key]
                else:
                    cmd.update(changes)
                    cmd["default"] = False
                    cmd["locked"] = False

                errors = validate_command(cmd)
                if errors:
                    return False, "; ".join(errors)

                self.save()
                return True, "Comando actualizado"

        return False, f"Comando '{cmd_id}' no encontrado"

    def delete(self, cmd_id: str) -> tuple[bool, str]:
        """Elimina un comando. Los defaults no se pueden eliminar."""
        for i, cmd in enumerate(self._commands):
            if cmd["id"] == cmd_id:
                if cmd.get("locked") or cmd.get("default"):
                    return False, "Los comandos por defecto no se pueden eliminar"
                self._commands.pop(i)
                self.save()
                return True, "Comando eliminado"
        return False, f"Comando '{cmd_id}' no encontrado"

    def duplicate(self, cmd_id: str, new_id: str) -> tuple[bool, str]:
        """Duplica un comando con un nuevo id."""
        original = self.get_by_id(cmd_id)
        if not original:
            return False, f"Comando '{cmd_id}' no encontrado"

        original["id"] = new_id
        original["name"] = f"{original['name']} (copia)"
        original["default"] = False
        original["locked"] = False
        return self.add(original)

    def toggle_enabled(self, cmd_id: str) -> tuple[bool, str]:
        """Activa/desactiva un comando."""
        for cmd in self._commands:
            if cmd["id"] == cmd_id:
                cmd["enabled"] = not cmd.get("enabled", True)
                self.save()
                state = "activado" if cmd["enabled"] else "desactivado"
                return True, f"Comando {state}"
        return False, f"Comando '{cmd_id}' no encontrado"

    def reset_defaults(self):
        """Restaura comandos por defecto a su estado original.
        Los personalizados se eliminan."""
        self._commands = copy.deepcopy(DEFAULT_COMMANDS)
        self.save()
