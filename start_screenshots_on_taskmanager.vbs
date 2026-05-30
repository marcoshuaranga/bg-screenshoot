REM Screenshot Capture - Task Manager Control (reads config from config.yaml)
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """E:\Users\maracudev\DevDrive\hobby\background-screenshot\.venv\Scripts\pythonw.exe"" ""E:\Users\maracudev\DevDrive\hobby\background-screenshot\screenshot_capture.py"" -i 60 -g", 0, False
Set WshShell = Nothing
