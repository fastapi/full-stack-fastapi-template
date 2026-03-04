"""
Email domain validation for subscription upgrade gating.
Tier 2 and Tier 3 require a working (non-personal) email address.
"""

PERSONAL_EMAIL_DOMAINS = frozenset({
    "gmail.com", "googlemail.com",
    "yahoo.com", "yahoo.co.uk", "yahoo.fr", "yahoo.de", "yahoo.es",
    "ymail.com",
    "hotmail.com", "hotmail.co.uk", "hotmail.fr",
    "outlook.com", "outlook.co.uk",
    "live.com", "live.co.uk",
    "msn.com",
    "icloud.com", "me.com", "mac.com",
    "aol.com",
    "protonmail.com", "proton.me",
    "tutanota.com",
    "zoho.com",
    "mail.com",
    "gmx.com", "gmx.net", "gmx.de",
})


def is_personal_email(email: str) -> bool:
    """Return True if the email domain is a known personal/consumer provider."""
    try:
        domain = email.strip().lower().split("@")[1]
        return domain in PERSONAL_EMAIL_DOMAINS
    except (IndexError, AttributeError):
        return False


def is_working_email(email: str) -> bool:
    """Return True if the email is suitable for Tier 2/3 (not a personal provider)."""
    return not is_personal_email(email)
