"""
Scene Store con persistencia a disco.
Gestiona scenes.json: carga, CRUD de escenas, plantillas predefinidas.
"""

import contextlib
import copy
import json
import logging
import shutil
from pathlib import Path

from app.core.config.schemas import (
    DEFAULT_SCENES,
    SCENE_TEMPLATE,
    SCENE_TEMPLATES,
    validate_scene,
)

logger = logging.getLogger(__name__)


class SceneStore:
    """Gestor del catálogo de escenas/rutinas.

    - Escenas del usuario: CRUD completo.
    - Plantillas predefinidas accesibles para crear nuevas escenas.
    - Persistencia en scenes.json.
    """

    def __init__(self, data_dir: Path):
        self._dir = data_dir
        self._file = self._dir / "scenes.json"
        self._scenes: list[dict] = []
        self._load()

    def _load(self):
        """Carga escenas desde disco."""
        if self._file.exists():
            try:
                with open(self._file, encoding="utf-8") as f:
                    loaded = json.load(f)
                if not isinstance(loaded, list):
                    logger.warning("scenes.json no es una lista, usando vacío")
                    loaded = []
                self._scenes = loaded
                logger.info("Escenas cargadas desde %s (%d)", self._file, len(loaded))
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Error cargando scenes.json: %s", e)
                self._backup_corrupt()
                self._scenes = copy.deepcopy(DEFAULT_SCENES)
        else:
            self._scenes = copy.deepcopy(DEFAULT_SCENES)
            self.save()
            logger.info("Scenes creadas con defaults en %s", self._file)

    def _backup_corrupt(self):
        """Respaldo de archivo corrupto."""
        if self._file.exists():
            backup = self._file.with_suffix(".corrupt.json")
            with contextlib.suppress(OSError):
                shutil.copy2(self._file, backup)

    def save(self):
        """Persiste las escenas a disco."""
        try:
            if self._file.exists():
                backup = self._file.with_suffix(".bak.json")
                shutil.copy2(self._file, backup)

            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._scenes, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error("Error guardando scenes.json: %s", e)

    # --- Consultas ---

    def get_all(self) -> list[dict]:
        """Retorna copia de todas las escenas."""
        return copy.deepcopy(self._scenes)

    def get_by_id(self, scene_id: str) -> dict | None:
        """Busca una escena por id."""
        for scene in self._scenes:
            if scene["id"] == scene_id:
                return copy.deepcopy(scene)
        return None

    def get_enabled(self) -> list[dict]:
        """Retorna solo las escenas habilitadas."""
        return [copy.deepcopy(s) for s in self._scenes if s.get("enabled", True)]

    def get_templates(self) -> list[dict]:
        """Retorna las plantillas predefinidas para crear escenas."""
        return copy.deepcopy(SCENE_TEMPLATES)

    @property
    def count(self) -> int:
        """Número total de escenas."""
        return len(self._scenes)

    # --- Mutaciones ---

    def add(self, scene: dict) -> tuple[bool, str]:
        """Agrega una escena nueva."""
        full_scene = copy.deepcopy(SCENE_TEMPLATE)
        full_scene.update(scene)

        errors = validate_scene(full_scene)
        if errors:
            return False, "; ".join(errors)

        if any(s["id"] == full_scene["id"] for s in self._scenes):
            return False, f"Ya existe una escena con id '{full_scene['id']}'"

        self._scenes.append(full_scene)
        self.save()
        return True, "Escena creada"

    def update(self, scene_id: str, changes: dict) -> tuple[bool, str]:
        """Actualiza una escena existente."""
        for scene in self._scenes:
            if scene["id"] == scene_id:
                scene.update(changes)
                scene["id"] = scene_id  # No permitir cambiar el id via update

                errors = validate_scene(scene)
                if errors:
                    return False, "; ".join(errors)

                self.save()
                return True, "Escena actualizada"
        return False, f"Escena '{scene_id}' no encontrada"

    def delete(self, scene_id: str) -> tuple[bool, str]:
        """Elimina una escena."""
        for i, scene in enumerate(self._scenes):
            if scene["id"] == scene_id:
                self._scenes.pop(i)
                self.save()
                return True, "Escena eliminada"
        return False, f"Escena '{scene_id}' no encontrada"

    def duplicate(self, scene_id: str, new_id: str) -> tuple[bool, str]:
        """Duplica una escena con un nuevo id."""
        original = self.get_by_id(scene_id)
        if not original:
            return False, f"Escena '{scene_id}' no encontrada"

        original["id"] = new_id
        original["name"] = f"{original['name']} (copia)"
        return self.add(original)

    def create_from_template(self, template_id: str, new_id: str, name: str) -> tuple[bool, str]:
        """Crea una escena desde una plantilla predefinida."""
        for tpl in SCENE_TEMPLATES:
            if tpl["id"] == template_id:
                new_scene = copy.deepcopy(tpl)
                new_scene["id"] = new_id
                new_scene["name"] = name
                new_scene["enabled"] = True
                return self.add(new_scene)
        return False, f"Plantilla '{template_id}' no encontrada"

    def reset(self):
        """Elimina todas las escenas."""
        self._scenes = copy.deepcopy(DEFAULT_SCENES)
        self.save()
