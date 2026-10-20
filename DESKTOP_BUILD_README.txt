SECURITY SHADOW — STANDALONE WINDOWS DESKTOP APP
Developed by Ayush S. Kshirsagar


Launch
  Double-click SecurityShadow.exe. The program opens a native Windows window
  and does not launch a separate browser.

What it does
  - Collects local process metadata and established internet connections.
  - Scores collected connections using explainable heuristic rules.
  - Shows process IDs, remote endpoints, risk scores, risk levels, and reasons.
  - Runs the backend and monitoring agent locally on loopback interfaces.
  - Generates random local credentials on first run.

Local data
  Credentials and diagnostic log are stored under:
    %LOCALAPPDATA%\SecurityShadow\
  The log file is security_shadow.log. Do not share this folder because it
  contains local credential files.

Limitations
  - This is a local monitoring prototype, not a certified security product.
  - Risk scores are investigation hints, not proof of malware; low scores do
    not guarantee safety.
  - Windows permissions may limit process and connection visibility.
  - It uses local loopback networking and is not designed for remote or
    multi-user deployment.
  - This one-file build targets 64-bit Windows and is built using Python and
    PyInstaller on Windows.
  - The executable embeds Company Name, Product Name, File Description, and
    copyright metadata identifying Ayush S. Kshirsagar. This metadata is not a
    digital signature and does not make Windows trust the publisher.
  - The executable remains unsigned. SmartScreen or antivirus software may
    show a warning. Do not disable protection or ignore a malware detection.

To close the app, click the window's X button. The local server and agent are
stopped as the application closes.
