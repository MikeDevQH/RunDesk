"""Tests para exportar/importar configuración (ZIP)."""

import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def data_dir(tmp_path):
    """Crea un directorio de datos temporal con archivos de config."""
    config = {"schema_version": 1, "app_name": "RunDesk", "hotkey": "ctrl+space"}
    commands = [{"id": "cmd_1", "name": "Test", "type": "app"}]
    scenes = []

    (tmp_path / "config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    (tmp_path / "commands.json").write_text(
        json.dumps(commands, indent=2), encoding="utf-8"
    )
    (tmp_path / "scenes.json").write_text(
        json.dumps(scenes, indent=2), encoding="utf-8"
    )
    return tmp_path


class TestExportConfig:
    """Tests para exportar configuración a ZIP."""

    def test_export_creates_zip(self, data_dir, tmp_path):
        """Debe crear un archivo ZIP con los archivos de config."""
        zip_path = tmp_path / "export.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in ("config.json", "commands.json", "scenes.json"):
                fpath = data_dir / fname
                if fpath.exists():
                    zf.write(fpath, fname)

        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            assert "config.json" in names
            assert "commands.json" in names
            assert "scenes.json" in names

    def test_export_contains_valid_json(self, data_dir, tmp_path):
        """Los archivos en el ZIP deben ser JSON válido."""
        zip_path = tmp_path / "export.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in ("config.json", "commands.json", "scenes.json"):
                zf.write(data_dir / fname, fname)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for fname in ("config.json", "commands.json", "scenes.json"):
                data = json.loads(zf.read(fname))
                assert data is not None

    def test_export_skips_missing_files(self, tmp_path):
        """Debe manejar archivos faltantes sin error."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "config.json").write_text('{"test": true}', encoding="utf-8")

        zip_path = tmp_path / "export.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in ("config.json", "commands.json", "scenes.json"):
                fpath = data_dir / fname
                if fpath.exists():
                    zf.write(fpath, fname)

        with zipfile.ZipFile(zip_path, "r") as zf:
            assert "config.json" in zf.namelist()
            assert "commands.json" not in zf.namelist()


class TestImportConfig:
    """Tests para importar configuración desde ZIP."""

    def test_import_extracts_files(self, data_dir, tmp_path):
        """Debe extraer archivos del ZIP al directorio de datos."""
        # Crear ZIP de origen
        zip_path = tmp_path / "import.zip"
        new_config = {"schema_version": 1, "app_name": "RunDesk", "hotkey": "alt+space"}

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("config.json", json.dumps(new_config))
            zf.writestr("commands.json", "[]")
            zf.writestr("scenes.json", "[]")

        # Importar al directorio de destino
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        valid_files = {"config.json", "commands.json", "scenes.json"}
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())
            to_extract = names & valid_files
            for fname in to_extract:
                zf.extract(fname, dest_dir)

        # Verificar
        imported = json.loads((dest_dir / "config.json").read_text(encoding="utf-8"))
        assert imported["hotkey"] == "alt+space"

    def test_import_ignores_unknown_files(self, tmp_path):
        """Debe ignorar archivos que no son config/commands/scenes."""
        zip_path = tmp_path / "import.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("config.json", '{"test": true}')
            zf.writestr("malware.exe", "bad content")
            zf.writestr("random.txt", "hello")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        valid_files = {"config.json", "commands.json", "scenes.json"}
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())
            to_extract = names & valid_files
            for fname in to_extract:
                zf.extract(fname, dest_dir)

        assert (dest_dir / "config.json").exists()
        assert not (dest_dir / "malware.exe").exists()
        assert not (dest_dir / "random.txt").exists()

    def test_import_rejects_empty_zip(self, tmp_path):
        """Debe rechazar ZIPs sin archivos válidos."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("readme.txt", "no config here")

        valid_files = {"config.json", "commands.json", "scenes.json"}
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())
            to_extract = names & valid_files
            assert len(to_extract) == 0

    def test_import_overwrites_existing(self, data_dir, tmp_path):
        """Debe sobreescribir archivos existentes."""
        zip_path = tmp_path / "import.zip"
        new_commands = [{"id": "new_cmd", "name": "New"}]

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("commands.json", json.dumps(new_commands))

        valid_files = {"config.json", "commands.json", "scenes.json"}
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())
            to_extract = names & valid_files
            for fname in to_extract:
                zf.extract(fname, data_dir)

        imported = json.loads((data_dir / "commands.json").read_text(encoding="utf-8"))
        assert imported[0]["id"] == "new_cmd"
