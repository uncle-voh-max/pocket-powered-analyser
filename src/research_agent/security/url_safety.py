from __future__ import annotations

from urllib.parse import urlparse

from research_agent.utils.urls import is_private_url, validate_url_scheme


class URLValidationError(Exception):
    """Raised when a URL fails security validation."""


def assert_safe_url(url: str) -> None:
    if not url:
        raise URLValidationError("URL is empty")

    if not validate_url_scheme(url):
        raise URLValidationError(f"Invalid URL scheme: {url}")

    if is_private_url(url):
        raise URLValidationError(f"URL points to private IP range: {url}")

    parsed = urlparse(url)
    if not parsed.hostname:
        raise URLValidationError(f"URL has no hostname: {url}")

    if len(url) > 8192:
        raise URLValidationError("URL exceeds maximum length")


MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB
REQUEST_TIMEOUT = 30.0
