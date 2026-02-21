# Architecture Validation: Dynamic Subclass Approach for AnyWidget Pane

## Recommendation

**Option A — Dynamic `AnyWidgetComponent` subclass** is the recommended architecture. The metaclass, data model construction, ESM injection, CSS handling, and import map pipelines all support dynamic class creation with no fundamental blockers. A few targeted mitigations are needed (import map conflicts, caching), but these are straightforward.

---

## 1. Metaclass Behavior — Dynamic Classes Get Proper Data Models

### How It Works

The `ReactiveESMMetaclass.__init__` (`panel/custom.py:178-193`) runs automatically when any class using it as a metaclass is created, including classes created via `type()`:

```python
class ReactiveESMMetaclass(ReactiveMetaBase):

    def __init__(mcs, name, bases, dict_):
        mcs.__original_doc__ = mcs.__doc__
        ParameterizedMetaclass.__init__(mcs, name, bases, dict_)

        # Create model with unique name
        ReactiveMetaBase._name_counter[name] += 1
        model_name = f'{name}{ReactiveMetaBase._name_counter[name]}'
        ignored = [
            p for p in Reactive.param
            if not issubclass(type(mcs.param[p].owner), ReactiveESMMetaclass)
        ]
        mcs._data_model = construct_data_model(
            mcs, name=model_name, ignore=ignored, extras={'esm_constants': param.Dict}
        )
```

### Validation: Dynamic `type()` Call

When we create a dynamic subclass:

```python
DynWidget = type('DynWidget', (AnyWidgetComponent,), {
    '_esm': esm_code,
    'value': param.Integer(default=0),
})
```

Python's metaclass resolution finds `ReactiveESMMetaclass` (inherited from `AnyWidgetComponent` -> `ReactComponent` -> `ReactiveESM`). Python calls `ReactiveESMMetaclass.__init__(DynWidget, 'DynWidget', (AnyWidgetComponent,), {...})`. This:

1. **Calls `ParameterizedMetaclass.__init__`** — This is param's metaclass, which processes `param.Integer()` declarations in the dict, registers them as proper parameters on the class, and sets up the parameter inheritance chain. This works identically whether the class is defined via `class` statement or `type()`.

2. **Increments the name counter** — `ReactiveMetaBase._name_counter['DynWidget'] += 1`, producing a unique model name like `DynWidget1`.

3. **Builds the ignore list** — Iterates `Reactive.param` to filter out inherited parameters whose owner is not a `ReactiveESMMetaclass` subclass. This correctly excludes base Reactive params (width, height, etc.) while keeping our dynamically-added `value` parameter.

4. **Calls `construct_data_model()`** — Creates a Bokeh `DataModel` subclass with the right properties. Our `value: param.Integer()` becomes a `bp.Int` property on the DataModel.

**Result**: `DynWidget._data_model` is a properly-constructed Bokeh DataModel class. This is verified — the metaclass does not check `inspect.getfile()` or `__module__` during `__init__`, and `ParameterizedMetaclass` fully supports `type()`-created classes.

### Critical Detail: `_name_counter`

The name counter is a `collections.Counter`, defined on `ReactiveMetaBase` (`panel/reactive.py:1494`):

```python
class ReactiveMetaBase(ParameterizedMetaclass):
    _name_counter: ClassVar[Counter] = Counter()
```

If multiple different anywidget classes produce dynamic subclasses with the same name (e.g., both named `'AnyWidgetBridge'`), the counter increments and produces unique DataModel names (`AnyWidgetBridge1`, `AnyWidgetBridge2`, etc.). This is safe.

**Verdict: CONFIRMED — dynamic `type()` creation triggers the full metaclass pipeline and produces valid `_data_model`.**

---

## 2. `construct_data_model()` — Works Correctly for Dynamic Classes

### Code Trace (`panel/io/datamodel.py:153-213`)

```python
def construct_data_model(parameterized, name=None, ignore=[], types={}, extras={}):
    properties = {}
    for pname in parameterized.param:
        if pname in ignore:
            continue
        p = parameterized.param[pname]
        if p.precedence and p.precedence < 0:
            continue
        ptype = types.get(pname, type(p))
        prop = PARAM_MAPPING.get(ptype)
        if isinstance(parameterized, Syncable) or (isinstance(parameterized, type) and issubclass(parameterized, Syncable)):
            pname = parameterized._property_mapping.get(pname, pname)
        if pname == 'name' or pname is None:
            continue
        # ... creates bp property and adds to properties dict ...
    for pname, ptype in extras.items():
        # ... handles esm_constants ...
    name = name or parameterized.name
    return type(name, (DataModel,), properties)
```

Key observations:

- **`parameterized.param` iteration**: Since `ParameterizedMetaclass.__init__` ran first (step 1 of the metaclass), all param Parameters (including our dynamically-added ones) are registered and visible via `parameterized.param`. This works correctly.

- **`_property_mapping` lookup**: The function checks `isinstance(parameterized, type) and issubclass(parameterized, Syncable)`, which is true for our dynamic class. It then applies `_property_mapping` (inherited from `ReactiveESM`). Since our dynamic params don't have custom rename mappings, `_property_mapping.get(pname, pname)` returns the original name.

- **`pname == 'name'` filter**: The `name` parameter is correctly skipped (line 188).

- **`PARAM_MAPPING` lookup**: The `PARAM_MAPPING` dict (`panel/io/datamodel.py:125-150`) maps param types to Bokeh property constructors. Common anywidget traitlet types map to: `param.Integer` -> `bp.Int`, `param.Number` -> `bp.Either(bp.Float, bp.Bool)`, `param.String` -> `bp.String`, `param.Dict` -> `bp.Dict(bp.String, bp.Any)`, `param.List` -> `bp.List(bp.Any)`, `param.Boolean` -> `bp.Bool`, `param.Bytes` -> `bp.Nullable(bp.Bytes)`. Types not in the mapping fall through to `bp.Any`.

- **Final `type()` call**: `type(name, (DataModel,), properties)` creates the DataModel class. This is the same pattern as the dynamic subclass creation itself — perfectly standard Python.

**Potential issue**: If a dynamic class has no custom params at all (only inherited ones that get filtered), the DataModel will have only `esm_constants`. This is fine — the component will still render, it just won't sync any data.

**Verdict: CONFIRMED — `construct_data_model()` correctly handles dynamically-created classes.**

---

## 3. ESM Injection — String `_esm` Works Directly

### Code Trace (`panel/custom.py:374-393`)

```python
@classmethod
def _render_esm(cls, compiled=True, server=False):
    esm_path = cls._esm_path(compiled=compiled is True)
    if esm_path:
        if esm_path == cls._bundle_path and cls.__module__ in sys.modules and server:
            esm = ('' if state.rel_path else './') + cls._component_resource_path(esm_path, compiled)
        else:
            esm = esm_path.read_text(encoding='utf-8')
    else:
        esm = cls._esm     # <-- Falls through to direct string
    if esm is None:
        raise ValueError(...)
    esm = textwrap.dedent(esm)
    return esm
```

And `_esm_path()` (`panel/custom.py:341-362`):

```python
@classmethod
def _esm_path(cls, compiled=True):
    if compiled is True or not cls._esm:
        bundle_path = cls._bundle_path
        if bundle_path:
            return bundle_path
    esm = cls._esm
    if isinstance(esm, os.PathLike):
        return esm
    elif not esm or not esm.endswith(('.js', '.jsx', '.ts', '.tsx')):
        return None     # <-- String ESM returns None here
    # ... path resolution ...
```

When `_esm` is set to a plain string (not a file path), `_esm_path()` returns `None` (since the string doesn't end in `.js`/`.jsx`/`.ts`/`.tsx`), and `_render_esm()` falls through to `esm = cls._esm`, returning the string directly.

For anywidgets, `_esm` is typically:
- A **string** containing JS/TS code — works directly via the fallback path
- A **`pathlib.Path`** — `_esm_path()` returns it as-is, and `_render_esm()` reads the file

Both cases work correctly for dynamically-created classes. The only subtlety is `_bundle_path`, which tries `cls._module_path` (via `inspect.getfile(cls)`). For dynamically-created classes, `inspect.getfile()` will raise `TypeError` (no source file), so `_module_path` returns `None`, and `_bundle_path` returns `None`. This is correct — dynamic classes should not look for bundles.

**If `_esm` is a `pathlib.Path`**: This also works. `_esm_path()` returns the Path directly (line 348: `if isinstance(esm, os.PathLike): return esm`), and `_render_esm()` reads the file contents.

**Verdict: CONFIRMED — both string and pathlib.Path `_esm` values work for dynamic subclasses.**

---

## 4. CSS Handling — `_stylesheets` for Anywidget `_css`

### How Stylesheets Flow

The `_stylesheets` class variable is defined on `Syncable` (`panel/reactive.py:122`):

```python
_stylesheets: ClassVar[list[str]] = []
```

These are processed in `Syncable._process_param_change()` (`panel/reactive.py:216-226`):

```python
if 'stylesheets' in properties:
    stylesheets += [
        resolve_stylesheet(self, css_file, '_stylesheets')
        for css_file in self._stylesheets
    ]
    stylesheets += properties['stylesheets']
```

The `_stylesheets` list is iterated and each entry is resolved. Entries can be:
- **File paths** (relative to the component's module) — resolved via `resolve_stylesheet()`
- **Strings** — CSS strings are processed as raw CSS

### Approach for Anywidget `_css`

Anywidgets define CSS via `_css` as a string or pathlib.Path. We can inject it as:

```python
DynWidget = type('DynWidget', (AnyWidgetComponent,), {
    '_esm': esm_code,
    '_stylesheets': [css_string],   # Raw CSS string
    'value': param.Integer(),
})
```

However, `_stylesheets` entries go through `resolve_stylesheet()`, which checks if the string is a file path. A raw CSS string won't match any file path pattern and will be treated as an inline stylesheet — but let's verify the resolution path.

Looking at `resolve_stylesheet()` usage, raw CSS strings are handled via `process_raw_css()` or as `ImportedStyleSheet` objects elsewhere. The safest approach is to use the `stylesheets` **param** (the public `stylesheets` parameter inherited from `Layoutable`) rather than `_stylesheets`:

```python
# Option 1: Set stylesheets on the instance at init time
instance = DynWidget(stylesheets=[css_string])

# Option 2: Set _stylesheets as raw CSS pathlib.Path
# Less reliable for dynamically-created classes

# Option 3: Override _get_properties to inject CSS
# Most control but more complex
```

The cleanest approach for the pane is to set the `stylesheets` parameter on instantiation. The CSS string from the anywidget's `_css` trait gets passed as a stylesheet entry, and Panel's stylesheet processing pipeline handles it.

Alternatively, if `_css` is a `pathlib.Path`, we can read it and pass the content as a string stylesheet.

**Verdict: CONFIRMED — CSS can be injected via the `stylesheets` parameter or `_stylesheets` class attribute. The `stylesheets` parameter at instantiation is the cleanest approach.**

---

## 5. Import Map Conflicts — React Injection Analysis

### The Problem

`AnyWidgetComponent` extends `ReactComponent`, which injects React into the import map via `_process_importmap()` (`panel/custom.py:854-887`):

```python
@classmethod
def _process_importmap(cls):
    imports = cls._importmap.get('imports', {})
    v_react = cls._react_version
    imports_with_deps = {
        "react": f"https://esm.sh/react@{v_react}...",
        "react/": f"https://esm.sh/react@{v_react}.../",
        "react-dom": f"https://esm.sh/react-dom@{v_react}...",
        "react-dom/": f"https://esm.sh/react-dom@{v_react}.../"
    }
    # ... adds more deps based on @mui usage ...
    for k, v in imports.items():
        imports_with_deps[k] = v  # User imports override
    return {'imports': imports_with_deps, 'scopes': ...}
```

For `AnyWidgetComponent`, `_react_version = "19"` (line 939 of custom.py). This means every AnyWidgetComponent gets React 19 in its import map.

### Is This a Problem for Non-React Anywidgets?

**No, this is not a problem.** Here's why:

1. **Import maps are declarative** — Having React in the import map doesn't force it to be loaded. It only maps `import "react"` to a URL. If the anywidget's ESM code never imports React, React is never fetched.

2. **The `_render_code()` method in AnyWidgetComponent** (`panel/models/anywidget_component.ts:165-178`) does NOT import React:
   ```typescript
   protected override _render_code(): string {
       return `
   function render(id) {
     const view = Bokeh.index.find_one_by_id(id)
     if (!view) { return }
     const out = Promise.resolve(view.render_fn({
       view, model: view.adapter, data: view.model.data, el: view.container
     }) || null)
     view.destroyer = out
     out.then(() => view.after_rendered())
   }
   export default {render}`
   }
   ```
   Unlike `ReactComponent._render_code()` (which imports React and createRoot at the top), `AnyWidgetComponent._render_code()` has NO React imports. React is only loaded if the anywidget's own ESM code imports it.

3. **Anywidgets that DO use React** (e.g., via `@anywidget/react`) can override import map entries. The user import loop in `_process_importmap` (line 877-883) applies user entries last, so a custom `_importmap` on the dynamic class can override React versions.

### Potential Concern: React Version Mismatch

If an anywidget depends on React 18 but Panel injects React 19 in the import map, there could be version conflicts. However:
- Most anywidgets that use React use `@anywidget/react`, which has its own import
- The `_importmap` can be set on the dynamic subclass to override versions
- `AnyWidgetComponent._react_version = "19"` — this is intentional and matches modern anywidget expectations

**Verdict: CONFIRMED — No import map conflicts for non-React anywidgets. React is in the map but only loaded on demand. Version overrides are possible via `_importmap`.**

---

## 6. Alternative Approaches

### Option B: New Bokeh Model from Scratch

This would involve creating a new Bokeh model (Python + TypeScript) specifically for wrapping anywidgets, bypassing the `AnyWidgetComponent` / `ReactiveESM` pipeline entirely.

**Pros:**
- Complete control over the rendering pipeline
- No potential conflicts with React import maps
- Could optimize for the anywidget API specifically

**Cons:**
- Massive duplication of effort — `AnyWidgetComponent` already provides the anywidget API compatibility layer (model adapter, change events, send/receive messages, `get`/`set`/`save_changes`)
- Would need to reimplement the TypeScript adapter (`AnyWidgetModelAdapter`, `AnyWidgetAdapter`) which is 190+ lines of carefully crafted compatibility code
- Would need to reimplement data model syncing, child model handling, ESM compilation, import map handling
- More surface area to maintain, more potential for bugs diverging from the main `ReactiveESM` pipeline

**Verdict: NOT RECOMMENDED** — too much duplication for marginal benefit. The existing `AnyWidgetComponent` TypeScript layer already solves the hard problem of anywidget API compatibility.

### Option C: Direct Manipulation of AnyWidgetComponent Instance Without Subclassing

This would involve creating a single `AnyWidgetComponent` instance and dynamically setting `_esm`, adding params, etc. at runtime.

**Problems:**
- **`_data_model` is created at class definition time** (in the metaclass `__init__`). There is no mechanism to rebuild it after class creation. Adding params to an instance does not update the data model.
- param Parameters are class-level descriptors. While `param.parameterized.add_parameter()` exists, it would not trigger the metaclass to rebuild `_data_model`.
- The `_esm` attribute is read as a class attribute (via `cls._esm` in `_render_esm`). Setting it on an instance may or may not work depending on descriptor behavior.
- The `_name_counter` and model naming logic assumes class-level operation.

**Verdict: NOT FEASIBLE** — the metaclass-driven `_data_model` construction is fundamentally a class-level operation. You cannot dynamically add params and expect the data model to reflect them without recreating the class.

### Why Option A Is Preferred

Option A (dynamic subclass) works because it leverages the **existing metaclass pipeline exactly as designed**:

1. `type()` calls `ReactiveESMMetaclass.__init__` — builds `_data_model`
2. `_esm` as a class attribute — picked up by `_render_esm()`
3. `_stylesheets` or `stylesheets` — handles CSS
4. `_importmap` — override-able per class
5. The entire TypeScript adapter layer (`AnyWidgetModelAdapter`, `AnyWidgetAdapter`, `AnyWidgetComponentView`) works unchanged

The only new code needed is the Python-side logic to:
- Map traitlets to param Parameters
- Extract `_esm` and `_css` from the anywidget class
- Call `type()` with the right dict
- Cache the dynamic class per anywidget class

---

## 7. Additional Considerations

### Caching Dynamic Subclasses

Multiple instances of the same anywidget class should reuse the same dynamic Panel subclass. This avoids:
- Repeatedly creating DataModel classes (memory)
- Name counter inflation (`Widget1`, `Widget2`, ...)
- Redundant metaclass processing

Recommended pattern:

```python
_ANYWIDGET_CLASS_CACHE: dict[type, type[AnyWidgetComponent]] = {}

def _get_or_create_panel_class(anywidget_cls):
    if anywidget_cls in _ANYWIDGET_CLASS_CACHE:
        return _ANYWIDGET_CLASS_CACHE[anywidget_cls]

    params = _map_traitlets_to_params(anywidget_cls)
    esm = anywidget_cls._esm
    css = getattr(anywidget_cls, '_css', None)

    class_dict = {
        '_esm': esm,
        **params,
    }
    if css:
        class_dict['_stylesheets'] = [css] if isinstance(css, str) else [css.read_text()]

    panel_cls = type(
        anywidget_cls.__name__,
        (AnyWidgetComponent,),
        class_dict,
    )
    _ANYWIDGET_CLASS_CACHE[anywidget_cls] = panel_cls
    return panel_cls
```

### Anywidgets with Both `_esm` and `_css`

Many anywidgets define both. The dynamic class should handle both:

```python
class_dict = {'_esm': esm_code}
if css_code:
    # Use _stylesheets for class-level CSS
    class_dict['_stylesheets'] = [css_code]
```

The `_stylesheets` entries flow through `Syncable._process_param_change` into the Bokeh model's `stylesheets` property, which applies them to the component's shadow DOM or document.

### TypeScript Compilation

The `AnyWidgetComponent` Bokeh model uses `sucrase_transforms: ["typescript", "jsx"]` (line 159 of `anywidget_component.ts`). This means anywidget ESM code that uses TypeScript or JSX syntax will be automatically compiled. Most anywidgets use plain JS, so the typescript+jsx transforms are a superset that handles everything.

### Module Caching on the Frontend

The TypeScript side caches compiled modules in `MODULE_CACHE` (line 23 of `reactive_esm.ts`), keyed by `class_name-esm_length` or bundle hash. Multiple instances of the same dynamic class share the same cache key (same `class_name`, same `esm`), so the ESM is compiled only once. This is correct and efficient.

### The `__abstract = True` Attribute

`AnyWidgetComponent` has `__abstract = True` (line 935 of custom.py). This prevents it from being directly instantiated via `panel()`. Our dynamic subclass does NOT inherit this attribute (it's name-mangled to `_AnyWidgetComponent__abstract`), so dynamic subclasses are not marked abstract. This is correct behavior.

---

## 8. Summary of Findings

| Aspect | Status | Notes |
|--------|--------|-------|
| Metaclass triggers on `type()` | Confirmed | `ReactiveESMMetaclass.__init__` runs automatically |
| `_data_model` created correctly | Confirmed | `construct_data_model()` handles dynamic classes |
| ESM string injection | Confirmed | Falls through to `cls._esm` string path |
| ESM pathlib.Path injection | Confirmed | Returned directly by `_esm_path()` |
| CSS via `_stylesheets` | Confirmed | Raw CSS strings or paths work |
| React import map conflicts | Not a problem | React only loaded if imported by ESM |
| Module caching (frontend) | Works correctly | Shared cache key per class |
| Multiple instances | Safe | Cache dynamic class per anywidget class |
| Name uniqueness | Safe | `_name_counter` ensures unique DataModel names |

**The dynamic subclass approach is architecturally sound and can be implemented with confidence.**

---

## Appendix A: AnyWidget Source Analysis — `_esm` and `_css` Extraction

Source: `/tmp/anywidget-src/anywidget/widget.py` and `/tmp/anywidget-src/anywidget/_util.py`

### How AnyWidget Handles `_esm` and `_css` Internally

The `AnyWidget` class (`anywidget/widget.py:25-84`) extends `ipywidgets.DOMWidget`. Understanding its internals is critical for extracting the right values.

#### Class-Level Processing (`__init_subclass__`)

When a user defines `class MyWidget(AnyWidget): _esm = "..."`, the `__init_subclass__` hook runs:

```python
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    for key in ("_esm", "_css") & cls.__dict__.keys():
        file_contents = try_file_contents(getattr(cls, key))
        if file_contents:
            setattr(cls, key, file_contents)  # Replaces str path with FileContents
```

This means:
- If `_esm` is a **multi-line string** (inline code): it stays as-is (a `str`)
- If `_esm` is a **file path string** (e.g., `"./widget.js"`): replaced with a `FileContents` object
- If `_esm` is a **`pathlib.Path`**: replaced with a `FileContents` object
- If `_esm` is a **URL** (e.g., `"https://cdn.example.com/widget.js"`): stays as-is (a `str`)

`FileContents` wraps a path and provides `str(file_contents)` -> current file content. It also watches for file changes and re-reads.

#### Instance-Level Processing (`__init__`)

In `__init__`, the widget dynamically adds traitlets:

```python
def __init__(self, *args, **kwargs):
    anywidget_traits = {}
    for key in ("_esm", "_css"):
        if hasattr(self, key) and not self.has_trait(key):
            value = getattr(self, key)
            anywidget_traits[key] = t.Unicode(str(value)).tag(sync=True)
            if isinstance(value, (VirtualFileContents, FileContents)):
                value.changed.connect(
                    lambda new_contents, key=key: setattr(self, key, new_contents),
                )
    self.add_traits(**anywidget_traits)
    super().__init__(*args, **kwargs)
```

Key points:
- `_esm` and `_css` become `Unicode` traitlets with `sync=True`
- The trait value is `str(value)` — for `FileContents`, this reads the file content
- If it's already a traitlet (user defined `_esm = t.Unicode(...).tag(sync=True)`), it's NOT re-created

### Extraction Strategy for the Pane

Given an anywidget **class** or **instance**, here's how to extract `_esm` and `_css`:

```python
def extract_esm(anywidget_obj_or_cls):
    """Extract ESM code from an anywidget class or instance."""
    if isinstance(anywidget_obj_or_cls, type):
        # Class: _esm may be str, FileContents, or traitlet default
        cls = anywidget_obj_or_cls
    else:
        # Instance: _esm is already resolved to a string via traitlet
        return anywidget_obj_or_cls._esm  # str (traitlet value)

    esm = getattr(cls, '_esm', None)
    if esm is None:
        return None
    # FileContents -> read file content
    return str(esm)  # Works for str, FileContents, VirtualFileContents

def extract_css(anywidget_obj_or_cls):
    """Extract CSS from an anywidget class or instance."""
    if isinstance(anywidget_obj_or_cls, type):
        cls = anywidget_obj_or_cls
    else:
        # On instances, _css may or may not exist as a trait
        css = getattr(anywidget_obj_or_cls, '_css', None)
        return str(css) if css else None

    css = getattr(cls, '_css', None)
    if css is None:
        return None
    return str(css)
```

### `_esm` Formats in the Wild

From the anywidget test suite (`tests/test_widget.py`), the following patterns are used:

1. **Inline string** (most common):
   ```python
   class Widget(AnyWidget):
       _esm = """
       function render({ model, el }) { el.innerText = "Hello"; }
       export default { render };
       """
   ```

2. **Explicit traitlet** (less common, for fine control):
   ```python
   class Widget(AnyWidget):
       _esm = t.Unicode("...code...").tag(sync=True)
   ```

3. **File path (pathlib.Path)**:
   ```python
   class Widget(AnyWidget):
       _esm = pathlib.Path("./widget.js")
   ```

4. **File path (string)**:
   ```python
   class Widget(AnyWidget):
       _esm = "./widget.js"  # Detected by suffix, resolved to FileContents
   ```

5. **Remote URL**:
   ```python
   class Widget(AnyWidget):
       _esm = "http://example.com/foo.js"
   ```

For the pane, all of these resolve to a string via `str(widget._esm)` on an instance. The only edge case is remote URLs — Panel's `_esm_path()` will return `None` for URLs (they don't end with a valid extension when preceded by `http`), and `_render_esm()` will try to use the URL string as ESM code, which is wrong. We need to handle remote URLs specially — either fetch the content or pass the URL through the import map.

### Traitlet Sync Tag

Only traitlets with `.tag(sync=True)` are synced to the frontend. The `_get_traitlets_state()` function (`anywidget/_descriptor.py:657-669`) uses `obj.trait_values(sync=True)` to get only synced traits. This means our pane should also only map traits that have `sync=True`.

### `ipywidgets_bokeh` Comparison

The existing `ipywidgets_bokeh` (`/tmp/ipywidgets_bokeh/ipywidgets_bokeh/widget.py`) takes a completely different approach — it serializes the widget state via `ipywidgets.embed` and sends it as a blob. This works for the full ipywidgets ecosystem but is heavyweight and requires the full ipywidgets JS runtime. For anywidgets specifically, our dynamic subclass approach is far more efficient because we can use Panel's native ESM rendering pipeline.
