# PowerShell script to activate virtual environment and run Django development server
$venv = Join-Path $PSScriptRoot 'senv\Scripts\Activate.ps1'
if (Test-Path $venv) {
    & $venv
} else {
    Write-Host "Virtual environment activate script not found; using system Python"
}
python manage.py runserver
