#!/usr/bin/env python3
"""Mock docstore server for the example adapter (standard library only).

API (bearer-token protected when a token is configured):

    GET /docs/<id>            -> {"id": "<id>", "latest": <n>}   (404 if unknown)
    GET /docs/<id>/<n>.pdf    -> the revision's bytes             (404 if unknown)

Documents live on disk as <root>/<id>/<n>.pdf, so tests can add, replace or
delete revisions while the server runs. Fault injection for tests:
`force_status` fails every request with that HTTP status, `delay` sleeps before
answering, and `meta_override` replaces the body of the document description.

usage: docstore_server.py ROOT [--token TOKEN] [--port PORT]
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import time


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, body=b"", ctype="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client gave up (timeout test)

    def do_GET(self):
        srv = self.server
        if srv.delay:
            time.sleep(srv.delay)
        if srv.force_status:
            return self.send(srv.force_status, b"{}")
        if srv.token and self.headers.get("Authorization") != f"Bearer {srv.token}":
            return self.send(401, b'{"error":"authentication required"}')
        match = re.fullmatch(r"/docs/([\w-]{1,64})(?:/([1-9]\d*)\.pdf)?", self.path)
        if not match:
            return self.send(404, b'{"error":"not found"}')
        doc, rev = match.groups()
        folder = Path(srv.root) / doc
        if rev:
            path = folder / f"{rev}.pdf"
            if not path.is_file():
                return self.send(404, b'{"error":"no such revision"}')
            return self.send(200, path.read_bytes(), "application/pdf")
        revs = [int(p.stem) for p in folder.glob("*.pdf") if re.fullmatch(r"[1-9]\d*", p.stem)] \
            if folder.is_dir() else []
        if not revs:
            return self.send(404, b'{"error":"no such document"}')
        if srv.meta_override is not None:
            return self.send(200, srv.meta_override)
        return self.send(200, json.dumps({"id": doc, "latest": max(revs)}).encode())


class DocstoreServer(ThreadingHTTPServer):
    def __init__(self, root, token=None, port=0):
        super().__init__(("127.0.0.1", port), Handler)
        self.root, self.token = str(root), token
        self.force_status, self.delay, self.meta_override = 0, 0, None

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server_address[1]}"

    def start(self):
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        return self

    def stop(self):
        self.shutdown()
        self.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root")
    ap.add_argument("--token")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    server = DocstoreServer(args.root, args.token, args.port)
    print(f"serving {args.root} at {server.url}")
    server.serve_forever()
