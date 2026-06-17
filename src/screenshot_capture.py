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

from src.config_manager import Config

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


def create_screenshot_folder(folder_path: str | Path) -> Path:
    """Create and return a screenshot folder from a validated config path."""
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


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
    parser = argparse.ArgumentParser(description="Take screenshots using the validated local configuration")
    parser.add_argument("-i", "--interval", type=int, default=None, help="Override interval in seconds")
    parser.add_argument("-f", "--folder", type=str, default=None, help="Override output folder")
    parser.add_argument("-p", "--prefix", type=str, default=None, help="Override screenshot prefix")
    parser.add_argument("-c", "--count", type=int, default=None, help="Number of screenshots to take")
    parser.add_argument("-s", "--single", action="store_true", help="Take a single screenshot and exit")
    parser.add_argument("-g", "--gdrive", action="store_true", help="Upload screenshots to Google Drive")
    parser.add_argument("-gf", "--gdrive-folder", type=str, default=None, help="Override Google Drive folder")

    args = parser.parse_args()

    config = Config()

    interval = args.interval if args.interval is not None else config.interval
    prefix = args.prefix if args.prefix is not None else config.prefix
    folder = args.folder if args.folder is not None else config.local_folder
    use_gdrive = args.gdrive or config.gdrive_enabled
    drive_folder = args.gdrive_folder if args.gdrive_folder is not None else config.gdrive_folder
    count = args.count if args.count is not None else 0

    # Setup Google Drive if enabled
    drive_service = None
    drive_folder_id = None
    if use_gdrive:
        print("🔐 Authenticating with Google Drive...")
        drive_service = get_google_drive_service()
        if not drive_service:
            print("❌ Google Drive authentication failed. Continuing without upload.")
        else:
            print("✅ Connected to Google Drive")
            drive_folder_id = get_or_create_drive_folder(drive_service, drive_folder)
            print(f"📁 Using Google Drive folder: {drive_folder}")

    # Create screenshot folder
    screenshot_folder = create_screenshot_folder(folder)
    print(f"💾 Local folder: {screenshot_folder}")

    if args.single:
        filepath = take_screenshot(screenshot_folder, prefix, use_gdrive, drive_service, drive_folder_id)
        status = "📸 Screenshot saved"
        if use_gdrive and drive_service:
            status += " and uploaded to Google Drive"
        print(f"{status}: {filepath.name}")
        return

    # Continuous mode
    print(f"Taking screenshots every {interval} seconds...")
    print("Press Ctrl+C to stop")

    captured = 0
    try:
        while True:
            filepath = take_screenshot(screenshot_folder, prefix, use_gdrive, drive_service, drive_folder_id)
            captured += 1
            status = f"[{captured}] 📸 {filepath.name}"
            if use_gdrive and drive_service:
                status += " ☁️"
            print(status)

            if count > 0 and captured >= count:
                print(f"\n✅ Completed {captured} screenshots")
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopped. Total screenshots taken: {captured}")


if __name__ == "__main__":
    main()
