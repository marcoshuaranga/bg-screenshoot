"""Configuration management for Screenshot Capture"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file="config.yaml"):
        self.config_file = Path(config_file)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        """Load and validate configuration from YAML file."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}. "
                "Copy config.example.yaml to config.yaml and adjust the values."
            )

        try:
            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_file}: {e}") from e

        if not isinstance(config, dict):
            raise ValueError(f"Configuration file {self.config_file} must contain a YAML object.")

        self._validate_config(config)
        logger.info(f"✅ Config loaded: {self.config_file}")
        return config

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate the required configuration schema and values."""
        screenshot = config.get("screenshot")
        if not isinstance(screenshot, dict):
            raise ValueError("Missing or invalid 'screenshot' section in config.yaml")

        interval = screenshot.get("interval")
        if not isinstance(interval, int) or interval <= 0:
            raise ValueError("'screenshot.interval' must be a positive integer")

        prefix = screenshot.get("prefix")
        if not isinstance(prefix, str) or not prefix.strip():
            raise ValueError("'screenshot.prefix' must be a non-empty string")

        local_folder = screenshot.get("local_folder")
        if not isinstance(local_folder, str) or not local_folder.strip():
            raise ValueError("'screenshot.local_folder' must be a non-empty path string")

        region = screenshot.get("region")
        if region is not None:
            if not (isinstance(region, list) and len(region) == 4):
                raise ValueError("'screenshot.region' must be null or a list of four integers")
            if not all(isinstance(v, int) and v >= 0 for v in region):
                raise ValueError("'screenshot.region' values must be non-negative integers")

        google_drive = config.get("google_drive")
        if not isinstance(google_drive, dict):
            raise ValueError("Missing or invalid 'google_drive' section in config.yaml")

        enabled = google_drive.get("enabled")
        if not isinstance(enabled, bool):
            raise ValueError("'google_drive.enabled' must be a boolean")

        folder = google_drive.get("folder")
        if not isinstance(folder, str) or not folder.strip():
            raise ValueError("'google_drive.folder' must be a non-empty string")

        error_handling = config.get("error_handling")
        if not isinstance(error_handling, dict):
            raise ValueError("Missing or invalid 'error_handling' section in config.yaml")

        max_retries = error_handling.get("max_retries")
        if not isinstance(max_retries, int) or max_retries <= 0:
            raise ValueError("'error_handling.max_retries' must be a positive integer")

        retry_delay = error_handling.get("retry_delay")
        if not isinstance(retry_delay, int) or retry_delay < 0:
            raise ValueError("'error_handling.retry_delay' must be a non-negative integer")

        circuit_breaker = error_handling.get("circuit_breaker")
        if not isinstance(circuit_breaker, dict):
            raise ValueError("Missing or invalid 'error_handling.circuit_breaker' section in config.yaml")

        for key in ("failure_threshold", "timeout_duration", "success_threshold"):
            value = circuit_breaker.get(key)
            if not isinstance(value, int) or value <= 0:
                raise ValueError(
                    f"'error_handling.circuit_breaker.{key}' must be a positive integer"
                )

    def _save(self, data: dict[str, Any]):
        """Save configuration to YAML file."""
        self._validate_config(data)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"✅ Config saved: {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")

    def save(self):
        """Save current configuration"""
        self._save(self.data)

    def reload(self):
        """Reload configuration from file"""
        self.data = self._load()

    # Screenshot settings
    @property
    def interval(self) -> int:
        return self.data["screenshot"]["interval"]

    @interval.setter
    def interval(self, value: int):
        self.data["screenshot"]["interval"] = value

    @property
    def prefix(self) -> str:
        return self.data["screenshot"]["prefix"]

    @prefix.setter
    def prefix(self, value: str):
        self.data["screenshot"]["prefix"] = value

    @property
    def local_folder(self) -> str:
        return self.data["screenshot"]["local_folder"]

    @local_folder.setter
    def local_folder(self, value: str):
        self.data["screenshot"]["local_folder"] = value

    @property
    def region(self):
        """Get region as tuple or None"""
        region = self.data["screenshot"].get("region")
        if region and isinstance(region, list) and len(region) == 4:
            return tuple(region)
        return None

    @region.setter
    def region(self, value):
        """Set region (tuple/list of 4 ints or None)"""
        if value is None:
            self.data["screenshot"]["region"] = None
        elif isinstance(value, tuple | list) and len(value) == 4:
            self.data["screenshot"]["region"] = list(value)
        else:
            raise ValueError("Region must be (x, y, width, height) or None")

    # Google Drive settings
    @property
    def gdrive_enabled(self) -> bool:
        return self.data["google_drive"]["enabled"]

    @gdrive_enabled.setter
    def gdrive_enabled(self, value: bool):
        self.data["google_drive"]["enabled"] = value

    @property
    def gdrive_folder(self) -> str:
        return self.data["google_drive"]["folder"]

    @gdrive_folder.setter
    def gdrive_folder(self, value: str):
        self.data["google_drive"]["folder"] = value

    # Error handling settings
    @property
    def max_retries(self) -> int:
        return self.data["error_handling"]["max_retries"]

    @property
    def retry_delay(self) -> int:
        return self.data["error_handling"]["retry_delay"]

    @property
    def circuit_failure_threshold(self) -> int:
        return self.data["error_handling"]["circuit_breaker"]["failure_threshold"]

    @property
    def circuit_timeout_duration(self) -> int:
        return self.data["error_handling"]["circuit_breaker"]["timeout_duration"]

    @property
    def circuit_success_threshold(self) -> int:
        return self.data["error_handling"]["circuit_breaker"]["success_threshold"]
