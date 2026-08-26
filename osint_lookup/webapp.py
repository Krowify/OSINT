"""Local web UI: dark, node-graph view of where an email/name was found.

Run with:
    python -m osint_lookup.webapp

Then open http://127.0.0.1:5000 in a browser. Results are stored in a local
SQLite database (see storage.py) so a previous search reappears after the
app is closed and reopened.
"""

from dataclasses import asdict

from flask import Flask, jsonify, render_template, request

from .cli import run_lookup
from .storage import get_lookup, list_recent, save_lookup

app = Flask(__name__)


def _result_to_json(result) -> dict:
    return {
        "query": result.query,
        "query_type": result.query_type,
        "findings": [asdict(f) for f in result.findings],
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/recent")
def api_recent():
    return jsonify(list_recent())


@app.get("/api/lookup")
def api_get_lookup():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "missing query"}), 400

    result = get_lookup(query)
    if result is None:
        return jsonify({"error": "no stored result for this query"}), 404

    return jsonify(_result_to_json(result))


@app.post("/api/search")
def api_search():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    if not query:
        return jsonify({"error": "missing query"}), 400

    result = run_lookup(query)
    save_lookup(result)
    return jsonify(_result_to_json(result))


def main():
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
