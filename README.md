# Background Screenshot Capture

A command-line tool to automatically take screenshots in the background and save them locally and/or upload to Google Drive.

## Features

✨ **Automatic Screenshots** - Take screenshots at custom intervals
📁 **Local Storage** - Save to a folder on your system
☁️ **Google Drive Upload** - Optionally upload to your Google Drive
🔄 **Smart Error Handling** - Automatic retries with circuit breaker pattern
🖼️ **Region Selection** - Capture full screen or specific area
⚙️ **GUI Configuration** - Easy settings dialog from system tray
📝 **YAML Configuration** - Simple config file for all settings
⏰ **Flexible Scheduling** - Configure intervals from 10 seconds to hours
🏷️ **Timestamped Files** - Each screenshot has a unique timestamp
🎨 **System Tray Integration** - Control from Windows system tray

## Installation

1. Create a virtual environment with a supported Python version (Python 3.13 is recommended for this project):

```bash
uv venv --python 3.13
uv pip install -r requirements.txt
```

> If you use Python 3.14 on Windows, Pillow may fail to build from source during installation.

2. **(Optional)** Setup Google Drive integration:
   - Follow the guide in [docs/GDRIVE_SETUP.md](docs/GDRIVE_SETUP.md)
   - You'll need a `credentials.json` file from Google Cloud Console

## Quick Start - Background Execution

### 🎨 **RECOMMENDED: System Tray**

Double-click: **`start_screenshots_silent.vbs`**

**Features:**

- ✅ **NO abre ventana** - completamente invisible
- 📸 Camera icon appears in system tray (bottom-right)
- ▶️ Right-click icon to Start/Pause/Stop
- ⚙️ **Settings menu** - Configure interval, folders, Google Drive
- 📊 See screenshot count and status
- ❌ Quit from tray menu

### Configuration

**Method 1: GUI Settings (Recommended)**

1. Start the app (double-click `start_screenshots_silent.vbs`)
2. Right-click the system tray icon
3. Select "⚙️ Settings"
4. Configure interval, folders, Google Drive
5. Save and restart the app

**Method 2: Edit config.yaml**
Open `config.yaml` and modify:

```yaml
screenshot:
  interval: 60 # Seconds between screenshots
  prefix: "screenshot" # Filename prefix
  local_folder: "E:/Users/maracudev/OneDrive/Imágenes/BG_Screenshots"

google_drive:
  enabled: true # Enable/disable Google Drive
  folder: "BG_Screenshots" # Google Drive folder name
```

### 🚀 Simple Background (Task Manager Control)

Double-click: **`start_screenshots_on_taskmanager.vbs`**

- ✅ **NO abre ventana** - completamente invisible
- ⚠️ To stop: Task Manager → End "pythonw.exe"

### ⚠️ .bat files (show console briefly)

- `start_screenshots.bat` - Simple background
- `start_screenshots_tray.bat` - System Tray
- Use .vbs files instead for invisible launch

---

## Usage

### Basic Commands

**Take a single screenshot:**

```bash
.\.venv\Scripts\python screenshot_capture.py -s
```

_Saves to: `E:\Users\maracudev\OneDrive\Imágenes\BG_Screenshots`_

**Take screenshots continuously (every 60 seconds):**

```bash
.\.venv\Scripts\python screenshot_capture.py
```

**Custom interval (every 30 seconds):**

```bash
.\.venv\Scripts\python screenshot_capture.py -i 30
```

**Save to a different folder:**

```bash
.\.venv\Scripts\python screenshot_capture.py -f "MyFolder"
```

_Custom folders are saved relative to Desktop_

### Google Drive Upload

**Upload single screenshot to Google Drive:**

```bash
.\.venv\Scripts\python screenshot_capture.py -s -g
```

**System Tray with Google Drive (recommended):**

```bash
.\.venv\Scripts\python screenshot_tray.py -g
```

Double-click `start_screenshots_tray.bat` for easy access.

**Continuous with Google Drive upload:**

```bash
.\.venv\Scripts\python screenshot_capture.py -g -i 60
```

**Custom Google Drive folder:**

```bash
.\.venv\Scripts\python screenshot_capture.py -g -gf "WorkScreenshots"
```

_By default, screenshots upload to a folder named "BG_Screenshots" in your Google Drive_

### Advanced Options

**Take specific number of screenshots:**

```bash
.\.venv\Scripts\python screenshot_capture.py -c 10 -i 30
```

**Custom local folder and prefix:**

```bash
.\.venv\Scripts\python screenshot_capture.py -f "MyScreenshots" -p "capture"
```

## Options

| Option                   | Description                                  | Default                     |
| ------------------------ | -------------------------------------------- | --------------------------- |
| `-i`, `--interval`       | Interval between screenshots (seconds)       | 60                          |
| `-f`, `--folder`         | Custom folder name (relative to Desktop)     | Screenshots (OneDrive path) |
| `-p`, `--prefix`         | Prefix for screenshot filenames              | screenshot                  |
| `-c`, `--count`          | Number of screenshots to take (0 = infinite) | 0                           |
| `-s`, `--single`         | Take a single screenshot and exit            | -                           |
| `-g`, `--gdrive`         | Upload screenshots to Google Drive           | -                           |
| `-gf`, `--gdrive-folder` | Google Drive folder name                     | BG_Screenshots              |

## Examples

```bash
# Take screenshots every 5 minutes
.\.venv\Scripts\python screenshot_capture.py -i 300

# Take 20 screenshots every 10 seconds, upload to Google Drive
.\.venv\Scripts\python screenshot_capture.py -c 20 -i 10 -g

# Single screenshot with custom prefix, upload to custom Drive folder
.\.venv\Scripts\python screenshot_capture.py -s -p "meeting" -g -gf "MeetingCaptures"

# Continuous with both local and cloud storage
.\.venv\Scripts\python screenshot_capture.py -i 120 -g -f "LocalBackup"
```

## Stop the program

Press `Ctrl+C` to stop taking screenshots when running in continuous mode.

For background execution:

- **System Tray**: Right-click icon → Quit
- **Task Manager**: End "pythonw.exe" process

## Logs

All activity is logged to `logs/screenshot_capture.log` with automatic daily rotation:

- 📅 **Daily rotation** - New log file created at midnight
- 📦 **30-day retention** - Keeps last 30 days of logs automatically
- 📝 **Naming format** - Rotated files: `screenshot_capture.log.YYYY-MM-DD`
- 🔍 **Current log** - Always in `screenshot_capture.log` (today)

**Log contents:**

- Screenshot captures
- Google Drive uploads
- Errors and warnings
- Circuit breaker state changes

**Quick view:** Double-click `view_log.bat` to see:

- Last 50 entries from current log
- List of all historical log files

**Log files example:**

```
logs/
├── screenshot_capture.log          ← Current (today)
├── screenshot_capture.log.2026-05-26  ← Yesterday
├── screenshot_capture.log.2026-05-25  ← 2 days ago
└── ...
```

## Error Handling

The app includes robust error handling for Google Drive uploads:

- 🔄 **Automatic retries** (3 attempts with exponential backoff)
- 🔴 **Circuit breaker** - Temporarily disables uploads after repeated failures
- 🟢 **Auto-recovery** - Automatically resumes when service is back
- 📝 **Detailed error logging** - All errors classified and logged
- 💾 **Local backup** - Screenshots ALWAYS saved locally, regardless of Drive status

See [docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md) for detailed information about the error handling system.

**Circuit Breaker Status:**

- Visible in System Tray menu
- Shows "✅ Online", "⚠️ Offline", or "🔄 Testing"
- Manual reset option when offline

## Testing

The project includes a comprehensive test suite with **69% code coverage**.

### Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=. --cov-report=html

# View HTML coverage report
start htmlcov/index.html
```

### Test Coverage

- ✅ Configuration Management (97%)
- ✅ Circuit Breaker Pattern (98%)
- ✅ Error Handling & Retry Logic (100%)
- ✅ Screenshot Capture (100% of testable code)
- ✅ Region Selection (62%)

See [tests/README.md](tests/README.md) for detailed testing documentation.

## Documentation

- 📘 [Google Drive Setup Guide](docs/GDRIVE_SETUP.md) - Complete OAuth setup instructions
- 🔧 [Error Handling System](docs/ERROR_HANDLING.md) - Circuit breaker and retry patterns
- ⚖️ [Authentication Comparison](docs/AUTH_COMPARISON.md) - OAuth vs API Keys vs Service Accounts
- 🔴 [Error 403 Fix](docs/ERROR_403_FIX.md) - Troubleshoot access denied errors
- 🖥️ [Background Execution](docs/BACKGROUND_EXECUTION.md) - Run as background process
- 🐍 [Python Guidelines](docs/PYTHON_GUIDELINES.md) - Code style and best practices
- 🪝 [Pre-commit Guide](docs/PRE_COMMIT_GUIDE.md) - Git hooks setup and usage

## Output

Screenshots are saved as PNG files with timestamps in the format:
`prefix_YYYYMMDD_HHMMSS.png`

Example: `screenshot_20260527_153000.png`
