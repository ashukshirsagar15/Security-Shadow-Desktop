# Security Shadow — standalone desktop build kit

## Goal

Build a single-file Windows desktop executable. The application uses a native
Tkinter window and does not open a separate browser.

## First build

1. Extract the entire ZIP to a normal writable folder.
2. Install 64-bit Python 3.12 or 3.13 if it is not already installed:
   https://www.python.org/downloads/windows/
3. Double-click `START_HERE.bat`.
4. On first run, the script creates `.build-venv`, installs dependencies and
   PyInstaller, executes `python -m unittest discover -s tests -v`, builds
   `SecurityShadow.exe`, and opens it. Internet access is needed to download
   build dependencies.
5. The standalone executable is saved at `release-output\SecurityShadow.exe`.
   A shareable ZIP is created at `Security-Shadow-Standalone-Windows-x64.zip`.

## Subsequent launches

Double-click `START_HERE.bat`. If the executable has already been built, it
launches directly without rebuilding.

## Sharing the final app

Share `Security-Shadow-Standalone-Windows-x64.zip` after the build succeeds.
The receiving computer needs compatible 64-bit Windows, but does not need
Python installed to run the EXE. Each computer creates its own credentials.

## Local data

Credentials and logs live in `%LOCALAPPDATA%\SecurityShadow\`. Do not share
that folder. Local APIs bind only to `127.0.0.1`; do not change this to expose
the services on a network. The backend holds only the latest snapshot in
memory. Heuristic scores are investigative signals, not malware verdicts.

## Troubleshooting

- Python not found: install 64-bit Python 3.12 or 3.13 from python.org and
  rerun the script.
- Dependency installation fails: confirm internet access, then rerun it.
- Tests fail: stop and review the test error before sharing the executable.
- App does not start: inspect `%LOCALAPPDATA%\SecurityShadow\security_shadow.log`.
- SmartScreen may warn because the EXE is unsigned. Do not bypass a warning
  unless you independently verify and trust the source and hash.


## Before sharing

1. Run `VERIFY_RELEASE.bat` to print the executable SHA-256 and signature status.
2. Share `Security-Shadow-Standalone-Windows-x64.zip` and its `.sha256` sidecar; send the expected hash through a separate trusted channel.
3. Scan the EXE using Microsoft Defender and test it on a separate Windows machine.
4. Use `FINAL_PACKAGING_SECURITY_CHECKLIST.md` to verify loopback-only binding and clean shutdown.


## Rebuild after branding changes

To generate an EXE containing the current developer label and Windows file
metadata, extract this updated build kit into a fresh writable folder and run
`BUILD_EXE.bat`. Do not merely launch an older `release-output\SecurityShadow.exe`;
an existing executable does not change when source files change.
