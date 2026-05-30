import argparse
import pickle
import time
from datetime import datetime
from pathlib import Path

import pyautogui
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_google_drive_service():
    """Authenticate and return Google Drive service"""
    creds = None
    token_path = Path("token.pickle")
    credentials_path = Path("credentials.json")

    if not credentials_path.exists():
        print("\n⚠️  ERROR: credentials.json not found!")
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Drive API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download and save as 'credentials.json' in this directory")
        return None

    # Load existing token
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def get_or_create_drive_folder(service, folder_name):
    """Get or create a folder in Google Drive"""
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    items = results.get("files", [])

    if items:
        return items[0]["id"]

    # Create new folder
    file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")


def upload_to_drive(service, file_path, folder_id=None):
    """Upload file to Google Drive"""
    file_metadata = {"name": file_path.name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(file_path), mimetype="image/png")
    file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()

    return file.get("webViewLink")


def get_default_screenshot_path():
    """Get the default screenshot path"""
    # Default to specific OneDrive path
    default_path = Path("E:/Users/maracudev/OneDrive/Imágenes/BG_Screenshots")

    # Create directory if it doesn't exist
    default_path.mkdir(parents=True, exist_ok=True)

    return default_path


def get_desktop_path():
    """Get the desktop path for Windows (fallback)"""
    # Try common desktop paths
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        # Try OneDrive Desktop
        desktop = Path.home() / "OneDrive" / "Desktop"
    if not desktop.exists():
        # Try local user desktop
        desktop = Path.home() / "OneDrive" / "Escritorio"  # Spanish
    if not desktop.exists():
        # Fallback to user home
        desktop = Path.home()
    return desktop


def create_screenshot_folder(folder_name="Screenshots"):
    """Create a folder on desktop if it doesn't exist"""
    # If folder_name is "Screenshots" (default), use the default OneDrive path
    if folder_name == "Screenshots":
        return get_default_screenshot_path()

    # If it's an absolute path, use it directly
    if Path(folder_name).is_absolute():
        folder_path = Path(folder_name)
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    # Otherwise, create in desktop
    desktop_path = get_desktop_path()
    screenshot_folder = desktop_path / folder_name
    screenshot_folder.mkdir(parents=True, exist_ok=True)
    return screenshot_folder


def take_screenshot(save_folder, prefix="screenshot", upload_to_gdrive=False, drive_service=None, drive_folder_id=None):
    """Take a screenshot and save it with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = save_folder / filename

    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    # Upload to Google Drive if enabled
    if upload_to_gdrive and drive_service:
        try:
            upload_to_drive(drive_service, filepath, drive_folder_id)
        except Exception as e:
            print(f"  ⚠️  Failed to upload to Google Drive: {e}")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Take screenshots in the background and save to desktop folder")
    parser.add_argument(
        "-i", "--interval", type=int, default=60, help="Interval between screenshots in seconds (default: 60)"
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default="Screenshots",
        help="Folder name on desktop to save screenshots (default: Screenshots)",
    )
    parser.add_argument(
        "-p", "--prefix", type=str, default="screenshot", help="Prefix for screenshot filenames (default: screenshot)"
    )
    parser.add_argument(
        "-c", "--count", type=int, default=0, help="Number of screenshots to take (0 for infinite, default: 0)"
    )
    parser.add_argument("-s", "--single", action="store_true", help="Take a single screenshot and exit")
    parser.add_argument("-g", "--gdrive", action="store_true", help="Upload screenshots to Google Drive")
    parser.add_argument(
        "-gf",
        "--gdrive-folder",
        type=str,
        default="BG_Screenshots",
        help="Google Drive folder name (default: BG_Screenshots)",
    )

    args = parser.parse_args()

    # Setup Google Drive if enabled
    drive_service = None
    drive_folder_id = None
    if args.gdrive:
        print("🔐 Authenticating with Google Drive...")
        drive_service = get_google_drive_service()
        if not drive_service:
            print("❌ Google Drive authentication failed. Continuing without upload.")
        else:
            print("✅ Connected to Google Drive")
            drive_folder_id = get_or_create_drive_folder(drive_service, args.gdrive_folder)
            print(f"📁 Using Google Drive folder: {args.gdrive_folder}")

    # Create screenshot folder
    screenshot_folder = create_screenshot_folder(args.folder)
    print(f"💾 Local folder: {screenshot_folder}")

    if args.single:
        # Take a single screenshot
        filepath = take_screenshot(screenshot_folder, args.prefix, args.gdrive, drive_service, drive_folder_id)
        status = "📸 Screenshot saved"
        if args.gdrive and drive_service:
            status += " and uploaded to Google Drive"
        print(f"{status}: {filepath.name}")
        return

    # Continuous mode
    print(f"Taking screenshots every {args.interval} seconds...")
    print("Press Ctrl+C to stop")

    count = 0
    try:
        while True:
            filepath = take_screenshot(screenshot_folder, args.prefix, args.gdrive, drive_service, drive_folder_id)
            count += 1
            status = f"[{count}] 📸 {filepath.name}"
            if args.gdrive and drive_service:
                status += " ☁️"
            print(status)

            if args.count > 0 and count >= args.count:
                print(f"\n✅ Completed {count} screenshots")
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopped. Total screenshots taken: {count}")


if __name__ == "__main__":
    main()
