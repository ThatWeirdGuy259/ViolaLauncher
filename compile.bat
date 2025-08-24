@echo off
REM --- Clean old builds ---
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist output rmdir /s /q output
if exist "ViolaLauncher.exe" del "ViolaLauncher.exe"

REM --- Recreate output folder ---
mkdir output

REM --- Build launcher ---
pyinstaller ^
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
