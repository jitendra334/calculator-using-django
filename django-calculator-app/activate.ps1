# Project activation wrapper — dot-source to keep env active in current shell
$venv = Join-Path $PSScriptRoot 'senv\Scripts\Activate.ps1'
if (Test-Path $venv) {
    . $venv
} else {
    Write-Host "Virtual environment activate script not found at $venv"
}
