@echo off
REM Screenshot Capture Background Starter
echo Starting Screenshot Capture in background...

cd /d "E:\Users\maracudev\DevDrive\hobby\background-screenshot"

REM Start in background without console window
start "" ".venv\Scripts\pythonw.exe" screenshot_capture.py -i 60 -g

echo Screenshot capture started!
echo.
echo To stop: Open Task Manager and end "pythonw.exe" process
echo.
pause
