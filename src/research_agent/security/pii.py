from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
API_KEY_PATTERN = re.compile(
    r"(?:sk-[a-zA-Z0-9]{20,}|api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,})",
    re.IGNORECASE,
)
IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")


def redact_sensitive(text: str) -> str:
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    text = API_KEY_PATTERN.sub("[REDACTED_API_KEY]", text)
    text = IP_PATTERN.sub("[REDACTED_IP]", text)
    return text
