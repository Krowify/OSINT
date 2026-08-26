"""Generate search-engine query suggestions ("dorks") for manual follow-up.

We don't scrape search-engine result pages here -- that violates the terms
of service of Google, Bing, etc., and is legally risky. Instead we hand back
ready-to-paste queries so the user can run them themselves in a browser.
"""


def suggest_queries(query: str, query_type: str) -> list[str]:
    quoted = f'"{query}"'
    if query_type == "email":
        return [
            quoted,
            f"{quoted} site:pastebin.com",
            f"{quoted} site:linkedin.com",
            f"{quoted} filetype:pdf",
        ]

    return [
        quoted,
        f"{quoted} site:linkedin.com",
        f"{quoted} site:twitter.com OR site:x.com",
        f"{quoted} resume OR cv",
    ]
