"""Tests for config_manager.py"""

from pathlib import Path

import pytest

from src.config_manager import DEFAULT_CONFIG, Config


class TestConfig:
    """Test Config class"""

    def test_load_default_config(self, temp_dir, monkeypatch):
        """Test loading default config when file doesn't exist"""
        monkeypatch.chdir(temp_dir)
        config_path = temp_dir / "config.yaml"

        config = Config(str(config_path))

        assert config.interval == DEFAULT_CONFIG["screenshot"]["interval"]
        assert config.prefix == DEFAULT_CONFIG["screenshot"]["prefix"]
        assert config_path.exists()  # Should create file

    def test_load_existing_config(self, test_config):
        """Test loading existing config file"""
        assert test_config.interval == 60
        assert test_config.prefix == "test_screenshot"  # From our fixture
        assert test_config.gdrive_enabled is False

    def test_save_config(self, test_config, temp_dir):
        """Test saving configuration changes"""
        test_config.interval = 120
        test_config.prefix = "new_prefix"
        test_config.save()

        # Reload and verify
        new_config = Config(str(temp_dir / "config.yaml"))
        assert new_config.interval == 120
        assert new_config.prefix == "new_prefix"

    def test_reload_config(self, test_config, temp_dir):
        """Test reloading configuration from file"""
        # Modify file directly
        config_path = temp_dir / "config.yaml"
        content = config_path.read_text()
        content = content.replace("interval: 60", "interval: 300")
        config_path.write_text(content)

        # Reload
        test_config.reload()
        assert test_config.interval == 300

    def test_interval_property(self, test_config):
        """Test interval getter and setter"""
        test_config.interval = 180
        assert test_config.interval == 180
        assert test_config.data["screenshot"]["interval"] == 180

    def test_prefix_property(self, test_config):
        """Test prefix getter and setter"""
        test_config.prefix = "custom"
        assert test_config.prefix == "custom"

    def test_gdrive_enabled_property(self, test_config):
        """Test Google Drive enabled property"""
        test_config.gdrive_enabled = True
        assert test_config.gdrive_enabled is True
        assert test_config.data["google_drive"]["enabled"] is True

    def test_gdrive_folder_property(self, test_config):
        """Test Google Drive folder property"""
        test_config.gdrive_folder = "NewFolder"
        assert test_config.gdrive_folder == "NewFolder"

    def test_region_property_none(self, test_config):
        """Test region property when None"""
        test_config.region = None
        assert test_config.region is None

    def test_region_property_tuple(self, test_config):
        """Test region property with tuple"""
        test_config.region = (100, 100, 800, 600)
        assert test_config.region == (100, 100, 800, 600)
        assert isinstance(test_config.data["screenshot"]["region"], list)

    def test_region_property_list(self, test_config):
        """Test region property with list"""
        test_config.region = [50, 50, 400, 300]
        assert test_config.region == (50, 50, 400, 300)

    def test_region_property_invalid(self, test_config):
        """Test region property with invalid value"""
        with pytest.raises(ValueError):
            test_config.region = (100, 100)  # Only 2 values

        with pytest.raises(ValueError):
            test_config.region = "invalid"

    def test_error_handling_properties(self, test_config):
        """Test error handling configuration properties"""
        assert test_config.max_retries == 3
        assert test_config.retry_delay == 1  # From our fixture
        assert test_config.circuit_failure_threshold == 3
        assert test_config.circuit_timeout_duration == 60
        assert test_config.circuit_success_threshold == 2

    def test_corrupted_config_loads_default(self, temp_dir, monkeypatch):
        """Test that corrupted config file loads defaults"""
        monkeypatch.chdir(temp_dir)
        config_path = temp_dir / "config.yaml"
        config_path.write_text("invalid: yaml: content: [[[")

        config = Config(str(config_path))

        # Should load defaults instead of crashing
        assert config.interval == DEFAULT_CONFIG["screenshot"]["interval"]
