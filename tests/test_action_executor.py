"""Tests para ActionExecutor y CommandRouter."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.actions.action_executor import ActionExecutor, ActionResult
from app.core.actions.command_router import CommandRouter
from app.core.input.alias_resolver import AliasResolver
from app.core.input.command_parser import CommandParser
from app.core.input.fuzzy_matcher import FuzzyMatcher

# --- Fixtures ---

COMMANDS = [
    {
        "id": "cmd_open_calc",
        "name": "Abrir calculadora",
        "aliases": ["calc", "calculadora"],
        "type": "system",
        "command_id": "open_calc",
        "enabled": True,
        "confirm_required": False,
        "category": "productivity",
    },
    {
        "id": "cmd_lock",
        "name": "Bloquear equipo",
        "aliases": ["bloquear", "lock"],
        "type": "system",
        "command_id": "lock",
        "enabled": True,
        "confirm_required": False,
        "category": "system",
    },
    {
        "id": "cmd_shutdown",
        "name": "Apagar equipo",
        "aliases": ["apagar", "shutdown"],
        "type": "system",
        "command_id": "shutdown",
        "enabled": True,
        "confirm_required": True,
        "category": "system",
    },
    {
        "id": "cmd_custom_url",
        "name": "Abrir GitHub",
        "aliases": ["github", "gh"],
        "type": "url",
        "url": "https://github.com",
        "enabled": True,
        "confirm_required": False,
        "category": "custom",
    },
    {
        "id": "cmd_custom_prog",
        "name": "Abrir Notepad",
        "aliases": ["notepad", "notas"],
        "type": "program",
        "path": "notepad.exe",
        "enabled": True,
        "confirm_required": False,
        "category": "custom",
    },
]


@pytest.fixture
def executor():
    return ActionExecutor()


@pytest.fixture
def router():
    resolver = AliasResolver()
    resolver.build_index(COMMANDS, [])
    fuzzy = FuzzyMatcher(threshold=0.65)
    parser = CommandParser(resolver, fuzzy)
    ex = ActionExecutor()
    return CommandRouter(parser, ex)


# === ActionResult ===


class TestActionResult:
    def test_success_repr(self):
        r = ActionResult(True, "OK")
        assert "OK" in repr(r)

    def test_error_repr(self):
        r = ActionResult(False, "Fallo")
        assert "ERROR" in repr(r)


# === ActionExecutor ===


class TestActionExecutor:
    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_open_calc(self, mock_popen, executor):
        result = executor.execute({"type": "system", "command_id": "open_calc"})
        assert result.success is True
        assert "Calculadora" in result.message
        mock_popen.assert_called_once()

    @patch("app.core.actions.action_executor.ctypes.windll.user32.LockWorkStation")
    def test_lock(self, mock_lock, executor):
        result = executor.execute({"type": "system", "command_id": "lock"})
        assert result.success is True
        mock_lock.assert_called_once()

    @patch("app.core.actions.action_executor.webbrowser.open")
    def test_open_url(self, mock_open, executor):
        result = executor.execute({"type": "url", "url": "https://example.com"})
        assert result.success is True
        mock_open.assert_called_once_with("https://example.com")

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_open_program(self, mock_popen, executor):
        result = executor.execute({"type": "program", "path": "notepad.exe"})
        assert result.success is True
        mock_popen.assert_called_once()

    def test_open_program_no_path(self, executor):
        result = executor.execute({"type": "program"})
        assert result.success is False

    def test_open_url_no_url(self, executor):
        result = executor.execute({"type": "url"})
        assert result.success is False

    def test_unknown_system_command(self, executor):
        result = executor.execute({"type": "system", "command_id": "nonexistent"})
        assert result.success is False

    def test_unknown_type(self, executor):
        result = executor.execute({"type": "alien_type"})
        assert result.success is False

    def test_open_folder_not_found(self, executor):
        result = executor.execute({"type": "folder", "path": "/nonexistent/dir"})
        assert result.success is False

    def test_script_no_command(self, executor):
        result = executor.execute({"type": "script"})
        assert result.success is False

    def test_register_launcher_action(self, executor):
        callback = MagicMock()
        executor.register_launcher_action("test_action", callback)
        result = executor.execute({"type": "system", "command_id": "test_action"})
        assert result.success is True
        callback.assert_called_once()

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_run_script(self, mock_popen, executor):
        result = executor.execute({"type": "script", "shell": "echo hello"})
        assert result.success is True
        mock_popen.assert_called_once()


# === CommandRouter ===


class TestCommandRouter:
    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_route_exact_alias(self, mock_popen, router):
        result = router.route("calc")
        assert result.success is True

    def test_route_no_match(self, router):
        result = router.route("xyznonexistent123")
        assert result.success is False
        assert "no encontrado" in result.message.lower()

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_route_fuzzy(self, mock_popen, router):
        result = router.route("calculadra")
        assert result.success is True

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_route_confirm_required_still_executes(self, mock_popen, router):
        # shutdown requiere confirmación pero por ahora ejecuta igual
        result = router.route("apagar")
        assert result.success is True

    def test_route_empty(self, router):
        result = router.route("")
        assert result.success is False

    def test_parser_property(self, router):
        assert router.parser is not None
