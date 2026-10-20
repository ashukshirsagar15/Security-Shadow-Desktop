# Release Safety Checklist

This checklist applies to the local prototype release. It does not certify production security.

- [x] Local dashboard and backend bind to `127.0.0.1` by default.
- [x] Agent uploads use a separate bearer credential from dashboard reads.
- [x] Credentials are created locally by `setup_local.py` and are not printed.
- [x] Source archive reviewed for `.env`, token files, private keys, and recognizable hard-coded API credential patterns; none were included in the supplied archive.
- [x] `.gitignore` excludes environment files, upload/read tokens, nested Git metadata, Python environments, backups, logs, and local telemetry exports.
- [x] Dashboard and agent reject remote backend URLs, preventing bearer tokens or monitoring snapshots from being sent to accidental non-loopback endpoints.
- [x] User-reported previous Windows build: 8/8 automated tests passed inside `.venv`.
- [x] Release-candidate loopback URL validation tests: 4 passed in the preparation environment.
- [ ] Rerun all 15 tests on Windows for this release candidate before pushing.
- [x] User confirmed the dashboard snapshot timestamp continued updating during live monitoring.
- [x] User reported expected MEDIUM (40/100) and HIGH (80/100) scores from synthetic test records.
- [ ] Before pushing: inspect the target repository's actual `git status`, tracked files, remotes, and commit history. This ZIP contains no `.git` directory, so it cannot establish the state of any existing remote repository or its history.
- [ ] Before pushing: ensure any previously exposed credentials are rotated and no secrets exist in previous commits.
- [ ] Before calling this production-ready: implement device enrollment and per-device credential rotation/revocation, persistent per-device storage, rate limits, and deployment security controls.

## Audit limitation

This checklist is based on the source ZIP that was uploaded for review and the test output provided from the user's Windows computer. It is not a scan of the user's original local `.git` history or an existing GitHub repository.


## Desktop branding

- [ ] Verify the application window displays “Developed by Ayush S. Kshirsagar”.
- [ ] After build, open SecurityShadow.exe > Properties > Details and verify Company Name, Product Name, File Description, File Version and Copyright.
- [ ] Run `Get-AuthenticodeSignature .\release-output\SecurityShadow.exe`. The current package is unsigned; version metadata does not change the signature status.
- [ ] Re-scan the final executable with Microsoft Defender and record the final hash.
