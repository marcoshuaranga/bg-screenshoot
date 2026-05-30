"""Tests for ScreenshotCapture class"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.config_manager import Config
from src.screenshot_tray import ScreenshotCapture


class TestScreenshotCapture:
    """Test ScreenshotCapture class"""

    @pytest.fixture
    def screenshot_capturer(self, test_config, mock_pyautogui, tmp_path):
        """Create a screenshot capturer instance"""
        # Ensure folder exists
        (tmp_path / "screenshots").mkdir(exist_ok=True)
        return ScreenshotCapture(test_config)

    def test_initialization(self, screenshot_capturer, test_config):
        """Test proper initialization"""
        assert screenshot_capturer.interval == test_config.interval
        assert screenshot_capturer.prefix == test_config.prefix
        assert screenshot_capturer.running is False
        assert screenshot_capturer.screenshot_count == 0

    def test_take_screenshot_fullscreen(self, screenshot_capturer, mock_pyautogui, mock_screenshot):
        """Test taking fullscreen screenshot"""
        with patch("pyautogui.screenshot", return_value=mock_screenshot):
            result = screenshot_capturer.take_screenshot()

        assert result is True
        assert screenshot_capturer.screenshot_count == 1
        mock_screenshot.save.assert_called_once()

    def test_take_screenshot_with_region(self, screenshot_capturer, mock_screenshot):
        """Test taking screenshot with region"""
        screenshot_capturer.region = (100, 100, 800, 600)

        with patch("pyautogui.screenshot", return_value=mock_screenshot) as mock_ss:
            result = screenshot_capturer.take_screenshot()

        assert result is True
        mock_ss.assert_called_once_with(region=(100, 100, 800, 600))
        mock_screenshot.save.assert_called_once()

    def test_take_screenshot_handles_error(self, screenshot_capturer):
        """Test screenshot handles errors gracefully"""
        with patch("pyautogui.screenshot", side_effect=Exception("Screen capture failed")):
            result = screenshot_capturer.take_screenshot()

        assert result is False
        assert screenshot_capturer.screenshot_count == 0

    def test_start_stop(self, screenshot_capturer):
        """Test starting and stopping capture"""
        screenshot_capturer.interval = 0.1  # Fast for testing

        screenshot_capturer.start()
        assert screenshot_capturer.running is True
        assert screenshot_capturer.thread is not None

        screenshot_capturer.stop()
        assert screenshot_capturer.running is False

    def test_pause_resume(self, screenshot_capturer):
        """Test pausing and resuming capture"""
        screenshot_capturer.pause()
        assert screenshot_capturer.paused is True

        screenshot_capturer.resume()
        assert screenshot_capturer.paused is False

    def test_get_status_stopped(self, screenshot_capturer):
        """Test status when stopped"""
        status = screenshot_capturer.get_status()
        assert "Stopped" in status or "⏹️" in status

    def test_get_status_running(self, screenshot_capturer):
        """Test status when running"""
        screenshot_capturer.running = True
        screenshot_capturer.screenshot_count = 5

        status = screenshot_capturer.get_status()
        assert "5" in status
        assert "Running" in status or "▶️" in status

    def test_get_status_paused(self, screenshot_capturer):
        """Test status when paused"""
        screenshot_capturer.running = True
        screenshot_capturer.paused = True

        status = screenshot_capturer.get_status()
        assert "Paused" in status or "⏸️" in status

    def test_reload_config(self, screenshot_capturer, test_config):
        """Test reloading configuration"""
        test_config.interval = 300
        test_config.prefix = "new_prefix"
        test_config.save()

        screenshot_capturer.reload_config()

        assert screenshot_capturer.interval == 300
        assert screenshot_capturer.prefix == "new_prefix"

    def test_upload_to_drive_no_service(self, screenshot_capturer, tmp_path):
        """Test upload when Drive service is not available"""
        screenshot_capturer.drive_service = None

        test_file = tmp_path / "test.png"
        test_file.write_text("fake image")

        result = screenshot_capturer.upload_to_drive(test_file)
        assert result is False

    def test_upload_to_drive_success(self, screenshot_capturer, mock_drive_service, tmp_path):
        """Test successful upload to Drive"""
        screenshot_capturer.drive_service = mock_drive_service
        screenshot_capturer.drive_folder_id = "test-folder-id"

        test_file = tmp_path / "test.png"
        test_file.write_text("fake image")

        with (
            patch("src.screenshot_tray.MediaFileUpload"),
            patch.object(screenshot_capturer.circuit_breaker, "call", return_value=True),
        ):
            result = screenshot_capturer.upload_to_drive(test_file)

        assert result is True

    def test_upload_to_drive_failure(self, screenshot_capturer, mock_drive_service, tmp_path):
        """Test failed upload to Drive"""
        screenshot_capturer.drive_service = mock_drive_service
        screenshot_capturer.drive_folder_id = "test-folder-id"

        test_file = tmp_path / "test.png"
        test_file.write_text("fake image")

        with (
            patch("src.screenshot_tray.MediaFileUpload"),
            patch.object(screenshot_capturer.circuit_breaker, "call", side_effect=Exception("Upload failed")),
        ):
            result = screenshot_capturer.upload_to_drive(test_file)

        assert result is False

    def test_get_drive_status_disabled(self, screenshot_capturer):
        """Test Drive status when disabled"""
        screenshot_capturer.use_gdrive = False
        status = screenshot_capturer.get_drive_status()
        assert status == "Disabled"

    def test_get_drive_status_enabled(self, screenshot_capturer):
        """Test Drive status when enabled"""
        screenshot_capturer.use_gdrive = True
        status = screenshot_capturer.get_drive_status()
        assert status is not None  # Should return circuit breaker status
