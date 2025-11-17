@echo off
setlocal

pushd "%~dp0"

rem Read version from __init__.py via PowerShell
for /f "usebackq delims=" %%V in (`
  powershell -NoLogo -NoProfile -Command ^
    "$t = Get-Content '__init__.py' -Raw;" ^
    "$m = [regex]::Match($t, '""version""\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)');" ^
    "if($m.Success){ '{0}.{1}.{2}' -f $m.Groups[1].Value,$m.Groups[2].Value,$m.Groups[3].Value }"
`) do set "VERSION=%%V"

if not defined VERSION goto :eof

powershell -NoLogo -NoProfile -Command ^
  "Compress-Archive -Path 'operators','ui','__init__.py','blender_manifest.toml' -DestinationPath ('MetahumanToManny_%VERSION%.zip') -Force"

popd
endlocal
