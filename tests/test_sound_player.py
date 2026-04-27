"""Tests para SoundPlayer."""

from unittest.mock import MagicMock, patch

from app.core.sounds.sound_player import SoundPlayer


class TestSoundPlayer:
    """Tests del reproductor de sonidos."""

    def test_init_defaults(self):
        player = SoundPlayer()
        assert player._enabled is True

    def test_init_with_config_disabled(self):
        config = MagicMock()
        config.get.return_value = {"enabled": False}
        player = SoundPlayer(config=config)
        assert player._enabled is False

    def test_set_enabled(self):
        player = SoundPlayer()
        player.set_enabled(False)
        assert player._enabled is False
        player.set_enabled(True)
        assert player._enabled is True

    @patch("app.core.sounds.sound_player.threading")
    def test_play_disabled_does_not_start_thread(self, mock_threading):
        player = SoundPlayer()
        player.set_enabled(False)
        player.play("confirm")
        mock_threading.Thread.assert_not_called()

    @patch("app.core.sounds.sound_player.threading")
    def test_play_enabled_starts_thread(self, mock_threading):
        player = SoundPlayer()
        player.play("confirm")
        mock_threading.Thread.assert_called_once()
        mock_threading.Thread.return_value.start.assert_called_once()

    @patch("app.core.sounds.sound_player.winsound")
    def test_play_sound_fallback_beep(self, mock_winsound):
        """When no .wav file exists, falls back to system beep."""
        player = SoundPlayer()
        player._play_sound("error")
        mock_winsound.MessageBeep.assert_called_once()

    @patch("app.core.sounds.sound_player.winsound")
    def test_play_sound_confirm_beep(self, mock_winsound):
        player = SoundPlayer()
        player._play_sound("confirm")
        mock_winsound.MessageBeep.assert_called_once()

    @patch("app.core.sounds.sound_player.winsound")
    def test_play_sound_activation_beep(self, mock_winsound):
        player = SoundPlayer()
        player._play_sound("activation")
        mock_winsound.MessageBeep.assert_called_once()

    @patch("app.core.sounds.sound_player.winsound")
    def test_play_sound_unknown_event(self, mock_winsound):
        """Unknown events fall through to default beep."""
        player = SoundPlayer()
        player._play_sound("unknown_event")
        mock_winsound.MessageBeep.assert_called_once()
