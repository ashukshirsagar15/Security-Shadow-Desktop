# Security Shadow — Final Packaging & Security Checklist

This checklist is for the current original local prototype packaged as a one-file Windows desktop EXE. It is not a certification or guarantee that the program detects malware.

## Packaging review (static checks)

- [x] The desktop UI shows “Developed by Ayush S. Kshirsagar”.
- [x] The EXE build embeds CompanyName, ProductName, FileDescription, FileVersion, ProductVersion, and copyright fields from `version_info.txt`. These are metadata only and do not authenticate the publisher.

- [x] Desktop UI uses Tkinter; it does not need to open a separate browser.
- [x] Build script uses PyInstaller `--onefile --windowed` and creates `release-output\SecurityShadow.exe`.
- [x] Credentials are generated per computer under `%LOCALAPPDATA%\SecurityShadow\private_backend\`.
- [x] The latest assessed snapshot is held in backend memory; it is not designed as a cloud service.
- [x] Backend binds to `127.0.0.1:5001`, not `0.0.0.0`.
- [x] Agent upload and dashboard read endpoints require separate bearer tokens and compare tokens with `hmac.compare_digest`.
- [x] `.gitignore` excludes `.upload_token`, `.read_token`, local logs and local monitoring exports.
- [x] The desktop build ZIP reviewed here contains no `.upload_token`, `.read_token`, `.env`, virtual environment, or pre-existing EXE.
- [x] Build-time tests are run before PyInstaller creates the executable.

## Checks performed on the developer/recipient Windows computer

1. Run `VERIFY_RELEASE.bat` in the extracted build-kit directory. Save the SHA-256 output.
2. Compare the EXE hash to the `SHA256.txt` from the same build. For files received from another person, confirm the expected hash with them through a separate trusted channel; a checksum stored beside an EXE alone does not establish trust.
3. In Windows Security, scan `SecurityShadow.exe` using Microsoft Defender. Do not disable Defender or create exclusions to get the app running.
4. Check that a SmartScreen prompt is an unfamiliar-app/reputation prompt, not a separate antivirus threat detection. This build is unsigned, so SmartScreen may still warn.
5. Launch the application and verify the dashboard timestamp and counts update.
6. In PowerShell run `netstat -ano | findstr :5001`. While the app is open, the service should listen on loopback (`127.0.0.1:5001`), not all network interfaces (`0.0.0.0:5001`).
7. Close the app using its window X button. Wait a few seconds and run the `netstat` command again; the app's listener should disappear unless another copy is running.
8. Reopen the app. Confirm monitoring resumes and a new timestamp appears.
9. Copy the final ZIP to a different supported Windows computer, extract it fully, and test again. Keep that computer's logs/credentials local.

## Security notes and limitations

- The executable is unsigned; `Get-AuthenticodeSignature` is expected to report `NotSigned` for this build. The new CompanyName metadata does not remove “Unknown Publisher”. A verified publisher identity requires a trusted code-signing certificate and a proper signing/release process.
- SmartScreen reputation prompts are not the same as an antivirus malware detection. Do not bypass a threat detection.
- Credentials are stored locally as files under the current user's LocalAppData directory. Do not share `%LOCALAPPDATA%\SecurityShadow\` or its token files.
- Monitoring data includes process names, PIDs, IP addresses and ports. Treat it as private machine data.
- The prototype uses loopback HTTP with bearer tokens and is intended for local, single-user use. Do not expose its backend/dashboard ports to a network.
- Risk results are heuristic investigation signals. They are not malware verdicts, and LOW does not guarantee safety.
- A successful launch on one additional computer is a useful portability test, but it is not a complete compatibility, security, or malware-detection evaluation.

## Current validation status

Static source/packaging review can be performed before release. The full regression suite and the actual EXE's behavior must be verified on Windows; a Linux-side source review cannot certify a Windows binary. Record the date, Windows version, EXE hash, test result, and any warning shown during the final cross-computer test.
