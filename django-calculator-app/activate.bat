@echo off
REM Project activation wrapper for cmd.exe
if exist "senv\Scripts\activate.bat" (
  call senv\Scripts\activate.bat
) else (
  echo Virtual environment not found at senv\Scripts\activate.bat
)
