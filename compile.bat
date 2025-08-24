@echo off
REM -------------------------
REM ViolaLauncher Build Script
REM -------------------------

REM --- Set output variables ---
set BUILD_DIR=build
set DIST_DIR=dist
set OUTPUT_EXE=ViolaLauncher.exe

REM --- Clean old builds ---
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%OUTPUT_EXE%" del "%OUTPUT_EXE%"

REM --- Build launcher with PyInstaller ---
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

REM --- Build complete ---
if %ERRORLEVEL% EQU 0 (
    echo Build successful!
) else (
    echo Build failed with exit code %ERRORLEVEL%
)

pause
