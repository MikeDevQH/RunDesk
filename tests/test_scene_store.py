"""Tests para SceneStore."""

import shutil
import tempfile
from pathlib import Path

import pytest

from app.core.config.schemas import SCENE_TEMPLATES
from app.core.scenes.scene_store import SceneStore


@pytest.fixture
def tmp_dir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestSceneStore:
    def test_starts_empty(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        assert store.count == 0
        assert (tmp_dir / "scenes.json").exists()

    def test_add_scene(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        ok, _msg = store.add({
            "id": "scene_test",
            "name": "Test Scene",
            "aliases": ["test"],
            "steps": [
                {"type": "program", "path": "notepad.exe", "enabled": True},
            ],
        })
        assert ok is True
        assert store.count == 1

    def test_add_duplicate_id_fails(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_dup",
            "name": "Dup",
            "aliases": [],
            "steps": [],
        })
        ok, msg = store.add({
            "id": "scene_dup",
            "name": "Dup 2",
            "aliases": [],
            "steps": [],
        })
        assert ok is False
        assert "ya existe" in msg.lower()

    def test_delete_scene(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_del",
            "name": "To Delete",
            "aliases": [],
            "steps": [],
        })
        ok, _msg = store.delete("scene_del")
        assert ok is True
        assert store.count == 0

    def test_update_scene(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_upd",
            "name": "Original",
            "aliases": [],
            "steps": [],
        })
        ok, _msg = store.update("scene_upd", {"name": "Updated"})
        assert ok is True
        scene = store.get_by_id("scene_upd")
        assert scene["name"] == "Updated"

    def test_duplicate_scene(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_orig",
            "name": "Original",
            "aliases": ["orig"],
            "steps": [{"type": "delay", "milliseconds": 500, "enabled": True}],
        })
        ok, _msg = store.duplicate("scene_orig", "scene_copy")
        assert ok is True
        assert store.count == 2
        copy = store.get_by_id("scene_copy")
        assert "(copia)" in copy["name"]

    def test_create_from_template(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        ok, _msg = store.create_from_template("tpl_programming", "my_dev", "Mi Dev")
        assert ok is True
        scene = store.get_by_id("my_dev")
        assert scene["name"] == "Mi Dev"
        assert scene["enabled"] is True
        assert len(scene["steps"]) > 0

    def test_templates_available(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        templates = store.get_templates()
        assert len(templates) == len(SCENE_TEMPLATES)

    def test_persistence_across_reloads(self, tmp_dir):
        store1 = SceneStore(data_dir=tmp_dir)
        store1.add({
            "id": "scene_persist",
            "name": "Persistent",
            "aliases": ["p"],
            "steps": [],
        })

        store2 = SceneStore(data_dir=tmp_dir)
        assert store2.get_by_id("scene_persist") is not None
        assert store2.count == 1

    def test_reset_clears_all(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_temp",
            "name": "Temp",
            "aliases": [],
            "steps": [],
        })
        store.reset()
        assert store.count == 0

    def test_get_enabled_only(self, tmp_dir):
        store = SceneStore(data_dir=tmp_dir)
        store.add({
            "id": "scene_on",
            "name": "On",
            "aliases": [],
            "enabled": True,
            "steps": [],
        })
        store.add({
            "id": "scene_off",
            "name": "Off",
            "aliases": [],
            "enabled": False,
            "steps": [],
        })
        enabled = store.get_enabled()
        assert len(enabled) == 1
        assert enabled[0]["id"] == "scene_on"
