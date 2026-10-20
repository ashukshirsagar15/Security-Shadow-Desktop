@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Security Shadow Setup

echo.
echo ========================================================
echo           SECURITY SHADOW - LOCAL PROTOTYPE
echo ========================================================
echo This first-run helper prepares the environment and starts
 echo the backend, local dashboard, and monitoring agent.
echo No monitoring data is sent to a remote server.
echo.

set "PYRUN="
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYRUN=py -3"
)
if defined PYRUN goto python_found

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYRUN=python"
)
if defined PYRUN goto python_found

echo Python 3.10 or newer was not found. Checking for WinGet to install Python 3.12...
where winget >nul 2>&1
if errorlevel 1 goto manual_python
winget install --id Python.Python.3.12 -e --scope user --silent --accept-package-agreements --accept-source-agreements
where py >nul 2>&1
if not errorlevel 1 (
    py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYRUN=py -3.12"
)
if not defined PYRUN if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYRUN="%LocalAppData%\Programs\Python\Python312\python.exe""
if not defined PYRUN goto manual_python

echo Using Python command: %PYRUN%

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo Rebuilding an incompatible existing virtual environment...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the local virtual environment...
    %PYRUN% -m venv .venv
    if errorlevel 1 goto setup_failed
)

set "PY=%~dp0.venv\Scripts\python.exe"
"%PY%" -c "import flask, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages. Internet access is needed on first setup...
    "%PY%" -m pip install --upgrade pip
    if errorlevel 1 goto setup_failed
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto setup_failed
)

if not exist "private_backend\.upload_token" goto setup_credentials
if not exist "private_backend\.read_token" goto setup_credentials
goto credentials_ready

:setup_credentials
echo Creating this computer's private local credentials...
"%PY%" setup_local.py
if errorlevel 1 goto setup_failed

:credentials_ready
if not exist ".security_shadow_setup_complete" (
    echo Running the project test suite for the first time...
    "%PY%" -m unittest discover -s tests -v
    if errorlevel 1 goto tests_failed
    >".security_shadow_setup_complete" echo passed
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try {$r=Invoke-RestMethod -Uri 'http://127.0.0.1:5001/health' -TimeoutSec 2 -ErrorAction Stop; if($r.service -eq 'Security Shadow Private Backend' -and $r.status -eq 'running'){exit 0}} catch {}; exit 1" >nul 2>&1
if not errorlevel 1 goto already_running

echo Starting private backend...
start "Security Shadow Backend" cmd /k ""%PY%" -m private_backend.app"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 20;$i++){try{$r=Invoke-RestMethod -Uri 'http://127.0.0.1:5001/health' -TimeoutSec 1 -ErrorAction Stop;if($r.service -eq 'Security Shadow Private Backend' -and $r.status -eq 'running'){$ok=$true;break}}catch{};Start-Sleep -Seconds 1};if(-not $ok){exit 1}" >nul 2>&1
if errorlevel 1 goto backend_failed

echo Starting local dashboard...
start "Security Shadow Dashboard" cmd /k ""%PY%" app.py"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 20;$i++){try{$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5000/' -TimeoutSec 1 -ErrorAction Stop;if($r.StatusCode -eq 200){$ok=$true;break}}catch{};Start-Sleep -Seconds 1};if(-not $ok){exit 1}" >nul 2>&1
if errorlevel 1 goto dashboard_failed

echo Starting local monitoring agent...
set "SECURITY_SHADOW_UPLOAD=true"
start "Security Shadow Agent" cmd /k ""%PY%" agent\agent.py"
start "" "http://127.0.0.1:5000"

echo.
echo Security Shadow is starting in three console windows.
echo Dashboard: http://127.0.0.1:5000
echo Use STOP_SECURITY_SHADOW.bat to stop the local services.
echo Close this setup window when ready.
echo.
pause
endlocal
exit /b 0

:already_running
echo A Security Shadow backend is already running on this computer.
echo To avoid starting duplicate services, open http://127.0.0.1:5000 if the dashboard is running.
echo If you need a fresh start, close the three Security Shadow console windows and run this file again.
pause
endlocal
exit /b 0

:manual_python
echo.
echo Python 3.10 or newer could not be installed automatically.
echo Install Python 3.12 from https://www.python.org/downloads/windows/
echo Then run START_HERE.bat again. Choose the option to add Python to PATH if offered.
start "" "https://www.python.org/downloads/windows/"
pause
endlocal
exit /b 1

:backend_failed
echo The backend did not become ready. Check the Security Shadow Backend window for errors.
pause
endlocal
exit /b 1

:dashboard_failed
echo The dashboard did not become ready. Check the Security Shadow Dashboard window for errors.
echo The backend may still be running; use STOP_SECURITY_SHADOW.bat before trying again.
pause
endlocal
exit /b 1

:tests_failed
echo Project tests failed. Security Shadow will not start until the issue is reviewed.
pause
endlocal
exit /b 1

:setup_failed
echo Setup failed. Check the message above, your internet connection, and Python installation.
pause
endlocal
exit /b 1
