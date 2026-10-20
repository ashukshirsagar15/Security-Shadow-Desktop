@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Security Shadow - Verify Release Package
set "EXE=release-output\SecurityShadow.exe"
set "HASHFILE=release-output\SHA256.txt"
if not exist "%EXE%" (
  echo ERROR: %EXE% was not found.
  echo Run BUILD_EXE.bat first.
  pause
  exit /b 1
)
echo === Executable SHA-256 ===
powershell -NoProfile -Command "Get-FileHash '%EXE%' -Algorithm SHA256 | Format-List Algorithm,Hash,Path"
echo === Authenticode signature ===
powershell -NoProfile -Command "Get-AuthenticodeSignature '%EXE%' | Format-List Status,StatusMessage,SignerCertificate"
echo.
if exist "%HASHFILE%" (
  echo A build-time checksum file exists at %HASHFILE%.
  echo Compare its hash with the hash above. For a file shared by someone else,
  echo obtain the expected hash through a separate trusted channel.
) else (
  echo WARNING: The build-time SHA256 file was not found.
)
echo.
echo Note: NotSigned is expected for this current unsigned prototype; it is not proof
 echo of malware, and it also does not certify that the file is safe. Verify its origin.
pause
endlocal
