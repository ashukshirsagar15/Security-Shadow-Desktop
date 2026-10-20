"""Configuration helpers for the local-only Security Shadow build."""

import os
from urllib.parse import urlsplit

_ALLOWED_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def resolve_local_backend_url(env_name: str, default: str, environ=None) -> str:
    """Return an HTTP loopback URL only; reject remote endpoints fail-closed."""
    source = os.environ if environ is None else environ
    value = source.get(env_name, default)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{env_name} must be a local loopback URL.")

    try:
        parsed = urlsplit(value.strip())
        port = parsed.port  # Forces invalid-port validation.
    except ValueError as exc:
        raise RuntimeError(f"{env_name} must be a valid local loopback URL.") from exc

    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme.lower() != "http"
        or host not in _ALLOWED_LOOPBACK_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise RuntimeError(
            f"{env_name} must target http://127.0.0.1, http://localhost, "
            "or http://[::1] only. Security Shadow's published build is local-only."
        )

    return value.strip().rstrip("/")
