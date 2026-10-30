"""
Local playground for trying EvalStack scorers in a browser.

Standard library only. Binds to 127.0.0.1 by default. The string scorers
need no API keys; the LLM judge needs the anthropic SDK and credentials, and
uses EVALSTACK_JUDGE_MODEL (default claude-opus-5-5).

    python playground/server.py            # http://127.0.0.1:8765
    python playground/server.py --port 9000
"""

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from evalstack.scorer import ContainsScorer, ExactMatchScorer, LLMJudgeScorer

DEFAULT_JUDGE_MODEL = "claude-opus-5-5"

SCORERS = {
    "exact_match": ExactMatchScorer,
    "contains": ContainsScorer,
    "llm_judge": lambda: LLMJudgeScorer(
        model=os.environ.get("EVALSTACK_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)),
}

INDEX_HTML = Path(__file__).with_name("index.html")
MAX_BODY_BYTES = 1_000_000


def score_request(payload: dict) -> tuple[int, dict]:
    """Run one scorer on a request payload. Returns (http_status, json_body)."""
    name = payload.get("scorer")
    if name not in SCORERS:
        return 400, {"error": f"Unknown scorer: {name!r}"}
    response = payload.get("response", "")
    expected = payload.get("expected", "")
    if not isinstance(response, str) or not isinstance(expected, str):
        return 400, {"error": "response and expected must be strings"}
    try:
        result = SCORERS[name]().score(response, expected)
    except ImportError as exc:
        return 200, {"scorer": name, "unavailable": True, "reason": str(exc)}
    except Exception as exc:  # noqa: BLE001  show any provider error in the page, never as a score
        return 502, {"error": f"{type(exc).__name__}: {exc}"}
    return 200, {
        "scorer": name,
        "value": result.value,
        "passed": result.passed,
        "reason": result.reason,
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data).encode(), "application/json")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX_HTML.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/scorers":
            self._send_json(200, {"scorers": list(SCORERS)})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/score":
            self._send_json(404, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "Request too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        if not isinstance(payload, dict):
            self._send_json(400, {"error": "Expected a JSON object"})
            return
        self._send_json(*score_request(payload))


def main() -> None:
    parser = argparse.ArgumentParser(description="EvalStack scorer playground")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"EvalStack playground on http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
