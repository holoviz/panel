"""
Minimal HTTP server with Cross-Origin Isolation headers.

These headers enable SharedArrayBuffer, which Pyodide needs for efficient
WASM memory management. Without them, Pyodide uses a fallback that roughly
doubles memory usage, often causing STATUS_ACCESS_VIOLATION crashes.

Usage:
    python serve.py [port]
    # Default: http://localhost:8080
"""
import sys

from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler


class COOPCOEPHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
print(f"Serving on http://localhost:{port} (with COOP/COEP headers)")
HTTPServer(("", port), partial(COOPCOEPHandler, directory=".")).serve_forever()
