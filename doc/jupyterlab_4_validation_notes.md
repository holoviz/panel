# JupyterLab 4.4–4.6 Validation Notes

> Companion to [stories & tasks](jupyterlab_4_support_stories_and_tasks.md) Epic **E4**.  
> Updated: 2026-08-05 during local implementation / smoke testing.

## E4-S1 — Frontend / stack smoke (Panel + pyviz_comms)

| Check | JL 4.4.9 | JL 4.5.9 | JL 4.6.2 | Notes |
|-------|----------|----------|----------|-------|
| `scripts/check_jupyterlab_stack.py --expect-jl X.Y` | Pass | Pass | Pass | `pyviz_comms` 3.0.6 |
| `@pyviz/jupyterlab_pyviz` in `jupyter labextension list` | Pass | Pass | Pass | Bundled with pyviz_comms |
| `panel.io.jupyter_server_extension` enabled | Pass | Pass | Pass | `_jupyter_server_extension_points` OK |
| `/lab` HTTP 200 | — | — | Pass | Interactive server on `:8887` |
| Preview `/panel-preview/render/...` HTTP 200 + Panel HTML | — | — | Pass | `examples/_jl_smoke/app.py` |
| Unit: `test_jupyter_server_extension_points.py` | Pass (ran in 4.6 env) | — | Pass | Discovery API |

Environments used locally:

- `.venv-jl-test` — JupyterLab **4.6.2** + editable Panel (primary interactive server)
- `.venv-jl45` — JupyterLab **4.5.9** + editable Panel (stack check)
- `/Users/bl44001/gdp/jupyterlab_venv` — JupyterLab **4.4.9** + editable Panel (stack check)

Upstream note: JL 4.6 remains compatible with extensions built for JL 4.0; `@pyviz/jupyterlab_pyviz@3.0.6` loads on 4.4 / 4.5 / 4.6 without rebuild.

## E4-S2 — `jupyter-builder` migration

**Status**: Remains an optional upstream task in **holoviz/pyviz_comms** (not this repository).

Not required for runtime support of published pyviz_comms 3.x wheels on JL 4.6. Track separately if CI build speed for pyviz_comms becomes a priority.

## Interactive URLs (local session)

After starting services from `.venv-jl-test`:

- JupyterLab: http://localhost:8887/lab  
- Panel Preview smoke: http://localhost:8887/panel-preview/render/examples/_jl_smoke/app.py  
- Panel serve smoke: http://127.0.0.1:5007/panel_serve_smoke  
