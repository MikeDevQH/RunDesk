"""Tests para CommandStore."""

import shutil
import tempfile
from pathlib import Path

import pytest

from app.core.commands.command_store import CommandStore
from app.core.config.schemas import DEFAULT_COMMANDS


@pytest.fixture
def tmp_dir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestCommandStore:
    def test_creates_commands_with_defaults(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        assert store.count == len(DEFAULT_COMMANDS)
        assert (tmp_dir / "commands.json").exists()

    def test_default_commands_are_locked(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        for cmd in store.get_all():
            if cmd["default"]:
                assert cmd["locked"] is True

    def test_cannot_delete_default_command(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, msg = store.delete("cmd_shutdown")
        assert ok is False
        assert "no se pueden eliminar" in msg.lower()

    def test_cannot_modify_protected_fields_on_locked(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, msg = store.update("cmd_shutdown", {"name": "Nuevo nombre"})
        assert ok is False
        assert "protegido" in msg.lower()

    def test_can_disable_default_command(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, _msg = store.update("cmd_shutdown", {"enabled": False})
        assert ok is True
        cmd = store.get_by_id("cmd_shutdown")
        assert cmd["enabled"] is False

    def test_can_toggle_enabled(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, _ = store.toggle_enabled("cmd_lock")
        assert ok is True
        cmd = store.get_by_id("cmd_lock")
        assert cmd["enabled"] is False

    def test_add_custom_command(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, _msg = store.add({
            "id": "cmd_custom_1",
            "name": "Mi comando",
            "aliases": ["mc"],
            "type": "program",
            "path": "C:\\Windows\\notepad.exe",
        })
        assert ok is True
        assert store.count == len(DEFAULT_COMMANDS) + 1

    def test_delete_custom_command(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        store.add({
            "id": "cmd_custom_del",
            "name": "Para borrar",
            "aliases": ["borrar"],
            "type": "program",
        })
        ok, _msg = store.delete("cmd_custom_del")
        assert ok is True
        assert store.count == len(DEFAULT_COMMANDS)

    def test_duplicate_command(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, _msg = store.duplicate("cmd_lock", "cmd_lock_copy")
        assert ok is True
        copy = store.get_by_id("cmd_lock_copy")
        assert copy is not None
        assert copy["default"] is False
        assert copy["locked"] is False

    def test_add_duplicate_id_fails(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        ok, msg = store.add({
            "id": "cmd_shutdown",
            "name": "Duplicado",
            "aliases": ["dup"],
            "type": "program",
        })
        assert ok is False
        assert "ya existe" in msg.lower()

    def test_persistence_across_reloads(self, tmp_dir):
        store1 = CommandStore(data_dir=tmp_dir)
        store1.add({
            "id": "cmd_persist",
            "name": "Persistente",
            "aliases": ["pers"],
            "type": "url",
            "url": "https://example.com",
        })

        store2 = CommandStore(data_dir=tmp_dir)
        assert store2.get_by_id("cmd_persist") is not None
        assert store2.count == len(DEFAULT_COMMANDS) + 1

    def test_get_enabled_only(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        store.toggle_enabled("cmd_mute")
        enabled = store.get_enabled()
        ids = [c["id"] for c in enabled]
        assert "cmd_mute" not in ids

    def test_get_by_category(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        audio = store.get_by_category("audio")
        assert len(audio) >= 3
        for cmd in audio:
            assert cmd["category"] == "audio"

    def test_reset_defaults_removes_custom(self, tmp_dir):
        store = CommandStore(data_dir=tmp_dir)
        store.add({
            "id": "cmd_temp",
            "name": "Temporal",
            "aliases": ["tmp"],
            "type": "program",
        })
        store.reset_defaults()
        assert store.count == len(DEFAULT_COMMANDS)
        assert store.get_by_id("cmd_temp") is None
