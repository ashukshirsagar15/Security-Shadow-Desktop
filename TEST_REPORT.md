# Security Shadow Desktop Build — Test Report

## Automated tests

The package includes 15 unit tests covering:

- backend snapshot validation and token-gated upload/read routes;
- dashboard API mapping for the original local prototype;
- local backend URL validation;
- risk levels, explanations, configured review IPs, invalid port types, and snapshot immutability.

At package preparation, Python syntax compilation passed for the desktop entry point and project modules. The 6 risk-engine tests and 4 local-configuration tests passed in the preparation environment. The full Flask-dependent test suite could not be repeated there because Flask was not installed and network access to the package index was unavailable. Therefore, this environment has **not** independently certified a complete Windows EXE build.

`BUILD_EXE.bat` installs dependencies, runs the complete test suite, and only builds the EXE if those tests pass. The receiving Windows computer should show all tests passing before the build continues.

## Manual checks required after building on Windows

1. Confirm `release-output\SecurityShadow.exe` exists.
2. Launch the EXE and confirm it opens a native desktop window without a browser.
3. Confirm the local-monitor status changes to active.
4. Confirm established connections display process, PID, remote endpoint, risk score, level, and reasons.
5. Select a connection and confirm investigation details appear.
6. Close the window and verify the local server/monitoring loop stops.
7. Reopen the EXE and verify new per-computer credentials are created or existing valid ones are reused.
8. Verify the SHA-256 hash in `release-output\SHA256.txt` and keep the executable and documentation together when sharing.

## Limitations

- This is a single-computer local monitoring prototype, not a production endpoint detection product.
- The backend retains only the latest snapshot in memory; restarting it clears the snapshot.
- Heuristic scores are investigation signals, not malware verdicts.
- Windows permissions can limit process and connection visibility.
- The executable is unsigned and has not been independently tested on every Windows version or hardware configuration.


## Branding checks

The desktop UI displays “Developed by Ayush S. Kshirsagar”. The Windows
version resource embeds CompanyName, FileDescription, FileVersion, ProductName,
ProductVersion and copyright metadata. These fields can appear in File Explorer
Properties > Details; they are not a digital signature and do not change
Authenticode status. The build remains unsigned unless it is separately signed
with a trusted code-signing certificate.
