# Security Policy

## Scope

Security Shadow is a local-only prototype. Its current bearer-token design is intended for a single local development machine, not a public multi-user service.

## Reporting a vulnerability

Please do not publish credentials, monitoring snapshots, or details that expose a live machine in a public issue. Use the repository's private vulnerability-reporting option if it is enabled; otherwise contact the maintainer privately before sharing technical details.

## Safe-use notes

- Do not expose the dashboard or private backend to the internet.
- Do not commit `.env`, `private_backend/.upload_token`, `private_backend/.read_token`, or telemetry exports.
- Treat process names, PIDs, IP addresses, and ports as potentially sensitive monitoring data.
- Risk scores are heuristic indicators, not malware verdicts.
