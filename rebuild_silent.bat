@echo off
REM --- Clean old builds ---
rmdir /s /q build
rmdir /s /q dist
del violalauncher.spec >nul 2>&1

REM --- Rebuild EXE silently ---
start /min "" python -m PyInstaller --onefile --windowed --icon=assets/logo.ico violalauncher.py

REM --- Optional: Clear Windows icon cache silently ---
start /min "" ie4uinit.exe -ClearIconCache

exit
