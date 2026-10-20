@echo off
setlocal
cd /d "%~dp0"
if not exist ".build-venv\Scripts\python.exe" (
    echo Run START_HERE.bat or BUILD_EXE.bat first to prepare the build environment.
    pause
    exit /b 1
)
".build-venv\Scripts\python.exe" -m unittest discover -s tests -v
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo One or more tests failed.
if "%RESULT%"=="0" echo All tests passed.
pause
exit /b %RESULT%
