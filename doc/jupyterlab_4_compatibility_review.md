# Panel JupyterLab 4.4.x ~ 4.5.9+ Compatibility Review

> **Scope**: Dependencies, server extension, frontend interaction, and theme integration related to JupyterLab in the Panel codebase  
> **Target versions**: JupyterLab `4.4.x` ~ `4.5.9` and later releases in the same major line (4.x; excluding 5.x)  
> **Review date**: 2026-08-05  
> **Summary**: **Supported overall**. With `pyviz_comms >= 3.0` (suggested `>= 3.0.2`, recommended `>= 3.0.6`), Panel works on JupyterLab 4.4.x ~ 4.5.9+ for notebook rendering, bidirectional comms, and Preview. There are loose lower bounds, deprecated APIs, and outdated docs, but none are blocking incompatibilities for these versions.  
> **Follow-ups**: [Solution plan (4.4–4.6)](jupyterlab_4_support_solution.md) · [Stories & tasks](jupyterlab_4_support_stories_and_tasks.md)

---

## 1. Review verdict

| Capability | JupyterLab 4.4.x | JupyterLab 4.5.0 ~ 4.5.9+ | Notes |
|------------|------------------|---------------------------|-------|
| Render Panel in notebooks / bidirectional sync | Supported | Supported | Requires `@pyviz/jupyterlab_pyviz` from `pyviz_comms` 3.x |
| Jupyter Panel Preview | Supported | Supported | Panel `jupyter_server` extension + pyviz frontend button |
| Layout Builder (drag-and-drop) | Supported | Supported | Docs require `panel >= 1.4.0` and `pyviz_comms >= 3.0.2` |
| Theme adaptation (`--jp-*` CSS variables) | Supported | Supported | Fast / Bootstrap / Material / Native themes adapt |
| Keyboard shortcut suppression | Supported | Supported | `data-lm-suppress-shortcuts` (since Panel 1.4.3) |
| JupyterLite / Panelite | Supported (indirect) | Supported (indirect) | Via `jupyterlite` build path; lite feature pins `pyviz_comms >= 3.0.6` |
| JupyterLab **5.x** | Out of scope | Out of scope | `pyviz_comms` currently builds against `jupyterlab>=4,<5` |

**Overall**: The code and dependency chain target JupyterLab **4.x**. Upstream release notes also state that 4.5 is compatible with extensions that support 4.0. Therefore **4.4.x ~ 4.5.9 and later 4.x releases should work**.

---

## 2. JupyterLab integration architecture

Panel **does not ship** its own JupyterLab frontend labextension. Integration has three layers:

```text
┌─────────────────────────────────────────────────────────────┐
│ JupyterLab 4.4 / 4.5 UI                                     │
│  ├─ @pyviz/jupyterlab_pyviz  (from pyviz_comms)             │
│  │    · MIME rendering / Comm channel / Preview / Layout    │
│  └─ Panel output DOM / CSS (--jp-*, data-lm-suppress-…)     │
├─────────────────────────────────────────────────────────────┤
│ jupyter_server 2.x                                          │
│  └─ panel.io.jupyter_server_extension                       │
│       · /panel-preview/render/*                             │
│       · /panel-preview/*/ws (Bokeh protocol via Kernel Comm)│
├─────────────────────────────────────────────────────────────┤
│ Kernel                                                      │
│  ├─ panel + bokeh + pyviz_comms (in-notebook interaction)   │
│  └─ panel.io.jupyter_executor.PanelExecutor (Preview)       │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Key modules and files

| Module / file | Role |
|---------------|------|
| `panel/io/jupyter_server_extension.py` | Preview HTTP/WS server extension (`JupyterHandler`, kernel proxy) |
| `panel/io/jupyter_executor.py` | Creates a Bokeh session in the kernel; talks to the proxy via `ipykernel.comm.Comm` |
| `panel/io/notebook.py` | Notebook MIME rendering, `push`/`send`, binary Comm buffers, `_jupyter_server_extension_paths` |
| `panel/config.py` | Registers the Jupyter Comm Manager in `pn.extension()` |
| `panel/_templates/doc_nb_js.js` | Sets `data-lm-suppress-shortcuts` after embed |
| `panel/_templates/jupyter.css`, `panel/theme/**` | JupyterLab CSS variables and theme sync |
| `scripts/jupyter-config/server.json` | Enables `jpserver_extensions` on install |
| `scripts/jupyter-config/notebook.json` | Classic Notebook compat (`nbserver_extensions`) |
| `pyproject.toml` | Runtime dep `pyviz_comms >= 2.0.0`; optional `jupyterlab` |

The Preview button and Layout Builder live in [holoviz/pyviz_comms](https://github.com/holoviz/pyviz_comms) (npm: `@pyviz/jupyterlab_pyviz`), **not** in this repository.

---

## 3. Dependency and version constraint review

### 3.1 Dependencies declared by Panel

| Dependency | Declared in | Current constraint | Impact on JL 4.4+ / 4.5.9+ |
|------------|-------------|--------------------|----------------------------|
| `pyviz_comms` | `pyproject.toml` dependencies | `>=2.0.0` | **Risk**: 2.x targets JL 3.x; JL 4.x needs **3.x**. Lower bound is too loose and can yield incompatible installs |
| `pyviz_comms` | `pixi.toml` (default) | `>=2.0.0` | Same as above |
| `pyviz_comms` | `pixi.toml` feature `lite` | `>=3.0.6` | Correct (JupyterLite path) |
| `jupyterlab` | optional `recommended` / pixi features | `*` (no upper bound) | CI/dev can resolve latest 4.x (including 4.5.9+) |
| `jupyter_bokeh` | Not a hard dep; example feature `>=3.0.7` | Optional | Only needed for ipywidgets / VSCode / Colab paths |
| `bokeh` | `>=3.7.0,<3.10.0` | Aligned with current Panel | No direct conflict with JL versions |

### 3.2 pyviz_comms (frontend extension) and JL 4.x

`pyviz_comms` 3.x (upstream currently around 3.0.6) declares:

- Classifier: `Framework :: Jupyter :: JupyterLab :: 4`
- Build: `jupyterlab>=4.0.0,<5`
- npm deps: `@jupyterlab/*` with carets such as `^4.0.3`, covering 4.4 / 4.5
- Compatibility table: JupyterLab **4.x ↔ jupyterlab_pyviz 3.0**

JupyterLab **4.5** release notes state compatibility with extensions that support JupyterLab **4.0**. Therefore `@pyviz/jupyterlab_pyviz@3.x` is usable on 4.4.x ~ 4.5.9+.

### 3.3 Recommended install set (JL 4.4+ / 4.5.9+)

```bash
pip install "panel" "pyviz_comms>=3.0.2" "jupyterlab>=4.4,<5"
# If using ipywidgets-compatible rendering:
pip install jupyter_bokeh
```

When environments are split, install `pyviz_comms` in **both** the JupyterLab environment and the kernel environment.

---

## 4. Server extension API review

### 4.1 Enablement

The wheel installs via hatch `shared-data`:

- `etc/jupyter/jupyter_server_config.d/panel-client-jupyter.json`  
  → `ServerApp.jpserver_extensions["panel.io.jupyter_server_extension"] = true`

This is the standard prebuilt-extension enablement path for JupyterLab 4 / jupyter_server 2, and is **compatible with 4.4 / 4.5**.

### 4.2 Entry points

Current implementation:

```python
# panel/io/notebook.py (re-exported from panel/__init__.py)
def _jupyter_server_extension_paths():
    return [{"module": "panel.io.jupyter_server_extension"}]

# panel/io/jupyter_server_extension.py
def _load_jupyter_server_extension(notebook_app):
    ...
load_jupyter_server_extension = _load_jupyter_server_extension  # legacy alias
```

| API | Status | Impact |
|-----|--------|--------|
| `_load_jupyter_server_extension` | Current recommended loader | OK |
| `load_jupyter_server_extension` (no underscore) | Legacy Notebook Server alias | Harmless |
| `_jupyter_server_extension_paths` | **Deprecated**; jupyter_server still falls back with a warning | Still works on 4.4/4.5 |
| `_jupyter_server_extension_points` | **Current recommended**; **not implemented** by Panel | Future jupyter_server may drop the old API |

**Verdict**: On JupyterLab 4.4 ~ 4.5.9+ (jupyter_server 2.x) the extension **loads and runs**. Adding `_jupyter_server_extension_points` is recommended to silence deprecation warnings and harden future upgrades.

### 4.3 jupyter_server / Tornado APIs in use

`PanelJupyterHandler` / `PanelWSProxy` / `PanelLayoutHandler` use:

- `jupyter_server.base.handlers.JupyterHandler`
- `@tornado.web.authenticated`
- `kernel_manager.start_kernel` / `get_kernel` / `shutdown_kernel`
- `kernel.iopub_channel` / `shell_channel` / Comm messages
- `application.settings["base_url"]`, `server_root_dir` / `contents_manager.root_dir`

These are stable jupyter_server 2.x surfaces. There is **no reliance on public APIs removed between 4.4 and 4.5**. Breaking changes in the JL 4.4/4.5 migration guide mostly affect **frontend labextension TypeScript APIs** (Panel has none); impact on Panel’s server extension is minimal.

### 4.4 Preview routes

| Route | Handler | Purpose |
|-------|---------|---------|
| `panel-preview/render/(.*)` | `PanelJupyterHandler` | Start kernel, run `PanelExecutor`, return HTML |
| `panel-preview/render/(.*)/ws` | `PanelWSProxy` | Bokeh WS ↔ kernel Comm proxy |
| `panel-preview/layout/(.*)` | `PanelLayoutHandler` | Layout Builder JSON |
| `panel-preview/static/...` | Bokeh static handlers | Static assets |
| `panel_dist/(.*)` | `StaticFileHandler` | Panel dist |

`@pyviz/jupyterlab_pyviz` hits these routes when opening Preview; the protocol is not tied to a specific JL minor version.

### 4.5 Minor code-quality issues (non-blocking)

- `PanelWSProxy.open` uses `datetime.utcnow()` (deprecated in Python 3.12+); prefer `datetime.now(datetime.UTC)`.
- `on_close` uses `asyncio.ensure_future`; it works, but can migrate to `create_task` (already used elsewhere in the same file).

---

## 5. Frontend / notebook interaction review

### 5.1 JupyterLab 4 Comm messages

Since Panel **1.1.1** (#5140), JupyterLab 4 Comm message formats are handled. Current `JupyterCommJSBinary` / `send()` buffer and metadata handling matches JL 4.x / ipykernel Comm behavior.

### 5.2 Keyboard shortcuts (JL 4.1+ interaction model)

After embed, `panel/_templates/doc_nb_js.js` sets on root children:

```js
child.setAttribute('data-lm-suppress-shortcuts', 'true')
```

This matches the JupyterLab notebook keyboard interaction model (docs reference 4.1.x). The attribute remains valid on Lumino 2 / JL 4.4 / 4.5 (since Panel **1.4.3** / #6825).

### 5.3 CSS variables and themes

`--jp-*` variables in use (e.g. `--jp-brand-color0`, `--jp-layout-color0`, `--jp-ui-font-color0`) are stable JupyterLab 4 theme tokens. The Fast design detects `window._JUPYTERLAB` and reads them. **No breaking removals observed for 4.4 / 4.5**.

`.lm-Widget` selectors in `jupyter.css` match Lumino 2 (JL 4) naming; Panel already uses `lm-` rather than the deprecated Lumino `p-` prefix.

### 5.4 IPyWidget embedding

`panel/models/ipywidget.ts`:

1. Prefer classic: `Jupyter.notebook.kernel.widget_manager`
2. Else: `window.PyViz.widget_manager` (provided by pyviz_comms in JL)

On JupyterLab 4.x the second path is used — **correct by design**.

---

## 6. Testing and CI

| Item | Status |
|------|--------|
| UI test env | `pixi` features `test-ui` / `test` use `jupyterlab = "*"` |
| Preview tests | `panel/tests/ui/io/test_jupyter_server_extension.py` (needs a Jupyter server) |
| JupyterLite tests | `panel/tests/ui/io/test_jupyterlite.py` (JL 4 DOM such as `jp-button`, `.jp-Notebook-ExecutionIndicator`) |
| Test config | `panel/tests/ui/jupyter_server_test_config.py` uses `LabApp.expose_app_in_browser` (still valid on JL 4) |
| Version matrix | **No** fixed dual matrix for 4.4.x vs 4.5.x; resolution follows latest 4.x |

CI enables the extension and starts JupyterLab:

```bash
jupyter server extension enable panel.io.jupyter_server_extension --sys-prefix
jupyter lab --config panel/tests/ui/jupyter_server_test_config.py --port 8887
```

This shows the enablement path is maintained for jupyter_server 2 / JL 4.

---

## 7. Documentation issues (do not affect runtime compatibility)

`doc/how_to/notebook/notebook.md` still documents classic installs:

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install @bokeh/jupyter_bokeh
```

On JupyterLab **3+ / 4.x**, those extensions usually install as **prebuilt** packages via pip/conda; `jupyter labextension install` is unnecessary. The docs are outdated and can mislead 4.4/4.5 users, but **do not change the code compatibility conclusion**.

The Layout Builder guide (`doc/how_to/notebook/layout_builder.md`) correctly states `pyviz_comms >= 3.0.2`.

---

## 8. JupyterLab 4.4 → 4.5 migration impact

Against the [Extension Migration Guide](https://jupyterlab.readthedocs.io/en/latest/extension/extension_migration.html):

| Change category | Affects Panel? |
|-----------------|----------------|
| Frontend plugin ID / token renames (4.3→4.4, 4.4→4.5) | No (no Panel labextension; owned by pyviz_comms) |
| File Browser `selectionChanged`, etc. | No |
| `extra_labextensions_path` precedence | Low risk; Panel uses the standard share/jupyter install path |
| Shared model / Yjs output format | No (Panel does not write cell shared models directly) |
| jupyter_server handler APIs | No (APIs in use remain stable) |

**4.5.9 and later patch/minor releases in 4.x**: expected to keep working under SemVer and the upstream “compatible with 4.0 extensions” commitment. The release that warrants a fresh review is future **JupyterLab 5**.

---

## 9. Risks and recommendations

### 9.1 High priority

1. **Tighten the `pyviz_comms` lower bound**  
   - Change `pyviz_comms >= 2.0.0` in `pyproject.toml` / `pixi.toml` to `>= 3.0.0` (or `>= 3.0.2`).  
   - Avoid installs of pyviz_comms 2.x (JL 3–only) into JL 4.4/4.5 environments.

2. **Implement `_jupyter_server_extension_points`**  
   - Keep `_jupyter_server_extension_paths` for compatibility; silence jupyter_server deprecation warnings and reduce future breakage risk.

### 9.2 Medium priority

3. Update JL 4 install instructions in `doc/how_to/notebook/notebook.md` (remove outdated `labextension install` steps).  
4. Replace `datetime.utcnow()` with a timezone-aware API.  
5. Add an explicit JupyterLab version axis in CI (e.g. `4.4.*` and `4.5.*`) so `*` resolution cannot hide regressions.

### 9.3 Low priority / informational

6. State clearly in the README or getting started: **JupyterLab 4.x requires pyviz_comms 3.x**.  
7. Before JupyterLab 5, track `pyviz_comms`’s `<5` build cap and API migration.

---

## 10. Verification checklist (manual / CI)

On JupyterLab **4.4.x** and **4.5.9+**, confirm:

- [ ] After `pn.extension()`, components render and widget interactions sync back to Python  
- [ ] Toolbar **Jupyter Panel Preview** opens and `.servable()` apps display  
- [ ] Preview Manual Reload / Render on save work  
- [ ] Layout Builder works when `.servable()` is not used (`pyviz_comms >= 3.0.2`)  
- [ ] Panel theme variables follow JL Light/Dark switches  
- [ ] Typing in Panel inputs does not trigger notebook global shortcuts  
- [ ] `jupyter server extension list` shows `panel.io.jupyter_server_extension` enabled  
- [ ] (Optional) `comms='ipywidgets'` + `jupyter_bokeh` path works  

Quick self-check:

```bash
jupyter lab --version          # expect 4.4.x or 4.5.x+
python -c "import pyviz_comms; print(pyviz_comms.__version__)"  # expect >= 3.0
jupyter server extension list  | grep -i panel
jupyter labextension list      | grep -i pyviz
```

---

## 11. Final determination

| Question | Determination |
|----------|---------------|
| Supports JupyterLab **4.4.x**? | **Yes** |
| Supports JupyterLab **4.5.0 ~ 4.5.9**? | **Yes** |
| Supports **later 4.x versions above 4.5.9**? | **Yes** (with pyviz_comms 3.x and the current Panel server extension) |
| Unconditionally supported for any dependency versions? | **No**; **pyviz_comms 3.x** is required; do not mix JL 3–only extensions |
| Commitment for JupyterLab **5**? | **No** (out of scope; needs separate pyviz_comms / Panel adaptation) |

**Bottom line**: Panel’s current code paths **support JupyterLab 4.4.x ~ 4.5.9 and later 4.x releases**. Keep runtime `pyviz_comms` on 3.x, and prefer adding `_jupyter_server_extension_points` plus a tighter dependency lower bound to reduce operational and upgrade risk.
