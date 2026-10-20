"""Create local-only random credentials for a fresh Security Shadow install."""

import os
import secrets
from pathlib import Path

BASE_DIR = Path(os.environ.get("SECURITY_SHADOW_DATA_DIR", Path(__file__).resolve().parent))
BACKEND_DIR = BASE_DIR / "private_backend"


def ensure_token(path: Path) -> str:
    if path.exists():
        token = path.read_text(encoding="utf-8").strip()
        if len(token) < 32:
            raise RuntimeError(
                f"{path.name} exists but is too short. Do not reuse it; back it up and regenerate deliberately."
            )
        return "existing"

    token = secrets.token_urlsafe(48)
    path.write_text(token + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass  # Windows permissions are governed by the folder's ACL.
    return "created"


def main() -> None:
    BACKEND_DIR.mkdir(parents=True, exist_ok=True)
    upload_state = ensure_token(BACKEND_DIR / ".upload_token")
    read_state = ensure_token(BACKEND_DIR / ".read_token")
    print("Security Shadow local credentials are ready.")
    print(f"Upload credential: {upload_state}")
    print(f"Dashboard read credential: {read_state}")
    print("Credential values were not displayed.")
    print("Keep private_backend/.upload_token and .read_token out of Git and shared ZIP files.")


if __name__ == "__main__":
    main()
