$ErrorActionPreference = 'Stop'

# Folder where this script lives
$src = Split-Path -Parent $MyInvocation.MyCommand.Path

$initPath = Join-Path $src '__init__.py'
$text     = Get-Content $initPath -Raw

$regex = '"version"\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)'
if ($text -notmatch $regex) {
    Write-Error "Version not found in __init__.py"
    exit 1
}

$version = '{0}.{1}.{2}' -f $Matches[1], $Matches[2], $Matches[3]
$zipPath = Join-Path $src ("MetahumanToManny_{0}.zip" -f $version)

$itemsToZip = @(
    (Join-Path $src 'operators'),
    (Join-Path $src 'ui'),
    (Join-Path $src '__init__.py'),
    (Join-Path $src 'blender_manifest.toml')
)

if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

Compress-Archive -Path $itemsToZip -DestinationPath $zipPath
