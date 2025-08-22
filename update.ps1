param(
    [string]$Repo = "ThatWeirdGuy259/ViolaLauncher",
    [string]$CurrentVersionFile = "version.txt",
    [string]$UpdateDir = "updates",
    [string]$DistDir = "dist"
)

# Ensure updates directory exists
if (-not (Test-Path $UpdateDir)) {
    New-Item -ItemType Directory -Path $UpdateDir | Out-Null
}

# Read current version
$currentVersion = ""
if (Test-Path $CurrentVersionFile) {
    $currentVersion = Get-Content $CurrentVersionFile -Raw
}

# Fetch latest.json from GitHub release
$latestUrl = "https://github.com/$Repo/releases/latest/download/latest.json"
Write-Output "Fetching $latestUrl ..."
try {
    $latest = Invoke-RestMethod -Uri $latestUrl
} catch {
    Write-Error "Failed to fetch update info."
    exit 1
}

$latestVersion = $latest.version
$downloadUrl   = $latest.url
$sha256        = $latest.sha256

if ($latestVersion -eq $currentVersion) {
    Write-Output "Already up to date (v$currentVersion)."
    exit 0
}

Write-Output "New version available: $latestVersion (current: $currentVersion)"
$zipPath = Join-Path $UpdateDir ("ViolaLauncher-$latestVersion.zip")

# Download new version
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

# Verify SHA256
$hash = Get-FileHash $zipPath -Algorithm SHA256
if ($hash.Hash -ne $sha256) {
    Write-Error "SHA256 mismatch! Update aborted."
    exit 1
}

# Extract update into dist/
Expand-Archive -Path $zipPath -DestinationPath $DistDir -Force

# Save version
$latestVersion | Set-Content $CurrentVersionFile

Write-Output "Updated to v$latestVersion successfully."
exit 0
