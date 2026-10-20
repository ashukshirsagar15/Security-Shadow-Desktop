SECURITY SHADOW — STANDALONE WINDOWS DESKTOP BUILD KIT
Developed by Ayush S. Kshirsagar


This kit builds a single-file Windows desktop executable that opens in its
own native application window. The final app does NOT open a separate browser.

FIRST BUILD:
1. Extract the entire ZIP to a normal writable folder.
2. Make sure 64-bit Python 3.12 or 3.13 is installed. Python installer:
   https://www.python.org/downloads/windows/
3. Double-click START_HERE.bat.
4. On first run, it creates an isolated build environment, downloads the
   required Python packages, runs the project tests, and builds the EXE.
   Internet access is required for the first build.
5. The native app opens after a successful build.

AFTER THE FIRST BUILD:
- Double-click START_HERE.bat to open the desktop app.
- The standalone executable is at release-output\SecurityShadow.exe.
- Share Security-Shadow-Standalone-Windows-x64.zip with another compatible
  64-bit Windows computer. That final ZIP does not require Python to run.

DATA AND SECURITY:
- Per-computer credentials and logs are stored in
  %LOCALAPPDATA%\SecurityShadow\.
- Do not share that app-data folder; it contains local credentials.
- The app uses local loopback services only. It is not a remote or
  multi-user monitoring product.
- Scores are heuristic investigation signals, not proof of malware.
- The EXE is unsigned, so SmartScreen or antivirus software may display a
  warning. Do not bypass warnings unless you independently trust and verify
  the file's origin and contents.

The build embeds Windows file-version metadata identifying Ayush S. Kshirsagar
as the Company Name/developer. This is only file metadata; it is not a trusted
digital signature, so SmartScreen may still show Unknown Publisher.

This is a build kit, not a precompiled EXE. The EXE is generated on the
Windows computer when START_HERE.bat is first run.
