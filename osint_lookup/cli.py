"""CLI entry point: search the internet for an email or a name and report
which public sources it turns up in."""

import argparse
import re
import sys

from .checkers import (
    check_duckduckgo_name,
    check_github_email,
    check_github_name,
    check_gravatar,
    check_hibp,
)
from .dorks import suggest_queries
from .models import Finding, LookupResult

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def detect_query_type(query: str) -> str:
    return "email" if EMAIL_RE.match(query.strip()) else "name"


def run_lookup(query: str, query_type: str | None = None) -> LookupResult:
    query_type = query_type or detect_query_type(query)
    result = LookupResult(query=query, query_type=query_type)

    checkers: list[Finding | None]
    if query_type == "email":
        checkers = [
            check_gravatar(query),
            check_github_email(query),
            check_hibp(query),
        ]
    else:
        checkers = [
            check_github_name(query),
            check_duckduckgo_name(query),
        ]

    result.findings = [f for f in checkers if f is not None]
    return result


def format_result(result: LookupResult) -> str:
    lines = [f"Results for {result.query_type} '{result.query}':", ""]

    for finding in result.findings:
        if finding.error:
            lines.append(f"  [!] {finding.source}: error - {finding.error}")
        elif finding.found:
            lines.append(f"  [+] {finding.source}: FOUND")
            if finding.evidence:
                lines.append(f"      {finding.evidence}")
            if finding.url:
                lines.append(f"      {finding.url}")
        else:
            lines.append(f"  [-] {finding.source}: not found")

    lines.append("")
    lines.append("Suggested manual search-engine queries for deeper coverage:")
    for q in suggest_queries(result.query, result.query_type):
        lines.append(f"  {q}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Look up where an email address or name shows up in public "
            "sources (Gravatar, GitHub, DuckDuckGo, and optionally "
            "HaveIBeenPwned). Use only on your own information or with "
            "proper authorization."
        )
    )
    parser.add_argument("query", help="the email address or name to look up")
    parser.add_argument(
        "--type",
        choices=["email", "name"],
        help="force interpretation of the query (auto-detected by default)",
    )
    args = parser.parse_args(argv)

    result = run_lookup(args.query, args.type)
    print(format_result(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
