# Run updater
Write-Output "Checking for updates..."
& powershell -ExecutionPolicy Bypass -File "update.ps1"

# Run the actual launcher EXE
$exePath = "dist\viola_launcher.exe"
if (Test-Path $exePath)) {
    Start-Process $exePath
} else {
    Write-Error "Executable not found: $exePath"
    exit 1
}