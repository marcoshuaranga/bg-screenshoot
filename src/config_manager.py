"""Configuration management for Screenshot Capture"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "screenshot": {
        "interval": 60,
        "prefix": "screenshot",
        "local_folder": "E:/Users/maracudev/OneDrive/Imágenes/BG_Screenshots",
        "region": None,  # (x, y, width, height) or None for fullscreen
    },
    "google_drive": {"enabled": True, "folder": "BG_Screenshots"},
    "error_handling": {
        "max_retries": 3,
        "retry_delay": 2,
        "circuit_breaker": {"failure_threshold": 5, "timeout_duration": 300, "success_threshold": 2},
    },
}


class Config:
    def __init__(self, config_file="config.yaml"):
        self.config_file = Path(config_file)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            logger.info(f"Creating default config: {self.config_file}")
            self._save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"✅ Config loaded: {self.config_file}")
                return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return DEFAULT_CONFIG.copy()

    def _save(self, data: dict[str, Any]):
        """Save configuration to YAML file"""
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
