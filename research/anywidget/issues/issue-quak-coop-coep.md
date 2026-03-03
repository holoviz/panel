# quak: Requires SharedArrayBuffer (COOP/COEP headers) for DuckDB-WASM

**Status: WORKS** — Not a Panel bug, but a deployment consideration.

## Summary

quak uses DuckDB-WASM which requires `SharedArrayBuffer`, available only when the page is served with `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp` HTTP headers. Without these headers, DuckDB-WASM fails to initialize.

**GitHub Codespaces** sets these headers automatically, so quak works out of the box there.

## Context

Panel's `AnyWidget` pane renders quak correctly. The only consideration is that standalone `panel serve` does not set the COOP/COEP headers by default. This affects any widget using `SharedArrayBuffer` (DuckDB-WASM, certain WebAssembly workloads).

## Workaround for standalone `panel serve`

The headers can be set using Tornado's `transforms` parameter:

```python
import tornado.web

class SecurityHeadersTransform(tornado.web.OutputTransform):
    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return status_code, headers, chunk

pn.serve({"app": app_func}, transforms=[SecurityHeadersTransform])
```

## Suggestion for Panel

Panel could add a `response_headers` parameter to `pn.serve()` to make this easier:

```python
# Proposed API
pn.serve(app, response_headers={
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
})
```

## Why this isn't a problem in JupyterLab / Marimo

- **JupyterLab**: Sets COOP/COEP headers by default in its Tornado server configuration since widgets like DuckDB-WASM need `SharedArrayBuffer`.
- **Marimo**: Ships with these headers enabled from the start.
- **GitHub Codespaces**: Sets the headers at the reverse proxy level.

## Could Panel add them automatically?

The `Cross-Origin-Embedder-Policy: require-corp` header can break loading of external resources (CDN scripts, images, fonts) that don't include a `Cross-Origin-Resource-Policy` header. So enabling it universally could break existing Panel apps that load third-party assets.

Options:
1. **`credentialless` mode** (safer): `Cross-Origin-Embedder-Policy: credentialless` enables `SharedArrayBuffer` without requiring all subresources to opt-in. Supported in Chrome 96+ and Firefox 119+, but not Safari.
2. **Opt-in via `pn.config`**: e.g. `pn.config.cross_origin_isolation = True` or a `--cross-origin-isolation` CLI flag.
3. **Auto-detect**: If any AnyWidget component uses DuckDB-WASM, set the headers automatically. (Hard to detect reliably.)

Recommendation: Add `pn.config.cross_origin_isolation` (default `False`) that sets both headers when enabled. This matches JupyterLab's approach while remaining backward-compatible.

## Environments where it works out of the box

- **GitHub Codespaces**: Sets COOP/COEP headers automatically
- **JupyterLab**: Sets COOP/COEP headers by default
- **Marimo**: Sets COOP/COEP headers by default
- **Custom deployments**: Add the headers to your reverse proxy (nginx, Caddy, etc.)
