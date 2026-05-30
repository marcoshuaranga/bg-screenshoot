"""Shared fixtures for tests"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from config_manager import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock config file"""
    config_path = temp_dir / "config.yaml"
    # Use forward slashes for YAML to avoid escape issues
    folder_path = str(temp_dir / "screenshots").replace("\\", "/")
    config_content = f"""
screenshot:
  interval: 60
  prefix: "test_screenshot"
  local_folder: "{folder_path}"
  region: null

google_drive:
  enabled: false
  folder: "TestFolder"

error_handling:
  max_retries: 3
  retry_delay: 1
  circuit_breaker:
    failure_threshold: 3
    timeout_duration: 60
    success_threshold: 2
"""

    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def test_config(mock_config_file, monkeypatch):
    """Create a test config instance"""
    # Change working directory to temp location
    monkeypatch.chdir(mock_config_file.parent)
    config = Config(str(mock_config_file))
    return config


@pytest.fixture
def mock_drive_service():
    """Mock Google Drive service"""
    service = MagicMock()

    # Mock files().list()
    list_result = MagicMock()
    list_result.execute.return_value = {"files": []}
    service.files().list.return_value = list_result

    # Mock files().create()
    create_result = MagicMock()
    create_result.execute.return_value = {"id": "mock-folder-id"}
    service.files().create.return_value = create_result

    return service


@pytest.fixture
def mock_screenshot():
    """Mock PIL Image for screenshot"""
    mock_img = MagicMock()
    mock_img.save = MagicMock()
    return mock_img


@pytest.fixture
def mock_pyautogui(monkeypatch, mock_screenshot):
    """Mock pyautogui module"""
    mock_module = MagicMock()
    mock_module.screenshot.return_value = mock_screenshot
    monkeypatch.setattr("pyautogui.screenshot", mock_module.screenshot)
    return mock_module
