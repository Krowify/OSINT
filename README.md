# OSINT

A small command-line tool that looks up where an email address or a name
shows up in public sources, and reports exactly which source and URL each
hit came from.

## Sources checked

| Source | Query type | Auth needed |
|---|---|---|
| [Gravatar](https://gravatar.com) profile | email | no |
| GitHub public search (user email / commit author email) | email | no (optional `GITHUB_TOKEN` for higher rate limits) |
| GitHub public search (matching display names) | name | no (optional `GITHUB_TOKEN`) |
| [Have I Been Pwned](https://haveibeenpwned.com) breach check | email | yes, `HIBP_API_KEY` (skipped if unset) |
| DuckDuckGo Instant Answer API | name | no |

For anything beyond these APIs (social media, forums, pastes), the tool
prints ready-to-use search-engine queries ("dorks") you can paste into a
browser. It does not scrape search engines directly, since that violates
their terms of service.

## Install

```bash
pip install -r requirements.txt
```

## Usage

### Command line

```bash
python -m osint_lookup.cli someone@example.com
python -m osint_lookup.cli "Jane Doe"
```

### Web UI

A dark, graph-style local web UI is also included: the query sits in the
center and each source that was checked branches off as a dot — bright
green if it was found, dim grey if not, red if the check errored. Click a
found dot to open a small popup with the evidence and a clickable link to
where it was found.

```bash
python -m osint_lookup.webapp
```

Then open http://127.0.0.1:5000 in a browser. Results are saved to a local
SQLite database (`~/.osint_lookup/history.db`), and the browser remembers
your last query, so reopening the app (or the browser tab) restores the
same graph without re-querying the network. A sidebar lists past searches
you can click back into.

Optional environment variables:

- `GITHUB_TOKEN` — raises GitHub API rate limits.
- `HIBP_API_KEY` — enables the Have I Been Pwned breach check.

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

## Responsible use

This tool only queries public APIs and returns their own public data — it
does not scrape, brute-force, or bypass any access controls. Use it only on
your own information or where you have clear authorization (e.g. an
authorized OSINT/security assessment). Do not use it to stalk, harass, or
build dossiers on people without consent.
