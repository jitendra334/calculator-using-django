@echo off
REM Activate virtualenv if it exists and run Django development server
if exist "senv\Scripts\activate.bat" (
  call senv\Scripts\activate.bat
) else (
  echo Virtual environment not found; running with system Python
)
python manage.py runserver
