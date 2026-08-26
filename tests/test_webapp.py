from unittest.mock import patch

import pytest

from osint_lookup import storage, webapp
from osint_lookup.models import Finding, LookupResult


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "history.db")


@pytest.fixture
def client():
    webapp.app.config.update(TESTING=True)
    return webapp.app.test_client()


def _fake_result(query="jane@example.com"):
    return LookupResult(
        query=query,
        query_type="email",
        findings=[Finding(source="Gravatar", found=True, url="https://gravatar.com/x", evidence="Public profile")],
    )


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"OSINT LOOKUP" in response.data


def test_search_stores_and_returns_findings(client):
    with patch("osint_lookup.webapp.run_lookup", return_value=_fake_result()):
        response = client.post("/api/search", json={"query": "jane@example.com"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["query"] == "jane@example.com"
    assert data["findings"][0]["source"] == "Gravatar"

    # Second read comes straight from storage, no network call needed.
    stored = client.get("/api/lookup?query=jane@example.com")
    assert stored.status_code == 200
    assert stored.get_json()["findings"][0]["url"] == "https://gravatar.com/x"


def test_lookup_missing_query_returns_404(client):
    response = client.get("/api/lookup?query=nobody@example.com")
    assert response.status_code == 404


def test_recent_lists_searched_queries(client):
    with patch("osint_lookup.webapp.run_lookup", return_value=_fake_result()):
        client.post("/api/search", json={"query": "jane@example.com"})

    response = client.get("/api/recent")
    assert response.status_code == 200
    queries = [item["query"] for item in response.get_json()]
    assert "jane@example.com" in queries
