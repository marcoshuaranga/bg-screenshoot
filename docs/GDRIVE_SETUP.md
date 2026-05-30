# Google Drive Setup Guide

Follow these steps to enable Google Drive integration:

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select an existing project
3. Give it a name like "Screenshot Uploader"

## 2. Enable Google Drive API

1. In your project, go to **"APIs & Services"** > **"Library"**
2. Search for **"Google Drive API"**
3. Click on it and press **"Enable"**

## 3. Configure OAuth Consent Screen

**IMPORTANT:** This step is required before creating credentials.

1. Go to **"APIs & Services"** > **"OAuth consent screen"**
2. Choose user type:
   - **"External"** - For personal Google accounts
   - **"Internal"** - Only if you have Google Workspace
3. Click **"Create"**

### Fill in the OAuth consent screen information:

**App information:**
- **App name:** `Screenshot Uploader` (or your preferred name)
- **User support email:** Your email address
- **App logo:** (Optional) Can skip for personal use

**App domain:** (Optional for testing)
- Can leave blank for personal use

**Developer contact information:**
- **Email addresses:** Your email address

4. Click **"Save and Continue"**

**Scopes page:**
- Click **"Add or Remove Scopes"**
- Search for: `drive.file`
- Check: `.../auth/drive.file` (Create/edit/delete only the files you use)
- Click **"Update"** then **"Save and Continue"**

**Test users:** (Important for External apps)
- Click **"+ ADD USERS"**
- Enter your Gmail address (the one you'll use to upload screenshots)
- Click **"Add"** then **"Save and Continue"**

5. Review the summary and click **"Back to Dashboard"**

## 4. Create OAuth Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**
3. Select application type:
   - Application type: **"Desktop app"**
   - Name: `Screenshot Uploader Desktop`
   - Click **"Create"**
4. Click **"Download JSON"** on the credentials you just created
5. A `client_secret_xxxxx.json` file will be downloaded

## 5. Setup credentials.json

1. Rename the downloaded file from `client_secret_xxxxx.json` to **`credentials.json`**
2. Move it to your project folder:
   ```
   background-screenshot/
   ├── credentials.json  ← Put it here
   ├── screenshot_capture.py
   └── requirements.txt
   ```

## 6. First Run (Authentication)

When you first run with `-g` flag:

```bash
.\.venv\Scripts\python screenshot_capture.py -s -g
```

1. A browser window will open
2. Select your Google account
3. Click **"Advanced"** > **"Go to [App name] (unsafe)"**
4. Click **"Allow"** to grant permissions
5. The browser will show "The authentication flow has completed"

A `token.pickle` file will be created to store your authentication for future runs.

**Note:** If you see "Google hasn't verified this app" warning:
- This is normal for personal projects
- Click **"Advanced"** at the bottom
- Click **"Go to Screenshot Uploader (unsafe)"**
- This is safe because it's your own app

## 7. Verify Setup

Test with a single screenshot:
```bash
.\.venv\Scripts\python screenshot_capture.py -s -g
```

You should see:
```
🔐 Authenticating with Google Drive...
✅ Connected to Google Drive
📁 Using Google Drive folder: Screenshots
💾 Local folder: C:\Users\YourName\Screenshots
📸 Screenshot saved and uploaded to Google Drive: screenshot_20260527_123456.png
```

## Troubleshooting

### Common Issues:

**"credentials.json not found"**
- Make sure the file is renamed correctly (not `client_secret_xxxxx.json`)
- File must be in the project directory

**"Authentication fails"**
- Delete `token.pickle` and try again
- Make sure you added yourself as a test user in OAuth consent screen

**"Access blocked: This app isn't verified"**
- Go back to OAuth consent screen and add your email as a test user
- Or click "Advanced" > "Go to [App] (unsafe)" during login

**"Permission denied"**
- Make sure you clicked "Allow" during authentication
- Check that you selected the correct Google account

**"Invalid scope" error**
- Go back to OAuth consent screen > Scopes
- Add the `drive.file` scope

## Publishing Status (Optional)

Your app starts in **"Testing"** mode, which:
- ✅ Works perfectly for personal use
- ✅ Allows up to 100 test users
- ❌ Shows "unverified app" warning (can be bypassed)

To remove the warning (optional):
1. Go to OAuth consent screen
2. Click **"Publish App"**
3. Note: Requires Google verification process for production

For personal use, staying in **Testing** mode is recommended and sufficient.

## Security Notes

- Keep `credentials.json` and `token.pickle` private
- Don't commit them to version control (already in .gitignore)
- These files give access to your Google Drive
- The app only has access to files it creates (drive.file scope)
