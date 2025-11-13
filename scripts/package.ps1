Param(
    [string]$Version = "1.0.9"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$AddonRoot = Split-Path -Parent $Root
$Name = "MetahumanToManny"
$Stage = Join-Path $AddonRoot "dist\$Name-$Version"
$Zip = Join-Path $AddonRoot "dist\$Name-$Version.zip"

# Prepare dist
if (-not (Test-Path (Join-Path $AddonRoot 'dist'))) {
    New-Item -ItemType Directory -Path (Join-Path $AddonRoot 'dist') | Out-Null
}

# Clean stage
if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
New-Item -ItemType Directory -Path $Stage | Out-Null

# Copy files excluding caches and dev folders
# Using robocopy for robust copy with excludes
$rc = robocopy $AddonRoot $Stage /E /XD __pycache__ .idea .git dist .github /XF thumbs.db desktop.ini
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }

# Create zip
if (Test-Path $Zip) { Remove-Item -Force $Zip }
Compress-Archive -Path (Join-Path $Stage '*') -DestinationPath $Zip

Write-Host "Packaged to: $Zip"