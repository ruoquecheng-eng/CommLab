$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Venv = Join-Path $Root ".desktop-build"

if (-not (Test-Path $Venv)) {
    py -3.12 -m venv $Venv
}

$Python = Join-Path $Venv "Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -e "$Root[desktop-build]"

Push-Location $Root
try {
    & $Python -m pytest -q tests/test_desktop_launcher.py
    & $Python -m PyInstaller --noconfirm --clean desktop/CommLabDesktop.spec
    if (Test-Path "desktop-artifacts/CommLab-Windows-x64.zip") {
        Remove-Item "desktop-artifacts/CommLab-Windows-x64.zip" -Force
    }
    New-Item -ItemType Directory -Force "desktop-artifacts" | Out-Null
    Compress-Archive -Path "dist/CommLab/*" -DestinationPath "desktop-artifacts/CommLab-Windows-x64.zip"
    $Iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($Iscc) {
        & $Iscc.Source "desktop/installer.iss"
    } else {
        Write-Warning "Inno Setup was not found; portable ZIP was built, installer was skipped."
    }
} finally {
    Pop-Location
}

Write-Host "Desktop artifacts are in $Root\desktop-artifacts"
