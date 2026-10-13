@echo off
setlocal
cd /d "%~dp0"

set "PYTHONW=.venv\Scripts\pythonw.exe"
if exist "%PYTHONW%" goto launch

set "UV=uv"
where uv >nul 2>nul
if not errorlevel 1 goto setup

set "UV=%USERPROFILE%\.local\bin\uv.exe"
if exist "%UV%" goto setup

echo Missing project environment and uv.
echo Install uv, then run this launcher again.
pause
exit /b 1

:setup
"%UV%" sync --extra dev
if errorlevel 1 (
    echo Environment setup failed.
    pause
    exit /b 1
)

:launch
start "" "%PYTHONW%" "app.py"
