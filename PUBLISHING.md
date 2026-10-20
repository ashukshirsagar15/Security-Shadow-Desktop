# Publishing Security Shadow safely

This folder is a source-code release candidate, not proof that an existing GitHub repository or its history is clean. The submitted ZIP has no `.git` directory, so local repository history and configured remotes must be checked on the machine where you plan to publish.

## 1. Run the release-candidate tests first

In PowerShell, from this folder:

```powershell
.\.build-venv\Scripts\python.exe -m unittest discover -s tests -v
```

Do not publish unless all 15 tests pass. The current release-candidate test run passed all 15 tests. Rerun the tests before publishing; if any fail, stop and investigate. If any fail, stop and investigate instead of pushing.

## 2. Create a new empty GitHub repository

Create a repository named `Security-Shadow`. Leave it empty: do not pre-create a README, licence, or `.gitignore`, because those are already in this release folder. Do not publish secrets, local snapshots, or your old development folder.

## 3. Initialize Git and inspect before committing

Run these commands in PowerShell from this release folder:

```powershell
git init -b main
git status --short
git add --all
git status --short
git diff --cached --name-only
git diff --cached --check
```

Review the staged file list. It should contain only source code, tests, documentation, licence, and CI configuration. It must not contain `.env`, `.upload_token`, `.read_token`, `.venv`, `__pycache__`, backups, logs, or real monitoring exports.

The `.gitignore` in this folder excludes these common local files, but `.gitignore` is not a substitute for inspecting the staged file list.

## 4. Commit and push only after the review

Replace the URL below with the HTTPS URL for the new repository you created:

```powershell
git commit -m "Prepare Security Shadow local prototype v1.0"
git remote add origin https://github.com/YOUR-ACCOUNT/Security-Shadow.git
git push -u origin main
```

Do not paste tokens, passwords, or `.env` contents into a chat, command, issue, README, or commit. If a credential was ever committed, revoke/rotate it even after deleting it from the latest version. This release source ZIP cannot audit old commits in another repository.

## Release label

Use **Security Shadow v1.0 — Local Prototype**. Do not describe this release as a production-ready security product: this version stores only the most recent snapshot in memory and has not been built for multi-device/public hosting.
