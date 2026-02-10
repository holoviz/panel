# Panel Live

Browser-based Panel embedding and playground. Run Panel apps entirely client-side using Pyodide.

## Quick Start

```bash
python serve.py
# Open http://localhost:8080/demos/playground.html
```

## Structure

- `src/` — Core library (`panel-embed.js`, `panel-runner.html`)
- `demos/` — Working demo HTML pages
- `poc/` — Experimental prototypes (web component, PyScript, WASM isolation)
- `examples/` — Example Panel Python apps
- `docs/` — Planning, research, and issue tracking

See `docs/live-dream.md` for vision and `docs/live-issues.md` for the roadmap.
