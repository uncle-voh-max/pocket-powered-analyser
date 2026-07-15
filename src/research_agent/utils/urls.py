from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

import httpx


def canonicalise(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/").lower() or "/"

    # Remove default ports
    if (scheme == "http" and netloc.endswith(":80")) or (
        scheme == "https" and netloc.endswith(":443")
    ):
        netloc = netloc.rsplit(":", 1)[0]

    # Remove tracking query params
    query = _strip_tracking_params(parsed.query)

    return urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment or ""))


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "gclsrc", "dclid", "gbraid", "wbraid",
    "msclkid", "ref", "source", "si",
}


def _strip_tracking_params(query: str) -> str:
    if not query:
        return ""
    params = [p for p in query.split("&") if p.split("=")[0] not in TRACKING_PARAMS]
    return "&".join(params)


def domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.rstrip("/") or "/"


PRIVATE_IPS = re.compile(
    r"^(10\.|127\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|"
    r"169\.254\.|::1|fc00:|fe80:)"
)


def is_private_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return bool(PRIVATE_IPS.match(host)) or host in {"localhost", "0.0.0.0"}


def validate_url_scheme(url: str) -> bool:
    return urlparse(url).scheme in {"http", "https"}


async def resolve_redirects(url: str, client: httpx.AsyncClient | None = None) -> str:
    if client is None:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as c:
            try:
                r = await c.head(url)
                return str(r.url)
            except httpx.HTTPError:
                return url
    try:
        r = await client.head(url)
        return str(r.url)
    except httpx.HTTPError:
        return url
