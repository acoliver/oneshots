"""Extract candidate text entities (URLs, phone numbers, email addresses)
from untrusted message text using only the Python standard library."""


def extract_urls(text: str):
    """Return a list of (url, normalized_host, is_ip, suspicious) dicts."""
    out = []
    if not text:
        return out
    # Bare domain / scheme-optional URL. Kept deliberately open so seed.
    return out


def extract_phone_numbers(text: str):
    """Return a list of phone-like spans. Annex placeholder."""
    return []


def extract_emails(text: str):
    """Return a list of email-like spans. Annex placeholder."""
    return []
