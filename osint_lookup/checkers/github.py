"""Check GitHub's public search API for a name or email.

Uses unauthenticated requests by default (60 req/hr, 10 req/min for search).
Set the GITHUB_TOKEN environment variable to raise those limits.
"""

import os

import requests

from ..models import Finding

TIMEOUT = 10
API_ROOT = "https://api.github.com"


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _search(endpoint: str, query: str) -> dict | None:
    try:
        response = requests.get(
            f"{API_ROOT}/search/{endpoint}",
            params={"q": query},
            headers=_headers(),
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return {"error": str(exc)}

    if response.status_code != 200:
        return {"error": f"unexpected status {response.status_code}"}

    return response.json()


def check_github_email(email: str) -> Finding:
    """Look for a GitHub account whose public profile email matches, and for
    commits authored with this email address."""

    result = _search("users", f"{email} in:email")
    if result and "error" in result:
        return Finding(source="GitHub (user email)", found=False, error=result["error"])

    items = (result or {}).get("items", [])
    if items:
        user = items[0]
        return Finding(
            source="GitHub (user email)",
            found=True,
            url=user.get("html_url", ""),
            evidence=f"Public profile email matches account '{user.get('login')}'",
        )

    commit_result = _search("commits", f"author-email:{email}")
    if commit_result and "error" in commit_result:
        return Finding(
            source="GitHub (commit email)", found=False, error=commit_result["error"]
        )

    commit_items = (commit_result or {}).get("items", [])
    if commit_items:
        commit = commit_items[0]
        return Finding(
            source="GitHub (commit email)",
            found=True,
            url=commit.get("html_url", ""),
            evidence=f"Commit authored with this email in {commit.get('repository', {}).get('full_name', 'a repository')}",
        )

    return Finding(source="GitHub (email)", found=False)


def check_github_name(name: str) -> Finding:
    """Look for GitHub accounts whose display name matches."""

    result = _search("users", f'"{name}" in:name')
    if result and "error" in result:
        return Finding(source="GitHub (name)", found=False, error=result["error"])

    items = (result or {}).get("items", [])
    if items:
        user = items[0]
        total = (result or {}).get("total_count", len(items))
        return Finding(
            source="GitHub (name)",
            found=True,
            url=user.get("html_url", ""),
            evidence=f"{total} account(s) with a matching display name, e.g. '{user.get('login')}'",
        )

    return Finding(source="GitHub (name)", found=False)
