import logging
import pickle
import threading
import time
from datetime import datetime
from enum import Enum
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pyautogui
import pystray
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw
from pystray import MenuItem

from src.config_dialog import ConfigDialog
from src.config_manager import Config
from src.region_selector import RegionSelector

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Setup logging with daily rotation
log_folder = Path(__file__).parent.parent / "logs"
log_folder.mkdir(exist_ok=True)
log_file = log_folder / "screenshot_capture.log"

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Create and configure TimedRotatingFileHandler
# Rotates daily at midnight, keeps 30 days of logs
file_handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",
    interval=1,
    backupCount=30,  # Keep 30 days of logs
    encoding="utf-8",
)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y-%m-%d"  # Adds date to rotated files

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Configure root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class CircuitState(Enum):
    """Circuit Breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Temporarily disabled due to failures
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit Breaker Pattern for Google Drive uploads"""

    def __init__(self, failure_threshold=5, timeout_duration=300, success_threshold=2):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_duration: Seconds to wait before trying again (default: 5 min)
            success_threshold: Consecutive successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("🔄 Circuit breaker: Testing if service recovered...")
            else:
                logger.debug(f"⚠️  Circuit breaker OPEN - Skipping upload (retry in {self._time_until_retry()}s)")
                return False

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout_duration

    def _time_until_retry(self):
        """Calculate seconds until next retry attempt"""
        if self.last_failure_time is None:
            return 0
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, int(self.timeout_duration - elapsed))

    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("✅ Circuit breaker: Service recovered - CLOSED")
        elif self.state == CircuitState.CLOSED:
            self.success_count = 0

    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"🔴 Circuit breaker OPEN - Too many failures. Retry in {self.timeout_duration}s")

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info("🔄 Circuit breaker manually reset")

    def get_status(self):
        """Get current status"""
        if self.state == CircuitState.OPEN:
            return f"⚠️  Offline (retry in {self._time_until_retry()}s)"
        elif self.state == CircuitState.HALF_OPEN:
            return "🔄 Testing connection..."
        else:
            return "✅ Online"


class ErrorType(Enum):
    """Types of upload errors"""

    NETWORK = "network"
    AUTH = "authentication"
    QUOTA = "quota_exceeded"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


def classify_error(exception):
    """Classify error type for better handling"""
    error_msg = str(exception).lower()

    if isinstance(exception, HttpError):
        status = exception.resp.status
        if status == 401 or status == 403:
            if "quota" in error_msg or "limit" in error_msg:
                return ErrorType.QUOTA
            return ErrorType.AUTH
        elif status == 404:
            return ErrorType.PERMISSION
        elif status >= 500:
            return ErrorType.NETWORK

    if "connection" in error_msg or "network" in error_msg or "timeout" in error_msg:
        return ErrorType.NETWORK

    if "auth" in error_msg or "credential" in error_msg or "token" in error_msg:
        return ErrorType.AUTH

    return ErrorType.UNKNOWN


def retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    Retry Pattern with exponential backoff

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_type = classify_error(e)

            # Don't retry on auth or quota errors
            if error_type in [ErrorType.AUTH, ErrorType.QUOTA, ErrorType.PERMISSION]:
                logger.error(f"❌ Non-retryable error ({error_type.value}): {e}")
                raise

            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)  # Exponential backoff
                logger.warning(f"⚠️  Upload failed (attempt {attempt + 1}/{max_retries}): {error_type.value}")
                logger.info(f"🔄 Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"❌ All {max_retries} attempts failed: {e}")
                raise

    raise Exception("Max retries exceeded")


class ScreenshotCapture:
    def __init__(self, config: Config = None):
        # Load or use provided config
        self.config = config if config else Config()

        # Load settings from config
        self.interval = self.config.interval
        self.use_gdrive = self.config.gdrive_enabled
        self.gdrive_folder_name = self.config.gdrive_folder
        self.prefix = self.config.prefix
        self.region = self.config.region  # Screen region or None

        # Runtime state
        self.running = False
        self.paused = False
        self.thread = None
        self.screenshot_count = 0
        self.drive_service = None
        self.drive_folder_id = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_failure_threshold,
            timeout_duration=self.config.circuit_timeout_duration,
            success_threshold=self.config.circuit_success_threshold,
        )

        # Setup paths
        self.screenshot_folder = Path(self.config.local_folder)
        self.screenshot_folder.mkdir(parents=True, exist_ok=True)

        # Setup Google Drive if enabled
        if self.use_gdrive:
            self.setup_google_drive()

    def reload_config(self):
        """Reload configuration and apply changes"""
        logger.info("🔄 Reloading configuration...")
        self.config.reload()
        self.interval = self.config.interval
        self.use_gdrive = self.config.gdrive_enabled
        self.gdrive_folder_name = self.config.gdrive_folder
        self.prefix = self.config.prefix
        self.region = self.config.region
        self.screenshot_folder = Path(self.config.local_folder)
        self.screenshot_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Config reloaded: interval={self.interval}s, gdrive={self.use_gdrive}, region={self.region}")

    def setup_google_drive(self):
        """Setup Google Drive connection"""
        try:
            self.drive_service = self.get_google_drive_service()
            if self.drive_service:
                self.drive_folder_id = self.get_or_create_drive_folder(self.drive_service, self.gdrive_folder_name)
                logger.info(f"✅ Connected to Google Drive folder: {self.gdrive_folder_name}")
        except Exception as e:
            logger.error(f"⚠️  Google Drive setup failed: {e}")
            self.use_gdrive = False

    def get_google_drive_service(self):
        """Authenticate and return Google Drive service"""
        creds = None
        token_path = Path("token.pickle")
        credentials_path = Path("credentials.json")

        if not credentials_path.exists():
            logger.warning("⚠️  credentials.json not found - Google Drive disabled")
            return None

        if token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

        return build("drive", "v3", credentials=creds)

    def get_or_create_drive_folder(self, service, folder_name):
        """Get or create a folder in Google Drive"""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
        items = results.get("files", [])

        if items:
            return items[0]["id"]

        file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        folder = service.files().create(body=file_metadata, fields="id").execute()
        return folder.get("id")

    def upload_to_drive(self, file_path):
        """Upload file to Google Drive with retry logic and circuit breaker"""
        if not self.drive_service or not self.drive_folder_id:
            return False

        def _upload():
            """Inner function for retry mechanism"""
            file_metadata = {"name": file_path.name}
            if self.drive_folder_id:
                file_metadata["parents"] = [self.drive_folder_id]

            media = MediaFileUpload(str(file_path), mimetype="image/png")
            self.drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        try:
            # Use circuit breaker to protect against repeated failures
            self.circuit_breaker.call(lambda: retry_with_backoff(_upload, max_retries=3, base_delay=2))
            return True
        except Exception as e:
            error_type = classify_error(e)
            logger.error(f"❌ Upload failed ({error_type.value}): {e}")
            return False

    def get_drive_status(self):
        """Get Google Drive connection status"""
        if not self.use_gdrive:
            return "Disabled"
        return self.circuit_breaker.get_status()

    def take_screenshot(self):
        """Take a screenshot and save it"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.prefix}_{timestamp}.png"
        filepath = self.screenshot_folder / filename

        try:
            # Take screenshot (full screen or region)
            if self.region:
                screenshot = pyautogui.screenshot(region=self.region)
            else:
                screenshot = pyautogui.screenshot()

            screenshot.save(filepath)
            self.screenshot_count += 1

            status = f"[{self.screenshot_count}] 📸 {filename}"
            if self.region:
                status += " (region)"

            # Upload to Google Drive if enabled
            if self.use_gdrive and self.drive_service and self.upload_to_drive(filepath):
                status += " ☁️"

            logger.info(status)
            return True
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return False

    def capture_loop(self):
        """Main capture loop"""
        logger.info(f"🚀 Started capturing every {self.interval} seconds")
        logger.info(f"💾 Saving to: {self.screenshot_folder}")
        if self.use_gdrive:
            logger.info(f"☁️  Uploading to Google Drive: {self.gdrive_folder_name}")

        while self.running:
            if not self.paused:
                self.take_screenshot()

            # Sleep in small intervals to allow quick stop
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

        logger.info("⏹️  Stopped capturing")

    def start(self):
        """Start capturing"""
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop capturing"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def pause(self):
        """Pause capturing"""
        self.paused = True

    def resume(self):
        """Resume capturing"""
        self.paused = False

    def get_status(self):
        """Get current status"""
        if not self.running:
            status = "⏹️  Stopped"
        elif self.paused:
            status = "⏸️  Paused"
        else:
            status = f"▶️  Running ({self.screenshot_count} screenshots)"

        # Add Drive status if enabled
        if self.use_gdrive:
            drive_status = self.get_drive_status()
            status += f" | Drive: {drive_status}"

        return status


class SystemTrayApp:
    def __init__(self, config: Config = None):
        self.config = config if config else Config()
        self.capturer = ScreenshotCapture(self.config)
        self.icon = None

    def create_icon_image(self):
        """Create a simple icon for the system tray"""
        # Create a 64x64 image with a camera icon
        image = Image.new("RGB", (64, 64), color="white")
        draw = ImageDraw.Draw(image)

        # Draw a simple camera shape
        draw.rectangle([10, 20, 54, 50], fill="blue", outline="darkblue", width=2)
        draw.ellipse([20, 25, 44, 45], fill="lightblue", outline="darkblue", width=2)
        draw.rectangle([25, 15, 39, 20], fill="blue", outline="darkblue", width=1)

        return image

    def on_start(self, icon, item):
        """Start capturing"""
        self.capturer.start()
        self.update_menu()

    def on_stop(self, icon, item):
        """Stop capturing"""
        self.capturer.stop()
        self.update_menu()

    def on_pause(self, icon, item):
        """Pause capturing"""
        self.capturer.pause()
        self.update_menu()

    def on_resume(self, icon, item):
        """Resume capturing"""
        self.capturer.resume()
        self.update_menu()

    def on_reset_drive(self, icon, item):
        """Reset Google Drive circuit breaker"""
        self.capturer.circuit_breaker.reset()
        logger.info("🔄 User manually reset Google Drive connection")
        self.update_menu()

    def on_settings(self, icon, item):
        """Open settings dialog"""

        def show_dialog():
            dialog = ConfigDialog(self.config, on_save_callback=self._on_config_saved)
            dialog.show()

        # Run dialog in separate thread to avoid blocking
        threading.Thread(target=show_dialog, daemon=True).start()

    def on_select_region(self, icon, item):
        """Open region selector"""

        def select_region():
            selector = RegionSelector()
            region = selector.select_region()

            if region is not None:
                # Save region to config
                self.config.region = region
                self.config.save()
                self.capturer.reload_config()

                if region:
                    logger.info(f"✅ Region set: {region}")
                else:
                    logger.info("✅ Full screen mode enabled")
            else:
                logger.info("Region selection cancelled")

            # Update menu to reflect changes
            self.update_menu()

        # Run in separate thread
        threading.Thread(target=select_region, daemon=True).start()

    def _on_config_saved(self):
        """Callback when configuration is saved"""
        # Note: App needs restart for changes to take effect
        pass

    def on_status(self, icon, item):
        """Show status"""
        return self.capturer.get_status()

    def on_quit(self, icon, item):
        """Quit application"""
        self.capturer.stop()
        icon.stop()

    def update_menu(self):
        """Update menu based on current state"""
        if self.icon:
            self.icon.menu = self.create_menu()

    def create_menu(self):
        """Create menu based on current state"""
        status_text = self.capturer.get_status()

        menu_items = [
            MenuItem(status_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
        ]

        if not self.capturer.running:
            menu_items.append(MenuItem("▶️  Start", self.on_start))
        else:
            if self.capturer.paused:
                menu_items.append(MenuItem("▶️  Resume", self.on_resume))
            else:
                menu_items.append(MenuItem("⏸️  Pause", self.on_pause))
            menu_items.append(MenuItem("⏹️  Stop", self.on_stop))

        menu_items.extend(
            [
                pystray.Menu.SEPARATOR,
                MenuItem(f"📁 Local: {self.capturer.screenshot_folder.name}", lambda: None, enabled=False),
            ]
        )

        # Region status
        if self.capturer.region:
            region_text = f"🖼️  Region: {self.capturer.region[2]}x{self.capturer.region[3]}"
        else:
            region_text = "🖼️  Region: Full screen"
        menu_items.append(MenuItem(region_text, lambda: None, enabled=False))

        if self.capturer.use_gdrive:
            drive_status_text = f"☁️  Drive: {self.capturer.get_drive_status()}"
            menu_items.append(MenuItem(drive_status_text, lambda: None, enabled=False))

            # Add reset option if circuit is open
            if self.capturer.circuit_breaker.state == CircuitState.OPEN:
                menu_items.append(MenuItem("🔄 Reset Drive Connection", self.on_reset_drive))

        menu_items.extend(
            [
                pystray.Menu.SEPARATOR,
                MenuItem("🖼️  Select Region", self.on_select_region),
                MenuItem("⚙️  Settings", self.on_settings),
                MenuItem("❌ Quit", self.on_quit),
            ]
        )

        return pystray.Menu(*menu_items)

    def run(self):
        """Run the system tray application"""
        icon_image = self.create_icon_image()
        self.icon = pystray.Icon("screenshot_capture", icon_image, "Screenshot Capture", menu=self.create_menu())

        # Auto-start capturing
        self.capturer.start()

        logger.info("🎨 System Tray app started!")
        logger.info("📸 Look for the camera icon in your system tray")
        logger.info("Right-click the icon to control the app")

        self.icon.run()


if __name__ == "__main__":
    # Load configuration
    config = Config()
    logger.info(f"📋 Loaded config: interval={config.interval}s, gdrive={config.gdrive_enabled}")

    # Create and run system tray app
    app = SystemTrayApp(config)
    app.run()
