REM Screenshot Capture - System Tray (reads config from config.yaml)
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """E:\Users\maracudev\DevDrive\hobby\background-screenshot\.venv\Scripts\pythonw.exe"" ""E:\Users\maracudev\DevDrive\hobby\background-screenshot\screenshot_tray.py""", 0, False
Set WshShell = Nothing
