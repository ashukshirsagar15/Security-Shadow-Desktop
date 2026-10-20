@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Security Shadow - Build Standalone Windows EXE

echo ============================================================
echo SECURITY SHADOW - STANDALONE WINDOWS BUILD
echo ============================================================
echo This creates a native Windows desktop EXE. It does not use a
 echo separate browser window. Initial build requires internet access.
echo.

set "PYTHON_LAUNCHER="
py -3.12 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_LAUNCHER=py -3.12"
if not defined PYTHON_LAUNCHER (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_LAUNCHER=py -3.13"
)
if not defined PYTHON_LAUNCHER (
    echo ERROR: Python 3.12 or 3.13 was not found through the Windows py launcher.
    echo Install 64-bit Python 3.12 or 3.13 from:
    echo https://www.python.org/downloads/windows/
    echo During installation, enable the Python launcher option.
    pause
    exit /b 1
)

echo Using %PYTHON_LAUNCHER%
if not exist ".build-venv\Scripts\python.exe" (
    echo Creating isolated build environment...
    %PYTHON_LAUNCHER% -m venv .build-venv
    if errorlevel 1 goto :fail
)
set "PY=.build-venv\Scripts\python.exe"

echo.
echo Installing build dependencies. This step needs internet access...
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto :fail
"%PY%" -m pip install -r requirements.txt "pyinstaller>=6.11,<7"
if errorlevel 1 goto :fail

echo.
echo Running project tests...
"%PY%" -m unittest discover -s tests -v
if errorlevel 1 goto :fail

echo.
echo Building one-file desktop executable...
"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name SecurityShadow --collect-all flask --collect-all werkzeug --collect-all psutil --collect-all requests --hidden-import agent.agent --hidden-import private_backend.app --hidden-import setup_local --hidden-import risk_engine --hidden-import local_config --version-file version_info.txt desktop_app.py
if errorlevel 1 goto :fail
if not exist "dist\SecurityShadow.exe" (
    echo ERROR: PyInstaller did not create dist\SecurityShadow.exe
    goto :fail
)

if exist "release-output" rmdir /s /q "release-output"
mkdir "release-output"
copy /y "dist\SecurityShadow.exe" "release-output\SecurityShadow.exe" >nul
copy /y "DESKTOP_BUILD_README.txt" "release-output\README.txt" >nul
copy /y "LICENSE" "release-output\LICENSE.txt" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-FileHash 'release-output\SecurityShadow.exe' -Algorithm SHA256 | Format-List | Out-File 'release-output\SHA256.txt' -Encoding ascii"
if errorlevel 1 goto :fail
if exist "Security-Shadow-Standalone-Windows-x64.zip" del /q "Security-Shadow-Standalone-Windows-x64.zip"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'release-output\*' -DestinationPath 'Security-Shadow-Standalone-Windows-x64.zip' -Force"
if errorlevel 1 goto :fail
powershell -NoProfile -Command "(Get-FileHash 'Security-Shadow-Standalone-Windows-x64.zip' -Algorithm SHA256).Hash + '  Security-Shadow-Standalone-Windows-x64.zip' | Set-Content 'Security-Shadow-Standalone-Windows-x64.zip.sha256' -Encoding ascii"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo BUILD SUCCESSFUL
echo Executable: %CD%\release-output\SecurityShadow.exe
echo Shareable ZIP: %CD%\Security-Shadow-Standalone-Windows-x64.zip
echo ============================================================
echo.
echo Open the EXE directly. It launches a native desktop window and
 echo keeps its credentials and logs under %%LOCALAPPDATA%%\SecurityShadow.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED. Read the error above, correct it, and rerun BUILD_EXE.bat.
pause
exit /b 1
