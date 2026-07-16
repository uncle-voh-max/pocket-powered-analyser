from __future__ import annotations

from research_agent.security.url_safety import URLValidationError, assert_safe_url
from research_agent.utils.urls import canonicalise, domain_from_url, is_private_url


def test_canonicalise_basic() -> None:
    assert canonicalise("https://Example.com/Path") == "https://example.com/path"


def test_canonicalise_remove_tracking() -> None:
    url = "https://example.com/page?utm_source=twitter&q=hello"
    canon = canonicalise(url)
    assert "utm_source" not in canon
    assert "q=hello" in canon


def test_canonicalise_default_ports() -> None:
    assert canonicalise("https://example.com:443/path") == "https://example.com/path"
    assert canonicalise("http://example.com:80/path") == "http://example.com/path"


def test_domain_from_url() -> None:
    assert domain_from_url("https://www.example.com/path") == "www.example.com"
    assert domain_from_url("http://example.com") == "example.com"


def test_is_private_url() -> None:
    assert is_private_url("http://127.0.0.1:8000/test")
    assert is_private_url("http://localhost:3000")
    assert is_private_url("http://10.0.0.1/test")
    assert not is_private_url("https://example.com")


def test_assert_safe_url() -> None:
    assert_safe_url("https://example.com")  # should not raise

    import pytest
    with pytest.raises(URLValidationError):
        assert_safe_url("http://127.0.0.1:8000")
    with pytest.raises(URLValidationError):
        assert_safe_url("")
    with pytest.raises(URLValidationError):
        assert_safe_url("ftp://example.com")
