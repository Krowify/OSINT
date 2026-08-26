from unittest.mock import Mock, patch

from osint_lookup.checkers.duckduckgo import check_duckduckgo_name
from osint_lookup.checkers.github import check_github_email, check_github_name
from osint_lookup.checkers.gravatar import check_gravatar
from osint_lookup.checkers.hibp import check_hibp


def _mock_response(status_code=200, json_data=None):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    return response


@patch("osint_lookup.checkers.gravatar.requests.get")
def test_gravatar_found(mock_get):
    mock_get.return_value = _mock_response(
        200, {"entry": [{"displayName": "Jane", "profileUrl": "https://gravatar.com/jane"}]}
    )
    finding = check_gravatar("jane@example.com")
    assert finding.found is True
    assert finding.url == "https://gravatar.com/jane"


@patch("osint_lookup.checkers.gravatar.requests.get")
def test_gravatar_not_found(mock_get):
    mock_get.return_value = _mock_response(404)
    finding = check_gravatar("nobody@example.com")
    assert finding.found is False


@patch("osint_lookup.checkers.github.requests.get")
def test_github_email_found_via_user(mock_get):
    mock_get.return_value = _mock_response(
        200, {"items": [{"login": "janedoe", "html_url": "https://github.com/janedoe"}]}
    )
    finding = check_github_email("jane@example.com")
    assert finding.found is True
    assert finding.url == "https://github.com/janedoe"


@patch("osint_lookup.checkers.github.requests.get")
def test_github_name_not_found(mock_get):
    mock_get.return_value = _mock_response(200, {"items": [], "total_count": 0})
    finding = check_github_name("Zzznobody Qqq")
    assert finding.found is False


@patch("osint_lookup.checkers.duckduckgo.requests.get")
def test_duckduckgo_found(mock_get):
    mock_get.return_value = _mock_response(
        200, {"AbstractText": "Some notable person.", "AbstractURL": "https://en.wikipedia.org/x"}
    )
    finding = check_duckduckgo_name("Notable Person")
    assert finding.found is True
    assert finding.url == "https://en.wikipedia.org/x"


def test_hibp_skipped_without_api_key(monkeypatch):
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    assert check_hibp("someone@example.com") is None


@patch("osint_lookup.checkers.hibp.requests.get")
def test_hibp_found_with_api_key(mock_get, monkeypatch):
    monkeypatch.setenv("HIBP_API_KEY", "fake-key")
    mock_get.return_value = _mock_response(200, [{"Name": "ExampleBreach"}])
    finding = check_hibp("someone@example.com")
    assert finding.found is True
    assert "ExampleBreach" in finding.evidence
