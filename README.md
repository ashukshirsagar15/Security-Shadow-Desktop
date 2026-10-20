> Developed by Ayush S. Kshirsagar

# Security Shadow — standalone Windows desktop build kit

This folder contains the original Security Shadow local prototype plus a Tkinter-based desktop window and a Windows build script. The **final executable** opens in its own native window; it does not open a separate browser.

## Build the EXE on Windows

1. Extract the entire folder to a writable location.
2. Install 64-bit Python 3.12 or 3.13 if required: https://www.python.org/downloads/windows/
3. Double-click `START_HERE.bat`.
4. On first run, `BUILD_EXE.bat` creates an isolated build environment, installs requirements and PyInstaller, runs the test suite, and builds a one-file windowed executable. Internet access is needed to download build packages.
5. The executable is `release-output\SecurityShadow.exe`. A shareable package is written to `Security-Shadow-Standalone-Windows-x64.zip`.
6. After the first build, `START_HERE.bat` launches the existing EXE directly.

The source kit itself is **not** a precompiled executable. The Windows build step is required to produce the EXE.

## Application architecture

- `desktop_app.py`: native Tkinter user interface and lifecycle.
- `agent/agent.py`: process and established-connection collection.
- `private_backend/app.py`: token-protected local snapshot ingestion and retrieval.
- `risk_engine.py`: explainable heuristic scores and findings.
- `setup_local.py`: random per-computer credentials.

## Local data and safety

Credentials and logs are stored under `%LOCALAPPDATA%\SecurityShadow\`. Do not share that folder. The app binds its local services to `127.0.0.1` and is intended for a single computer, not network hosting. Heuristic scores are indicators for investigation, not proof of malware. LOW does not guarantee safety.

The resulting executable is unsigned and may receive a Windows SmartScreen or antivirus warning. Verify the source and SHA-256 hash before sharing; do not bypass warnings unless you independently trust the executable.

See `QUICK_START_WINDOWS.md`, `DESKTOP_BUILD_README.txt`, and `TEST_REPORT.md` for build and use details.

## Tests

The build script runs `python -m unittest discover -s tests -v` before it compiles the EXE. If tests fail, the script stops rather than producing the release package.

## License

MIT License. See `LICENSE`.


## Final packaging and security checks

Read `FINAL_PACKAGING_SECURITY_CHECKLIST.md` before sharing the executable. Run `VERIFY_RELEASE.bat` on the build computer to inspect the EXE hash and Authenticode status. After `BUILD_EXE.bat` succeeds, a SHA-256 sidecar is also written beside `Security-Shadow-Standalone-Windows-x64.zip`; share the expected hash separately through a trusted channel. The current EXE is unsigned, so SmartScreen can still show a reputation prompt. Do not disable Microsoft Defender or bypass a malware detection.


## Branding and executable identity

The desktop window displays “Developed by Ayush S. Kshirsagar”. The Windows
build also embeds CompanyName, FileDescription, ProductName, version, and
copyright metadata. These fields are editable file metadata, not proof of
publisher identity. The current build is unsigned; a trusted code-signing
certificate is required for a verified Windows publisher signature.
