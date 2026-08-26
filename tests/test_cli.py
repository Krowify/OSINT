from osint_lookup.cli import detect_query_type, format_result
from osint_lookup.models import Finding, LookupResult


def test_detect_query_type_email():
    assert detect_query_type("someone@example.com") == "email"


def test_detect_query_type_name():
    assert detect_query_type("Jane Doe") == "name"


def test_format_result_includes_hits_and_misses():
    result = LookupResult(
        query="someone@example.com",
        query_type="email",
        findings=[
            Finding(source="Gravatar", found=True, url="https://gravatar.com/x", evidence="Public profile"),
            Finding(source="GitHub (user email)", found=False),
            Finding(source="HaveIBeenPwned", found=False, error="no api key"),
        ],
    )

    output = format_result(result)

    assert "FOUND" in output
    assert "https://gravatar.com/x" in output
    assert "not found" in output
    assert "error - no api key" in output
    assert "Suggested manual search-engine queries" in output
