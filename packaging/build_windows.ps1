param(
    [string]$Version = "1.0.0"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Dist = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
python -m pip install -r (Join-Path $Root "requirements-build.txt")
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name "FocusTasks" `
    --distpath $Dist `
    --workpath (Join-Path $Root "build/windows") `
    --specpath (Join-Path $Root "build") `
    (Join-Path $Root "focus_tasks.py")
Write-Host "Build $Version completado: $Dist\FocusTasks.exe"
