@echo off
REM Run the Django dev server from repository root (handles inner project path)
pushd "%~dp0django-calculator-app"
if exist "senv\Scripts\activate.bat" (
  call senv\Scripts\activate.bat
) else (
  echo Virtual environment not found; running with system Python
)
REM allow optional port/addr arg, default to 127.0.0.1:8000
if "%~1"=="" (
  set ADDR=127.0.0.1:8000
) else (
  set ADDR=%~1
)
python manage.py runserver %ADDR%
popd
