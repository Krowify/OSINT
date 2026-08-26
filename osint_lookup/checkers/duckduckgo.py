"""Check DuckDuckGo's Instant Answer API for mentions of a name.

This uses DuckDuckGo's public, keyless Instant Answer JSON endpoint rather
than scraping search-result pages, which would violate DuckDuckGo's terms
of service. Coverage is limited to topics DuckDuckGo has an instant answer
for (notable people, organizations, etc.) -- it will not surface arbitrary
web pages.
"""

import requests

from ..models import Finding

TIMEOUT = 10
API_URL = "https://api.duckduckgo.com/"


def check_duckduckgo_name(name: str) -> Finding:
    try:
        response = requests.get(
            API_URL,
            params={"q": name, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return Finding(source="DuckDuckGo", found=False, error=str(exc))

    if response.status_code != 200:
        return Finding(
            source="DuckDuckGo",
            found=False,
            error=f"unexpected status {response.status_code}",
        )

    data = response.json()
    abstract = data.get("AbstractText", "")
    source_url = data.get("AbstractURL", "")

    if abstract and source_url:
        return Finding(
            source="DuckDuckGo",
            found=True,
            url=source_url,
            evidence=abstract[:200],
        )

    return Finding(source="DuckDuckGo", found=False)
