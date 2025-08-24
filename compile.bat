@echo off
REM --- Clean old builds ---
rmdir /s /q build
rmdir /s /q dist
if exist "ViolaLauncher.exe" del "ViolaLauncher.exe"

REM --- Build launcher ---
python -m PyInstaller ^
    --noconsole ^
    --windowed ^
    --onefile ^
    --name "ViolaLauncher" ^
    --icon "src/assets/logo.ico" ^
    --add-data "src/assets;assets" ^
    --add-data "src/updater.py;." ^
    --hidden-import keyboard ^
    src/viola_launcher.py

pause

