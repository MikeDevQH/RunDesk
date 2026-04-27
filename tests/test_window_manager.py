"""Tests para WindowManager y confirmación de acciones críticas."""

from typing import ClassVar
from unittest.mock import MagicMock, patch

from app.core.actions.action_executor import ActionExecutor, ActionResult
from app.core.actions.command_router import CommandRouter
from app.core.actions.window_manager import (
    _calc_position,
    _get_all_visible_windows,
    find_new_window,
    get_monitors,
)


class TestCalcPosition:
    """Tests para el cálculo de posiciones predefinidas."""

    WORK_AREA: ClassVar[dict] = {"x": 0, "y": 0, "width": 1920, "height": 1080}

    def test_maximized(self):
        x, y, w, h = _calc_position("maximized", self.WORK_AREA)
        assert (x, y, w, h) == (0, 0, 1920, 1080)

    def test_left_half(self):
        x, y, w, h = _calc_position("left-half", self.WORK_AREA)
        assert (x, y, w, h) == (0, 0, 960, 1080)

    def test_right_half(self):
        x, y, w, h = _calc_position("right-half", self.WORK_AREA)
        assert (x, y, w, h) == (960, 0, 960, 1080)

    def test_top_half(self):
        x, y, w, h = _calc_position("top-half", self.WORK_AREA)
        assert (x, y, w, h) == (0, 0, 1920, 540)

    def test_bottom_half(self):
        x, y, w, h = _calc_position("bottom-half", self.WORK_AREA)
        assert (x, y, w, h) == (0, 540, 1920, 540)

    def test_top_left(self):
        x, y, w, h = _calc_position("top-left", self.WORK_AREA)
        assert (x, y, w, h) == (0, 0, 960, 540)

    def test_top_right(self):
        x, y, w, h = _calc_position("top-right", self.WORK_AREA)
        assert (x, y, w, h) == (960, 0, 960, 540)

    def test_bottom_left(self):
        x, y, w, h = _calc_position("bottom-left", self.WORK_AREA)
        assert (x, y, w, h) == (0, 540, 960, 540)

    def test_bottom_right(self):
        x, y, w, h = _calc_position("bottom-right", self.WORK_AREA)
        assert (x, y, w, h) == (960, 540, 960, 540)

    def test_center(self):
        x, y, w, h = _calc_position("center", self.WORK_AREA)
        assert (x, y, w, h) == (480, 270, 960, 540)

    def test_unknown_defaults_to_full(self):
        x, y, w, h = _calc_position("unknown", self.WORK_AREA)
        assert (x, y, w, h) == (0, 0, 1920, 1080)

    def test_offset_monitor(self):
        """Un monitor con offset (multi-monitor)."""
        wa = {"x": 1920, "y": 0, "width": 2560, "height": 1440}
        x, _y, w, h = _calc_position("right-half", wa)
        assert x == 1920 + 1280
        assert w == 1280
        assert h == 1440


class TestGetMonitors:
    """Tests básicos para get_monitors (depende del hardware)."""

    def test_returns_list(self):
        result = get_monitors()
        assert isinstance(result, list)

    def test_at_least_one_monitor(self):
        result = get_monitors()
        assert len(result) >= 1

    def test_monitor_has_required_keys(self):
        result = get_monitors()
        if result:
            m = result[0]
            assert "index" in m
            assert "width" in m
            assert "height" in m
            assert "primary" in m
            assert "work_area" in m

    def test_primary_monitor_exists(self):
        result = get_monitors()
        primaries = [m for m in result if m["primary"]]
        assert len(primaries) == 1


class TestConfirmCallback:
    """Tests para el flujo de confirmación en CommandRouter."""

    def _make_router(self):
        parser = MagicMock()
        executor = MagicMock()
        return CommandRouter(parser, executor), parser, executor

    def test_confirm_accepted_executes(self):
        router, parser, executor = self._make_router()
        parser.parse.return_value = MagicMock(
            matched=True,
            item={
                "type": "command",
                "name": "Apagar",
                "data": {"type": "system", "command_id": "shutdown", "confirm_required": True},
            },
        )
        executor.execute.return_value = ActionResult(True, "Apagando")
        router.set_confirm_callback(lambda name: True)

        result = router.route("apagar")
        assert result.success
        executor.execute.assert_called_once()

    def test_confirm_rejected_cancels(self):
        router, parser, executor = self._make_router()
        parser.parse.return_value = MagicMock(
            matched=True,
            item={
                "type": "command",
                "name": "Apagar",
                "data": {"type": "system", "command_id": "shutdown", "confirm_required": True},
            },
        )
        router.set_confirm_callback(lambda name: False)

        result = router.route("apagar")
        assert not result.success
        assert "Cancelado" in result.message
        executor.execute.assert_not_called()

    def test_no_callback_still_executes(self):
        router, parser, executor = self._make_router()
        parser.parse.return_value = MagicMock(
            matched=True,
            item={
                "type": "command",
                "name": "Apagar",
                "data": {"type": "system", "command_id": "shutdown", "confirm_required": True},
            },
        )
        executor.execute.return_value = ActionResult(True, "OK")
        # No se establece callback

        result = router.route("apagar")
        assert result.success


class TestWindowPositionInExecutor:
    """Tests para la integración de window positioning en ActionExecutor."""

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_open_program_without_window(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.pid = 1234
        mock_popen.return_value = mock_proc

        executor = ActionExecutor()
        result = executor.execute({"type": "program", "path": "notepad.exe"})
        assert result.success

    @patch("app.core.actions.window_manager.launch_and_position")
    def test_open_program_with_window_calls_launch_and_position(self, mock_lap):
        executor = ActionExecutor()
        cmd = {
            "type": "program",
            "path": "notepad.exe",
            "window": {"monitor": 0, "position": "right-half"},
        }
        result = executor.execute(cmd)
        assert result.success
        mock_lap.assert_called_once()
        call_kwargs = mock_lap.call_args
        assert call_kwargs[1]["monitor_index"] == 0
        assert call_kwargs[1]["position"] == "right-half"

    @patch("app.core.actions.action_executor.subprocess.Popen")
    def test_open_program_no_window_config_skips(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.pid = 9999
        mock_popen.return_value = mock_proc

        executor = ActionExecutor()
        cmd = {"type": "program", "path": "calc.exe", "window": None}
        result = executor.execute(cmd)
        assert result.success

    @patch("app.core.actions.window_manager.launch_and_position")
    def test_open_url_with_window_calls_launch_and_position(self, mock_lap):
        executor = ActionExecutor()
        cmd = {
            "type": "url",
            "url": "https://youtube.com",
            "window": {"monitor": 0, "position": "left-half"},
        }
        result = executor.execute(cmd)
        assert result.success
        mock_lap.assert_called_once()


class TestFindNewWindow:
    """Tests para find_new_window."""

    def test_find_new_window_returns_none_when_no_change(self):
        current = _get_all_visible_windows()
        # Sin lanzar nada, no debería encontrar ventana nueva
        result = find_new_window(current, timeout=0.5)
        assert result is None
