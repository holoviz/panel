# Solution Plan: Official JupyterLab 4.4–4.6 Support for Panel

> **Goal**: Make Panel **explicitly supported, tested, and documented** on JupyterLab **4.4.x**, **4.5.x (including 4.5.9)**, and **4.6.x**.  
> **Related**: [Compatibility review](jupyterlab_4_compatibility_review.md) · [Stories & tasks](jupyterlab_4_support_stories_and_tasks.md)  
> **Date**: 2026-08-05  
> **Status**: Proposed implementation plan (not yet executed)

---

## 1. Problem statement

Panel already **largely works** on JupyterLab 4.x when `pyviz_comms` 3.x is installed. Gaps that prevent claiming first-class support:

| Gap | Impact |
|-----|--------|
| `pyviz_comms >= 2.0.0` allows JL3-only 2.x packages | Users on JL 4.4–4.6 can install a broken combo |
| No `_jupyter_server_extension_points` | Deprecation warnings; future jupyter_server breakage risk |
| CI uses `jupyterlab = "*"` with no 4.4 / 4.5 / 4.6 matrix | Regressions can slip by |
| Docs still show classic `jupyter labextension install` | Misleading for JL 4.x users |
| No published support matrix for 4.4 / 4.5 / 4.6 | Support claims are informal |
| Frontend Preview/Layout Builder owned by **pyviz_comms** | Panel alone cannot guarantee JL 4.6 UI without coordinating upstream |

**Target outcome**: Panel declares, tests, and documents support for JupyterLab `>=4.4,<5` (covering 4.4, 4.5.9, and 4.6), with clear dependency requirements and a coordinated pyviz_comms validation path.

---

## 2. Support policy (what “supported” means)

### 2.1 Supported versions

| JupyterLab | Support level | Notes |
|------------|---------------|-------|
| 4.4.x | **Supported** | Baseline; CI matrix cell |
| 4.5.x (incl. 4.5.9) | **Supported** | CI matrix cell |
| 4.6.x | **Supported** | CI matrix cell; extensions supporting JL 4.0 remain valid per upstream |
| 4.0–4.3 | Best-effort | Not required in CI matrix |
| 5.x | Out of scope | Separate epic when pyviz_comms / JL5 land |

### 2.2 Required companion packages

| Package | Minimum for JL 4.4–4.6 | Role |
|---------|------------------------|------|
| `pyviz_comms` | **`>=3.0.2`** (recommend latest 3.x, e.g. `>=3.0.6`) | Labextension: MIME, Comms, Preview button, Layout Builder |
| `jupyter_server` | 2.x (pulled in by JupyterLab) | Hosts Panel Preview extension |
| `jupyter_bokeh` | Optional (`>=3.0.7` if used) | ipywidgets / VSCode / Colab path only |
| `panel` | Current mainline (post-hardening changes below) | Server extension + notebook embedding |

### 2.3 Supported features under this policy

1. Notebook rendering + bidirectional Python↔JS sync  
2. Jupyter Panel Preview (`.servable()` apps)  
3. Layout Builder (`pyviz_comms >= 3.0.2`)  
4. Theme sync via `--jp-*` CSS variables  
5. Keyboard shortcut suppression (`data-lm-suppress-shortcuts`)  
6. JupyterLite / Panelite (existing lite path; smoke-test on one JL 4.x line)

---

## 3. Architecture and ownership

```text
┌──────────────────────────── Panel repo ────────────────────────────┐
│ · pyviz_comms lower bound                                          │
│ · _jupyter_server_extension_points                                 │
│ · Preview handlers (jupyter_server_extension / jupyter_executor)   │
│ · Notebook embed JS/CSS (shortcuts, --jp-*)                        │
│ · Docs + CI matrix (JL 4.4 / 4.5 / 4.6)                            │
└────────────────────────────┬───────────────────────────────────────┘
                             │ depends on
┌────────────────────────────▼───────────────────────────────────────┐
│ pyviz_comms (upstream)                                             │
│ · @pyviz/jupyterlab_pyviz prebuilt extension                       │
│ · Preview UI, Layout Builder, Comm MIME handlers                   │
│ · Build against JL 4.x; validate on 4.4 / 4.5 / 4.6                │
│ · Optional later: migrate build to jupyter-builder (JL 4.6 tooling)│
└────────────────────────────────────────────────────────────────────┘
```

**Principle**: Panel hardens its own server/notebook surface and dependency policy; **pyviz_comms** remains the source of the JupyterLab UI extension. Work is split into Panel PRs and (if needed) pyviz_comms PRs/releases.

---

## 4. Solution phases

### Phase A — Dependency & packaging hardening (Panel) — *P0*

**Objective**: Make “install Panel + JupyterLab 4.4–4.6” land on a compatible stack by default.

#### A1. Raise `pyviz_comms` lower bound

**Files**:
- `pyproject.toml` → `dependencies`: `pyviz_comms >= 3.0.2` (or `>= 3.0.0` minimum; prefer `>= 3.0.2` to match Layout Builder docs)
- `pixi.toml` → align default / test features with the same bound (lite already has `>=3.0.6`)
- `pyproject.toml` build-system `requires` if it still mentions older comms bounds

**Acceptance**:
- Fresh `pip install panel jupyterlab==4.5.9` resolves `pyviz_comms` 3.x
- Document CHANGELOG entry under Compatibility

#### A2. Optional JupyterLab pin in extras

```toml
[project.optional-dependencies]
recommended = [
    'jupyterlab >=4.4,<5',
    ...
]
jupyter = [
    'jupyterlab >=4.4,<5',
    'pyviz_comms >=3.0.2',
]
```

Keeps `jupyterlab` optional (Panel is not JL-only) but documents the supported range for people who install the extra.

---

### Phase B — Server extension modernization (Panel) — *P0*

**Objective**: Load cleanly on jupyter_server 2.x used by JL 4.4–4.6 without deprecation warnings.

#### B1. Add `_jupyter_server_extension_points`

**Files**:
- `panel/io/notebook.py` (definition)
- `panel/io/__init__.py` and `panel/__init__.py` (exports)

```python
def _jupyter_server_extension_points() -> list[dict[str, str]]:
    return [{"module": "panel.io.jupyter_server_extension"}]

# Keep legacy name as alias for older tooling
def _jupyter_server_extension_paths() -> list[dict[str, str]]:
    return _jupyter_server_extension_points()
```

**Acceptance**:
- `jupyter server extension list` shows Panel enabled
- No warning: `_jupyter_server_extension_points` function was not found…
- Preview routes still register under JL 4.4 / 4.5 / 4.6

#### B2. Keep hatch shared-data config

Retain:

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "panel.io.jupyter_server_extension": true
    }
  }
}
```

No change required unless path/module rename occurs (it should not).

#### B3. Small cleanups in Preview handlers

**File**: `panel/io/jupyter_server_extension.py`

| Change | Why |
|--------|-----|
| Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` (or `timezone.utc`) | Python 3.12+ deprecation; JL stacks often use newer Python |
| Prefer `asyncio.create_task` over `ensure_future` in `on_close` | Consistency / future asyncio hygiene |

**Acceptance**: Unit/UI Preview tests pass; no behavior change in token expiry checks.

---

### Phase C — CI matrix for JL 4.4 / 4.5 / 4.6 (Panel) — *P0*

**Objective**: Prove support continuously.

#### C1. Pixi environments (or matrix dimensions)

Add explicit environments / matrix cells, for example:

| Env | Pin |
|-----|-----|
| `test-ui-jl44` | `jupyterlab = "4.4.*"` |
| `test-ui-jl45` | `jupyterlab = "4.5.*"` |
| `test-ui-jl46` | `jupyterlab = "4.6.*"` |

Shared deps: `pyviz_comms >= 3.0.2`, existing UI test stack.

#### C2. Workflow changes (`.github/workflows/test.yaml`)

Extend the UI / Jupyter job matrix:

```yaml
matrix:
  os: ["ubuntu-latest"]  # expand macOS/Windows later if cost allows
  jupyterlab: ["4.4.*", "4.5.*", "4.6.*"]
```

For each cell:

1. Install env with pinned JL  
2. `jupyter server extension enable panel.io.jupyter_server_extension --sys-prefix`  
3. Start `jupyter lab` with `panel/tests/ui/jupyter_server_test_config.py`  
4. Run Jupyter-marked UI tests (`--jupyter`), at least:
   - `panel/tests/ui/io/test_jupyter_server_extension.py`
   - Notebook smoke (render + interact) if available
5. Upload screenshots/logs on failure

**Cost control**: Full UI suite on `ubuntu` × 3 JL versions; keep broader OS matrix on a single JL (e.g. latest 4.6).

#### C3. Smoke checklist automation

Add a small script or pytest module that asserts:

```text
jupyter lab --version          # matches cell pin
pyviz_comms.__version__ >= 3.0.2
@pyviz/jupyterlab_pyviz enabled in labextension list
panel.io.jupyter_server_extension enabled
```

---

### Phase D — pyviz_comms validation & optional build migration — *P0/P1*

**Objective**: Ensure the **frontend** extension Panel relies on works on 4.4–4.6 (especially 4.6 build-tooling changes).

Upstream states JL **4.6 is compatible with extensions supporting JL 4.0**. Existing `@pyviz/jupyterlab_pyviz@3.x` should **run** without rebuild. Still validate and optionally modernize.

#### D1. Validation in pyviz_comms (coordinate with maintainers)

Manual / CI smoke on JL 4.4, 4.5, 4.6:

- [ ] MIME render of Panel/HoloViews output  
- [ ] Bidirectional Comm updates  
- [ ] Preview button opens Panel Preview tab  
- [ ] Layout Builder loads and saves layout  
- [ ] No console errors from `@pyviz/jupyterlab_pyviz`

If failures appear only on 4.6, open pyviz_comms issues/PRs (not Panel-only fixes).

#### D2. Optional: migrate pyviz_comms build to `jupyter-builder` (JL 4.6 tooling)

Per [JL 4.5→4.6 migration](https://jupyterlab.readthedocs.io/en/stable/extension/extension_migration.html):

1. `pyproject.toml` build requires: replace `jupyterlab` with `jupyter-builder>=1.0.0`  
2. `package.json`: `@jupyterlab/builder` → `@jupyter/builder`  
3. Scripts: `jupyter labextension build` → `jupyter-builder build`

**Priority**: P1 — improves CI/build speed; not required for runtime compatibility of already-published wheels.

#### D3. Pin strategy for Panel

- Runtime: `pyviz_comms >= 3.0.2` (no upper pin unless a known break appears)  
- If a pyviz_comms fix release is needed for 4.6: bump Panel’s lower bound to that version and note in CHANGELOG

---

### Phase E — Documentation & support matrix — *P1*

**Objective**: Users and support know exactly what works.

#### E1. User-facing docs

Update:

| Doc | Change |
|-----|--------|
| `doc/how_to/notebook/notebook.md` | Remove obsolete `jupyter labextension install` steps; document JL 4.x + `pyviz_comms>=3.0.2` |
| `doc/how_to/notebook/jupyterlabpreview.md` | Add version prerequisites table |
| `doc/how_to/notebook/layout_builder.md` | Confirm bounds; cross-link support matrix |
| `doc/getting_started/installation.md` (if present) | Optional JL extra / version note |
| `README.md` | One-line JL 4.4–4.6 support mention if appropriate |

#### E2. Publish support matrix page

Add `doc/how_to/notebook/jupyterlab_support.md` (or under explanation) with:

- Supported JL versions  
- Required `pyviz_comms`  
- Split-environment install rules  
- Feature checklist  
- Link to this solution + compatibility review  

#### E3. Developer docs

Add a short section in `doc/developer_guide/` pointing to:

- How to run UI tests against a pinned JL  
- How Preview server extension is loaded  

#### E4. CHANGELOG

Under Compatibility:

- Raise `pyviz_comms` requirement for JupyterLab 4  
- Add `_jupyter_server_extension_points`  
- Document tested JupyterLab 4.4 / 4.5 / 4.6  

---

### Phase F — Hardening & edge cases — *P2*

| Item | Action |
|------|--------|
| Keyboard shortcuts on JL 4.6 | Re-verify `data-lm-suppress-shortcuts` (4.6 focused a11y/shortcuts) |
| Theme tokens | Confirm `--jp-*` used by Panel still exist; ignore new datagrid/focus tokens unless Panel themes need them |
| `PanelWSProxy` auth | Review `get_current_user` / `check_origin` looseness for security follow-up (separate from version support) |
| JupyterLite | Smoke Panelite build once against a JL 4.6-based JupyterLite if/when lite stack upgrades |
| Classic Notebook / Notebook 7 | Smoke Preview enablement still works via `jupyter_server` config |

---

## 5. Concrete code change list (Panel)

| # | File | Change |
|---|------|--------|
| 1 | `pyproject.toml` | `pyviz_comms >= 3.0.2`; optional `jupyterlab >=4.4,<5` |
| 2 | `pixi.toml` | Align bounds; add `test-ui-jl44/45/46` features or matrix pins |
| 3 | `panel/io/notebook.py` | Add `_jupyter_server_extension_points`; alias old name |
| 4 | `panel/io/__init__.py` | Export new symbol |
| 5 | `panel/__init__.py` | Export new symbol |
| 6 | `panel/io/jupyter_server_extension.py` | UTC datetime; optional asyncio cleanup |
| 7 | `.github/workflows/test.yaml` | JL version matrix for Jupyter UI tests |
| 8 | `doc/how_to/notebook/*.md` | JL 4.4–4.6 install & support docs |
| 9 | `CHANGELOG.md` | Compatibility notes |
| 10 | New: `doc/how_to/notebook/jupyterlab_support.md` | Public support matrix |
| 11 | New tests (optional) | Assert extension points discovery / version smoke |

**Out of Panel repo (coordinate)**:

| # | Repo | Change |
|---|------|--------|
| U1 | `holoviz/pyviz_comms` | CI smoke on JL 4.4 / 4.5 / 4.6 |
| U2 | `holoviz/pyviz_comms` | Optional `jupyter-builder` migration |
| U3 | `holoviz/pyviz_comms` | Bugfix release if 4.6 UI issues found → Panel bumps lower bound |

---

## 6. Verification plan

### 6.1 Automated

For each of JL **4.4.***, **4.5.***, **4.6.*** on Linux:

1. Extension enablement smoke  
2. `test_jupyter_server_extension.py` (Preview render, custom resources, kernel error, theme query)  
3. Representative notebook UI test (widget interaction)  
4. (Optional weekly) full UI suite on latest 4.6 only  

### 6.2 Manual acceptance (once per JL minor)

Use checklist in [compatibility review §10](jupyterlab_4_compatibility_review.md#10-verification-checklist-manual--ci) on:

- Fresh conda/pip env with pinned JL  
- Split env (JL in env A, kernel in env B) with `pyviz_comms` in both  

### 6.3 Exit criteria for “support complete”

- [ ] Dependency lower bound prevents pyviz_comms 2.x  
- [ ] `_jupyter_server_extension_points` shipped  
- [ ] CI green on 4.4, 4.5, and 4.6 cells for Preview + Jupyter markers  
- [ ] User docs + support matrix published  
- [ ] pyviz_comms validated (or release bumped) on 4.6  
- [ ] CHANGELOG compatibility section written  

---

## 7. Rollout strategy

| Step | Action |
|------|--------|
| 1 | Land Phase A+B in one PR (deps + extension points + small cleanups) |
| 2 | Land Phase C CI matrix (may be second PR if lockfile churn is large) |
| 3 | Run manual + CI validation; file pyviz_comms issues if UI fails on 4.6 |
| 4 | Land Phase E docs |
| 5 | Announce in release notes: “JupyterLab 4.4–4.6 supported; requires pyviz_comms>=3.0.2” |
| 6 | Track Phase F as follow-ups |

**Risk**: Raising `pyviz_comms` to 3.x **drops** automatic support for JupyterLab 3 via the default install. That is acceptable if Panel has already standardized on JL 4 (comms 3.x era); call out in CHANGELOG. If JL 3 must remain installable, use an environment marker (usually unnecessary in 2026).

---

## 8. Timeline estimate (indicative)

| Phase | Effort | Owner focus |
|-------|--------|-------------|
| A Dependency hardening | 0.5–1 day | Panel packaging |
| B Server extension points + cleanups | 0.5–1 day | Panel IO |
| C CI matrix | 1–2 days | Panel CI |
| D pyviz_comms validation / optional builder migrate | 1–3 days | pyviz_comms + Panel QA |
| E Docs & matrix page | 0.5–1 day | Docs |
| F Edge hardening | 1 day (as needed) | Panel + QA |

**Total calendar time** (single engineer, with review): ~1–2 weeks including CI lockfile and upstream coordination.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| pyviz_comms breaks only on JL 4.6 UI | Validate early (Phase D); block “4.6 supported” claim until fixed or waived |
| CI cost triples | Matrix Jupyter tests on ubuntu only; full OS matrix on one JL version |
| Users pinned to pyviz_comms 2.x | CHANGELOG + migration note; error/docs if Preview button missing |
| jupyter_server removes `_paths` before Panel upgrades | Ship `_points` in the same release as support claim |
| JL 4.6 shortcut/a11y changes steal keys again | Re-test suppression attribute; adjust embed JS if needed |

---

## 10. Non-goals

- JupyterLab **5** support  
- Rewriting Preview as a Panel-owned labextension  
- Making `jupyterlab` a hard runtime dependency of Panel  
- Guaranteeing Classic Notebook 6.x beyond existing best-effort paths  

---

## 11. Summary

To **officially** support JupyterLab 4.4–4.5.9 and 4.6:

1. **Require** `pyviz_comms >= 3.0.2` and document `jupyterlab >=4.4,<5`.  
2. **Modernize** the jupyter_server extension entry point.  
3. **Test** Preview and Jupyter UI flows on **4.4, 4.5, and 4.6** in CI.  
4. **Validate** `@pyviz/jupyterlab_pyviz` on those versions (migrate its build tooling optionally).  
5. **Publish** a support matrix and fix outdated install docs.

Panel’s runtime integration is already JL 4-capable; this plan converts that into an explicit, regression-proof support commitment.
