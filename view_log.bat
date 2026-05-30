@echo off
REM View Screenshot Capture Log
echo ====================================
echo Screenshot Capture - Activity Log
echo ====================================
echo.

cd /d "E:\Users\maracudev\DevDrive\hobby\background-screenshot"

if not exist "logs\screenshot_capture.log" (
    echo No log file found yet.
    echo The log will be created when you run the app.
    echo.
    pause
    exit /b
)

echo Current log file: screenshot_capture.log
echo.
echo Last 50 entries:
echo.
powershell -Command "Get-Content logs\screenshot_capture.log -Tail 50"

echo.
echo.
echo ====================================
echo Other log files (by date):
echo ====================================
powershell -Command "Get-ChildItem logs\screenshot_capture.log.* | Sort-Object LastWriteTime -Descending | Select-Object Name, @{N='Size';E={'{0:N2} KB' -f ($_.Length/1KB)}}, LastWriteTime | Format-Table -AutoSize"

echo.
echo ====================================
echo Press any key to exit...
pause >nul
