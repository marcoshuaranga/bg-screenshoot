REM Screenshot Capture - System Tray (reads config from config.yaml)
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
projectDir = fso.GetAbsolutePathName(".")
pythonw = """" & projectDir & "\.venv\Scripts\pythonw.exe"""
cmd = pythonw & " -m src.screenshot_tray"
WshShell.Run cmd, 0, False
Set fso = Nothing
Set WshShell = Nothing
