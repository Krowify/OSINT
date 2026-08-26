"""Check whether an email has a public Gravatar profile."""

import hashlib

import requests

from ..models import Finding

TIMEOUT = 10


def check_gravatar(email: str) -> Finding:
    email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"

    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return Finding(source="Gravatar", found=False, error=str(exc))

    if response.status_code == 200:
        data = response.json()
        entry = data.get("entry", [{}])[0]
        display_name = entry.get("displayName", "")
        profile_url = entry.get("profileUrl", f"https://www.gravatar.com/{email_hash}")
        evidence = f"Public Gravatar profile{f' for {display_name}' if display_name else ''}"
        return Finding(source="Gravatar", found=True, url=profile_url, evidence=evidence)

    if response.status_code == 404:
        return Finding(source="Gravatar", found=False, url=url)

    return Finding(
        source="Gravatar",
        found=False,
        error=f"unexpected status {response.status_code}",
    )
