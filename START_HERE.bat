@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Security Shadow - Start

if exist "%~dp0release-output\SecurityShadow.exe" (
    start "Security Shadow" "%~dp0release-output\SecurityShadow.exe"
    exit /b 0
)

call "%~dp0BUILD_EXE.bat"
if errorlevel 1 exit /b 1
if exist "%~dp0release-output\SecurityShadow.exe" (
    start "Security Shadow" "%~dp0release-output\SecurityShadow.exe"
    exit /b 0
)
echo The EXE was not found after the build.
pause
exit /b 1
