REM Screenshot Capture - Task Manager Control (reads config from config.yaml)
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
projectDir = fso.GetAbsolutePathName(".")
pythonw = """" & projectDir & "\.venv\Scripts\pythonw.exe"""
cmd = pythonw & " -m src.screenshot_capture"
WshShell.Run cmd, 0, False
Set fso = Nothing
Set WshShell = Nothing
