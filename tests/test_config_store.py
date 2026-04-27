"""Tests para ConfigStore."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from app.core.config.config_store import ConfigStore


@pytest.fixture
def tmp_dir():
    """Directorio temporal para cada test."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestConfigStore:
    def test_creates_config_on_first_run(self, tmp_dir):
        _store = ConfigStore(config_dir=tmp_dir)
        assert (tmp_dir / "config.json").exists()

    def test_loads_defaults(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        assert store.get("hotkey") == "ctrl+space"
        assert store.get("ui_language") == "es"
        assert store.get("schema_version") == 1

    def test_get_nested(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        assert store.get_nested("appearance", "theme") == "professional_dark"
        assert store.get_nested("fuzzy_matching", "threshold") == 0.65
        assert store.get_nested("nonexistent", "key", default="fallback") == "fallback"

    def test_set_persists(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        store.set("hotkey", "alt+space")

        # Recargar desde disco
        store2 = ConfigStore(config_dir=tmp_dir)
        assert store2.get("hotkey") == "alt+space"

    def test_set_nested_persists(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        store.set_nested("appearance", "accent", "#FF0000")

        store2 = ConfigStore(config_dir=tmp_dir)
        assert store2.get_nested("appearance", "accent") == "#FF0000"

    def test_reset_to_defaults(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        store.set("hotkey", "alt+x")
        store.reset_to_defaults()
        assert store.get("hotkey") == "ctrl+space"

    def test_deep_merge_preserves_user_values(self, tmp_dir):
        # Escribir config parcial a disco
        partial = {"schema_version": 1, "hotkey": "ctrl+shift+l", "ui_language": "en"}
        with open(tmp_dir / "config.json", "w") as f:
            json.dump(partial, f)

        store = ConfigStore(config_dir=tmp_dir)
        # User value preserved
        assert store.get("hotkey") == "ctrl+shift+l"
        assert store.get("ui_language") == "en"
        # Defaults filled in
        assert store.get_nested("appearance", "theme") == "professional_dark"
        assert store.get_nested("fuzzy_matching", "enabled") is True

    def test_corrupt_file_uses_defaults(self, tmp_dir):
        with open(tmp_dir / "config.json", "w") as f:
            f.write("{broken json!!!")

        store = ConfigStore(config_dir=tmp_dir)
        assert store.get("hotkey") == "ctrl+space"
        assert (tmp_dir / "config.corrupt.json").exists()

    def test_backup_created_on_save(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        store.set("hotkey", "alt+space")  # triggers save, creates .bak
        assert (tmp_dir / "config.bak.json").exists()

    def test_config_property_returns_copy(self, tmp_dir):
        store = ConfigStore(config_dir=tmp_dir)
        cfg = store.config
        cfg["hotkey"] = "MUTATED"
        assert store.get("hotkey") == "ctrl+space"  # Original not mutated
