"""Tests para el sistema de internacionalización."""

from app.i18n import get_language, set_language, t


class TestTranslator:
    """Tests del motor de traducciones."""

    def test_default_language_is_es(self):
        set_language("es")
        assert get_language() == "es"

    def test_switch_to_en(self):
        set_language("en")
        assert get_language() == "en"
        set_language("es")

    def test_invalid_language_ignored(self):
        set_language("es")
        set_language("xx")
        assert get_language() == "es"

    def test_simple_key(self):
        set_language("es")
        assert t("sidebar.dashboard") == "Dashboard"

    def test_nested_key(self):
        set_language("es")
        assert t("commands.title") == "Comandos"

    def test_en_translation(self):
        set_language("en")
        assert t("commands.title") == "Commands"
        set_language("es")

    def test_missing_key_returns_key(self):
        set_language("es")
        assert t("nonexistent.key") == "nonexistent.key"

    def test_partial_key_returns_key(self):
        set_language("es")
        result = t("sidebar")
        assert result == "sidebar"

    def test_overlay_placeholder_es(self):
        set_language("es")
        assert t("overlay.placeholder") == "Escribe un comando..."

    def test_overlay_placeholder_en(self):
        set_language("en")
        assert t("overlay.placeholder") == "Type a command..."
        set_language("es")

    def test_all_sidebar_keys_exist_both_langs(self):
        for lang in ("es", "en"):
            set_language(lang)
            for key in ("dashboard", "commands", "scenes", "launcher",
                        "appearance", "languages", "tutorials", "diagnostics"):
                result = t(f"sidebar.{key}")
                assert result != f"sidebar.{key}", f"Missing sidebar.{key} in {lang}"
        set_language("es")

    def test_catalogs_have_same_top_level_keys(self):
        from app.i18n.catalog_en import CATALOG_EN
        from app.i18n.catalog_es import CATALOG_ES
        assert set(CATALOG_ES.keys()) == set(CATALOG_EN.keys()), (
            f"Mismatched top-level keys: "
            f"ES-only={set(CATALOG_ES) - set(CATALOG_EN)}, "
            f"EN-only={set(CATALOG_EN) - set(CATALOG_ES)}"
        )

    def test_catalogs_have_same_nested_keys(self):
        from app.i18n.catalog_en import CATALOG_EN
        from app.i18n.catalog_es import CATALOG_ES
        for section in CATALOG_ES:
            es_keys = set(CATALOG_ES[section].keys())
            en_keys = set(CATALOG_EN[section].keys())
            assert es_keys == en_keys, (
                f"Mismatched keys in '{section}': "
                f"ES-only={es_keys - en_keys}, "
                f"EN-only={en_keys - es_keys}"
            )

    def test_language_page_keys_exist(self):
        for lang in ("es", "en"):
            set_language(lang)
            for key in ("title", "subtitle", "active_badge",
                        "es_name", "en_name", "info_title",
                        "info_1", "info_2", "info_3", "info_4"):
                result = t(f"languages.{key}")
                assert result != f"languages.{key}", (
                    f"Missing languages.{key} in {lang}"
                )
        set_language("es")

    def test_diagnostics_keys_exist(self):
        for lang in ("es", "en"):
            set_language(lang)
            for key in ("title", "subtitle", "health_ok",
                        "health_warning", "health_error",
                        "system_info", "os", "architecture",
                        "config_path", "commands_loaded",
                        "scenes_loaded", "file_ok", "file_missing",
                        "file_corrupt", "file_check",
                        "log_viewer", "log_empty",
                        "open_data_folder", "export_logs",
                        "factory_reset", "reset_title",
                        "reset_warning", "reset_success"):
                result = t(f"diagnostics.{key}")
                assert result != f"diagnostics.{key}", (
                    f"Missing diagnostics.{key} in {lang}"
                )
        set_language("es")

    def test_launcher_keys_exist(self):
        for lang in ("es", "en"):
            set_language(lang)
            for key in ("title", "subtitle", "section_activation",
                        "hotkey", "hotkey_desc", "section_fuzzy",
                        "section_behavior", "restart_hint", "yes", "no",
                        "saved"):
                result = t(f"launcher.{key}")
                assert result != f"launcher.{key}", (
                    f"Missing launcher.{key} in {lang}"
                )
        set_language("es")

    def test_tutorial_step_keys_exist_both_langs(self):
        """Verifica que todos los pasos de tutoriales existen en ambos idiomas."""
        from app.ui.pages.tutorials_page import TUTORIAL_DEFS
        for lang in ("es", "en"):
            set_language(lang)
            for tdef in TUTORIAL_DEFS:
                tid = tdef["id"]
                prefix = f"tutorials.tut_{tid}"
                # title, desc, level, action, tip
                for suffix in ("_title", "_desc", "_level", "_action", "_tip"):
                    key = f"{prefix}{suffix}"
                    result = t(key)
                    assert result != key, f"Missing {key} in {lang}"
                # steps
                for i in range(1, tdef["step_count"] + 1):
                    key = f"{prefix}_step_{i}"
                    result = t(key)
                    assert result != key, f"Missing {key} in {lang}"
        set_language("es")

    def test_default_cmd_names_exist_both_langs(self):
        """Verifica que los nombres traducidos de comandos default existen."""
        from app.core.config.schemas import DEFAULT_COMMANDS
        for lang in ("es", "en"):
            set_language(lang)
            for cmd in DEFAULT_COMMANDS:
                key = f"default_cmd.{cmd['id']}"
                result = t(key)
                assert result != key, f"Missing {key} in {lang}"
        set_language("es")
