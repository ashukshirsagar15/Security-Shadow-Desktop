@echo off
setlocal EnableExtensions

echo Security Shadow normally shuts down cleanly when you close its window using X.
echo Use this script only if the application is frozen and will not close normally.
echo It force-closes SecurityShadow.exe and may interrupt the current snapshot.
echo.
choice /C YN /M "Force-close SecurityShadow.exe now"
if errorlevel 2 exit /b 0

taskkill /IM SecurityShadow.exe /T /F
if errorlevel 1 echo No running SecurityShadow.exe process was found.
echo.
pause
endlocal
