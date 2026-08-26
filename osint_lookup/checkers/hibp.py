"""Check Have I Been Pwned for breaches containing an email.

Requires an HIBP API key (https://haveibeenpwned.com/API/Key) set in the
HIBP_API_KEY environment variable. Intended for checking your own email
addresses in line with HIBP's terms of use. Skipped entirely if no key is
configured.
"""

import os

import requests

from ..models import Finding

TIMEOUT = 10
API_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{account}"


def check_hibp(email: str) -> Finding | None:
    api_key = os.environ.get("HIBP_API_KEY")
    if not api_key:
        return None  # skip silently: this checker requires an API key

    try:
        response = requests.get(
            API_URL.format(account=email),
            headers={"hibp-api-key": api_key, "user-agent": "osint-lookup"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return Finding(source="HaveIBeenPwned", found=False, error=str(exc))

    if response.status_code == 200:
        breaches = [b.get("Name", "?") for b in response.json()]
        return Finding(
            source="HaveIBeenPwned",
            found=True,
            url="https://haveibeenpwned.com/",
            evidence=f"Appears in breach(es): {', '.join(breaches)}",
        )

    if response.status_code == 404:
        return Finding(source="HaveIBeenPwned", found=False)

    return Finding(
        source="HaveIBeenPwned",
        found=False,
        error=f"unexpected status {response.status_code}",
    )
