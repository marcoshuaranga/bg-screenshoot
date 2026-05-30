@echo off
REM Screenshot Capture System Tray App Starter
echo Starting Screenshot Capture with System Tray...

cd /d "E:\Users\maracudev\DevDrive\hobby\background-screenshot"

REM Start with system tray (with Google Drive)
start "" ".venv\Scripts\pythonw.exe" screenshot_tray.py -i 60 -g

echo.
echo System Tray app started!
echo Look for the camera icon in your system tray (bottom-right corner)
echo Right-click the icon to control the app
echo.
pause
