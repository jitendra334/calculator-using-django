# Run the Django dev server from repository root (handles inner project path)
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location (Join-Path $scriptRoot 'django-calculator-app')
$venv = Join-Path (Get-Location) 'senv\Scripts\Activate.ps1'
if (Test-Path $venv) {
    . $venv
} else {
    Write-Host "Virtual environment not found; running with system Python"
}
# default address
if ($args.Count -eq 0) { $addr = '127.0.0.1:8000' } else { $addr = $args -join ' ' }
python manage.py runserver $addr
Pop-Location
