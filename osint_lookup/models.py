"""Shared data types for OSINT checkers."""

from dataclasses import dataclass, field


@dataclass
class Finding:
    """One piece of evidence that a query (email or name) was found somewhere."""

    source: str
    found: bool
    url: str = ""
    evidence: str = ""
    error: str = ""


@dataclass
class LookupResult:
    """All findings collected for a single query."""

    query: str
    query_type: str  # "email" or "name"
    findings: list[Finding] = field(default_factory=list)

    @property
    def hits(self) -> list[Finding]:
        return [f for f in self.findings if f.found]
