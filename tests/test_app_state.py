"""Tests para app_state.py — usage tracking y persistencia."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.app_state import AppState, DEFAULT_STATE


@pytest.fixture
def temp_state_file(tmp_path):
    """Crea un archivo temporal para el state."""
    return tmp_path / "app_state.json"


@pytest.fixture
def app_state(temp_state_file):
    """Crea un AppState apuntando al archivo temporal."""
    with patch("app.core.app_state.STATE_FILE", temp_state_file):
        state = AppState()
        yield state


class TestAppStateBasics:
    """Tests básicos de AppState."""

    def test_default_state_loaded(self, app_state):
        """Debe cargar defaults cuando no existe archivo."""
        assert app_state.get("last_page") == "dashboard"
        assert app_state.get("onboarding_completed") is False

    def test_set_and_get(self, app_state):
        """Debe poder establecer y obtener valores."""
        app_state.set("last_page", "commands")
        assert app_state.get("last_page") == "commands"

    def test_window_geometry(self, app_state):
        """Debe guardar y recuperar geometría de ventana."""
        app_state.save_window_geometry(100, 200, 800, 600, False)
        geom = app_state.get_window_geometry()
        assert geom["x"] == 100
        assert geom["y"] == 200
        assert geom["width"] == 800
        assert geom["height"] == 600
        assert geom["maximized"] is False

    def test_is_first_run(self, app_state):
        """Debe detectar primera ejecución."""
        assert app_state.is_first_run() is True
        app_state.save_window_geometry(0, 0, 1024, 768, True)
        assert app_state.is_first_run() is False


class TestUsageStats:
    """Tests para el tracking de uso."""

    def test_initial_stats_empty(self, app_state):
        """Las stats iniciales deben estar vacías."""
        stats = app_state.get_usage_stats()
        assert stats["total_executions"] == 0
        assert stats["command_counts"] == {}
        assert stats["recent_activity"] == []

    def test_record_execution_increments_total(self, app_state):
        """Debe incrementar el total de ejecuciones."""
        app_state.record_execution("cmd_1", "Test Command", True)
        stats = app_state.get_usage_stats()
        assert stats["total_executions"] == 1

    def test_record_execution_tracks_counts(self, app_state):
        """Debe contar ejecuciones por comando."""
        app_state.record_execution("cmd_1", "Test", True)
        app_state.record_execution("cmd_1", "Test", True)
        app_state.record_execution("cmd_2", "Other", False)

        stats = app_state.get_usage_stats()
        assert stats["command_counts"]["cmd_1"] == 2
        assert stats["command_counts"]["cmd_2"] == 1

    def test_record_execution_adds_activity(self, app_state):
        """Debe registrar actividad reciente."""
        app_state.record_execution("cmd_1", "Test Command", True)
        activity = app_state.get_recent_activity()
        assert len(activity) == 1
        assert activity[0]["id"] == "cmd_1"
        assert activity[0]["name"] == "Test Command"
        assert activity[0]["success"] is True
        assert "timestamp" in activity[0]

    def test_recent_activity_order(self, app_state):
        """La actividad más reciente debe estar primero."""
        app_state.record_execution("cmd_1", "First", True)
        app_state.record_execution("cmd_2", "Second", True)
        activity = app_state.get_recent_activity()
        assert activity[0]["id"] == "cmd_2"
        assert activity[1]["id"] == "cmd_1"

    def test_recent_activity_limited_to_50(self, app_state):
        """Debe mantener máximo 50 entradas."""
        for i in range(60):
            app_state.record_execution(f"cmd_{i}", f"Cmd {i}", True)
        stats = app_state.get_usage_stats()
        assert len(stats["recent_activity"]) == 50

    def test_get_top_commands(self, app_state):
        """Debe retornar los comandos más usados en orden."""
        for _ in range(5):
            app_state.record_execution("cmd_a", "A", True)
        for _ in range(3):
            app_state.record_execution("cmd_b", "B", True)
        for _ in range(7):
            app_state.record_execution("cmd_c", "C", True)

        top = app_state.get_top_commands(3)
        assert top[0] == ("cmd_c", 7)
        assert top[1] == ("cmd_a", 5)
        assert top[2] == ("cmd_b", 3)

    def test_get_top_commands_with_limit(self, app_state):
        """Debe respetar el límite."""
        for i in range(10):
            app_state.record_execution(f"cmd_{i}", f"Cmd {i}", True)
        top = app_state.get_top_commands(3)
        assert len(top) == 3

    def test_get_recent_activity_with_limit(self, app_state):
        """Debe respetar el límite de actividad."""
        for i in range(20):
            app_state.record_execution(f"cmd_{i}", f"Cmd {i}", True)
        activity = app_state.get_recent_activity(5)
        assert len(activity) == 5

    def test_persistence(self, temp_state_file):
        """Las stats deben persistir en disco."""
        with patch("app.core.app_state.STATE_FILE", temp_state_file):
            state1 = AppState()
            state1.record_execution("cmd_1", "Test", True)

        with patch("app.core.app_state.STATE_FILE", temp_state_file):
            state2 = AppState()
            stats = state2.get_usage_stats()
            assert stats["total_executions"] == 1
            assert stats["command_counts"]["cmd_1"] == 1
