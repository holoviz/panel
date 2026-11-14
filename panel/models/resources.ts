/**
 * Client-side registry for external component resources.
 *
 * Both the eager path (`pn.extension`, which renders its script and link
 * tags into the page and then calls `declare`) and the lazy path (a model
 * carrying an `external_resources` spec, which calls `ensure`) write to one
 * registry, so a library is fetched at most once per page no matter how
 * many components, documents or Panel versions ask for it.
 *
 * The registry is installed on `globalThis.__panel_resources__`, outside any
 * version-namespaced object, so two Panel versions sharing a JupyterLab page
 * share it as well. Its shape is therefore a cross-version contract: it
 * carries a `v` field and must stay minimal and backwards compatible.
 */

import {ImportedStyleSheet} from "@bokehjs/models/dom/stylesheets"
import * as dom from "@bokehjs/core/dom"

export const REGISTRY_VERSION = 1

export const DEFAULT_TIMEOUT = 15000

export type Probe = {global?: string, custom_element?: string}

export type ModuleSpec = {url: string, export?: string}

export type LibSpec = {
  name: string
  js?: string[]
  modules?: ModuleSpec[]
  probe?: Probe
}

export type ResourceSpec = {
  v: number
  libs?: LibSpec[]
  css?: string[]
  shim?: string
  timeout?: number
  inline_fallback?: boolean
}

function url_key(url: string): string {
  try {
    return new URL(resource_url(url), document.baseURI).href
  } catch (e) {
    return url
  }
}

/**
 * Absolutizes a module url.
 *
 * `importShim` resolves anything that does not start with a scheme, `/`,
 * `./` or `../` through the import map, so the relative urls Panel emits
 * in `server` mode (`static/extensions/panel/bundled/...`) fail as
 * unknown packages. Every url that reaches here comes from a resource
 * spec or from a blob, never from an import map, so resolving it against
 * the document is safe.
 */
function module_url(url: string): string {
  url = resource_url(url)
  return /^[a-z][a-z0-9+.-]*:/i.test(url) ? url : url_key(url)
}

function existing_urls(selector: string, attr: "src" | "href"): Set<string> {
  const urls = new Set<string>()
  for (const el of document.querySelectorAll(selector)) {
    const url = el.getAttribute(attr)
    if (url != null && url !== "") {
      urls.add(url_key(url))
    }
  }
  return urls
}

const JUPYTER_ENDPOINT = "/panel-preview/"

/**
 * Maps a Jupyter extension endpoint url to its CDN equivalent, using the
 * map of endpoint paths to CDN urls the notebook bootstrap publishes
 * (Panel's dist, every extension with a CDN and each BokehJS file). Null
 * if the url is not served by the endpoint or has no CDN equivalent, e.g.
 * in server/served-app contexts, where the bootstrap never runs.
 */
export function cdn_url(url: string): string | null {
  const global = globalThis as any
  let cdn_map: [string, string][] | null = global.__panel_cdn_map__ ?? null
  if (cdn_map == null && typeof global.__panel_cdn_dist__ === "string") {
    cdn_map = [["static/extensions/panel/", global.__panel_cdn_dist__]]
  }
  const index = url.indexOf(JUPYTER_ENDPOINT)
  if (cdn_map == null || index === -1) {
    return null
  }
  const path = url.slice(index + JUPYTER_ENDPOINT.length)
  for (const [prefix, cdn] of cdn_map) {
    if (path.startsWith(prefix)) {
      return cdn + path.slice(prefix.length)
    }
  }
  return null
}

/**
 * Loads endpoint urls from the CDN where the endpoint cannot serve them:
 * in an exported notebook, or once the bootstrap found the endpoint
 * unreachable.
 */
export function resource_url(url: string): string {
  const global = globalThis as any
  if (global.__panel_live_notebook__ === false || global.__panel_endpoint_failed__ === true) {
    return cdn_url(url) ?? url
  }
  return url
}

/**
 * Rewrites a failed Jupyter-extension-endpoint url to its CDN equivalent,
 * mirroring the eager bootstrap's fallback in autoload_panel_js.js. Only
 * tried once per element.
 */
function fallback_to_cdn(el: HTMLScriptElement | HTMLLinkElement, url: string): string | null {
  const fallback = cdn_url(url)
  if (fallback == null || el.dataset.panelCdnFallback != null) {
    return null
  }
  el.dataset.panelCdnFallback = ""
  return fallback
}

function is_endpoint_url(url: string): boolean {
  return url.includes(`${JUPYTER_ENDPOINT}static/`)
}

function inject(el: HTMLScriptElement | HTMLLinkElement): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    const attempt = (element: HTMLScriptElement | HTMLLinkElement) => {
      element.addEventListener("load", () => resolve(), {once: true})
      element.addEventListener("error", () => {
        const url = (element as HTMLScriptElement).src || (element as HTMLLinkElement).href
        const fallback = fallback_to_cdn(element, url)
        if (fallback != null) {
          element.remove()
          if (element instanceof HTMLLinkElement) {
            element.href = fallback
          } else {
            element.src = fallback
          }
          attempt(element)
          document.head.appendChild(element)
          return
        }
        if (is_endpoint_url(url)) {
          const global = globalThis as any
          global.__panel_jupyter_extension_error__?.()
        }
        reject(new Error(`Failed to load ${url}`))
      }, {once: true})
    }
    attempt(el)
    document.head.appendChild(el)
  })
}

/**
 * Hides RequireJS from the scripts the registry loads while they execute.
 *
 * On a page with RequireJS (the classic notebook, VS Code) a UMD bundle
 * finds `define.amd` and registers an anonymous AMD module instead of
 * assigning the global the components read, and RequireJS attributes that
 * anonymous define() to whichever script it loads next. Hiding `define`
 * itself for as long as the scripts load would also hide it from whatever
 * RequireJS loads in the meantime, so instead `define.amd` reads as
 * undefined only while Panel's own code is running: a classic script is
 * recognized by a marker attribute, a module script, which has no
 * `document.currentScript`, by the directory it was loaded from.
 */
const NO_AMD_ATTR = "data-panel-no-amd"

function install_amd_guard(): void {
  const global = globalThis as any
  const define = global.define
  if (typeof define !== "function" || define.amd == null || define.__panel_no_amd__ === true) {
    return
  }
  const dirs: string[] = global.__panel_no_amd_dirs__ ??= []
  const hidden = (): boolean => {
    const script = document.currentScript
    if (script != null) {
      return script.hasAttribute(NO_AMD_ATTR)
    }
    const stack = new Error().stack ?? ""
    return dirs.some((dir) => stack.includes(dir))
  }
  let amd = define.amd
  try {
    Object.defineProperty(define, "amd", {
      configurable: true,
      enumerable: true,
      get: () => hidden() ? undefined : amd,
      set: (value) => { amd = value },
    })
    Object.defineProperty(define, "__panel_no_amd__", {value: true})
  } catch (e) {
    console.warn(`Panel: could not hide RequireJS from component libraries: ${e}`)
  }
}

function hide_amd(el: HTMLScriptElement): void {
  el.setAttribute(NO_AMD_ATTR, "")
  install_amd_guard()
}

function hide_amd_module(url: string): void {
  const dirs: string[] = (globalThis as any).__panel_no_amd_dirs__ ??= []
  const dir = url_key(url).split("?")[0].replace(/[^/]*$/, "")
  // panel.js itself lives in a dist root, and must never match.
  if (!/\/(dist|static\/extensions\/panel)\/$/.test(dir) && !dirs.includes(dir)) {
    dirs.push(dir)
  }
  install_amd_guard()
}

/**
 * Injects a classic script tag.
 *
 * `async = false` on a dynamically inserted script keeps execution in
 * insertion order while still fetching in parallel, which is what the
 * eager path relies on for order-significant libraries (echarts before
 * echarts-gl, vega before vega-lite before vega-embed, ...).
 */
function inject_script(url: string): Promise<void> {
  const el = document.createElement("script")
  el.async = false
  el.src = resource_url(url)
  hide_amd(el)
  return inject(el)
}

/**
 * Injects a native module script, optionally exposing its export as a global.
 *
 * Deliberately native rather than `importShim`: es-module-shims runs in
 * shim mode, where it fetches module sources and re-serves them as blobs,
 * and a library that resolves a sibling asset against `import.meta.url`
 * (perspective and its wasm, for one) cannot survive that. The eager path
 * emitted plain `<script type="module">` tags for the same reason, so this
 * keeps both paths on the same loader. `async = false` keeps execution in
 * insertion order.
 *
 * The wrapper for an export is served from a blob, which only moves the
 * *wrapper's* `import.meta.url`; the imported module keeps its own. The url
 * has to be absolute for that reason: resolving Panel's relative
 * `server` mode urls against a `blob:` base does not reach the server.
 */
function inject_module(url: string, name?: string): Promise<void> {
  const el = document.createElement("script")
  el.type = "module"
  el.async = false
  hide_amd_module(url)
  if (name == null) {
    el.src = resource_url(url)
    return inject(el)
  }
  url = module_url(url)
  const code = `import * as ns from ${JSON.stringify(url)}\nglobalThis[${JSON.stringify(name)}] = ns.default ?? ns\n`
  el.src = URL.createObjectURL(new Blob([code], {type: "text/javascript"}))
  return inject(el).finally(() => URL.revokeObjectURL(el.src))
}

function inject_link(url: string): Promise<void> {
  const el = document.createElement("link")
  el.rel = "stylesheet"
  el.type = "text/css"
  el.href = resource_url(url)
  return inject(el)
}

/**
 * Resolves once the web component a library ships actually exists.
 *
 * Neither a script tag on the page nor a `declare` from the eager path
 * means the library is done: one that ships web components may register
 * them well after its own script has executed (perspective-viewer defines
 * itself once its wasm resolves, and perspective's client refuses to start
 * a worker before then). Where a probe names an element, that element is
 * the completion signal.
 */
function element_defined(lib: LibSpec): Promise<void> {
  const name = lib.probe?.custom_element
  if (name == null || customElements.get(name) != null) {
    return Promise.resolve()
  }
  return customElements.whenDefined(name).then(() => undefined)
}

function with_timeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  if (!(ms > 0)) {
    return promise
  }
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => reject(
      new Error(`Timed out after ${ms}ms waiting for external resources`),
    ), ms)
    promise.then(
      (value) => { clearTimeout(timer); resolve(value) },
      (error) => { clearTimeout(timer); reject(error) },
    )
  })
}

export class ResourceRegistry {
  readonly v: number = REGISTRY_VERSION

  /** lib name -> promise resolving once the library is usable */
  readonly libs: Map<string, Promise<void>> = new Map()
  /** absolute url -> promise resolving once the url has loaded */
  readonly urls: Map<string, Promise<void>> = new Map()
  /** module url -> promise resolving to the module namespace */
  readonly modules: Map<string, Promise<any>> = new Map()
  /** lib name -> last seen spec, for `libs` entries given by name only */
  readonly specs: Map<string, LibSpec> = new Map()
  /** export name -> resolved module handle */
  readonly exports: Map<string, any> = new Map()

  protected _shim: Promise<void> | null = null

  /**
   * Records resources that are already on the page, without fetching.
   *
   * Called by the eager path so that "pn.extension already handled it"
   * is a fact rather than an inference. It is the only thing that can
   * get this right for `inline` resources, where the libraries were
   * inlined and there are no urls to compare against.
   */
  declare(declared: LibSpec[] | {libs?: LibSpec[], css?: string[]}): void {
    const {libs, css} = Array.isArray(declared) ? {libs: declared, css: []} : declared
    for (const lib of libs ?? []) {
      if (lib == null || lib.name == null) {
        continue
      }
      this.specs.set(lib.name, lib)
      this.libs.set(lib.name, element_defined(lib))
      for (const url of lib.js ?? []) {
        this.urls.set(url_key(url), Promise.resolve())
      }
      for (const {url} of lib.modules ?? []) {
        this.urls.set(url_key(url), Promise.resolve())
      }
    }
    for (const url of css ?? []) {
      this.urls.set(url_key(url), Promise.resolve())
    }
  }

  /**
   * Records that a loader outside the registry (RequireJS, in the classic
   * notebook) is already fetching these libraries. Unlike `declare`, this
   * does not mark them ready immediately: `await_resources` waits on
   * `ready` instead, so a view doesn't read an unassigned global.
   */
  claim(declared: {libs?: LibSpec[]}, ready: Promise<void>): void {
    for (const lib of declared.libs ?? []) {
      if (lib == null || lib.name == null) {
        continue
      }
      this.specs.set(lib.name, lib)
      this.libs.set(lib.name, ready.then(() => {
        if (this.loaded(lib)) {
          return element_defined(lib)
        }
        // The other loader failed or gave up, so load what is missing here.
        const urls = [...(lib.js ?? []), ...(lib.modules ?? []).map((module) => module.url)]
        for (const url of urls) {
          if (this.urls.get(url_key(url)) === ready) {
            this.urls.delete(url_key(url))
          }
        }
        const elements = lib.probe?.custom_element != null ? [lib.probe.custom_element] : []
        return this._load(lib.js ?? [], lib.modules ?? [], elements)
      }))
      for (const url of lib.js ?? []) {
        this.urls.set(url_key(url), ready)
      }
      for (const {url} of lib.modules ?? []) {
        this.urls.set(url_key(url), ready)
      }
    }
  }

  /**
   * Whether a library is already available without loading anything.
   *
   * Probes are hints derived from `__js_skip__` and are known to be wrong
   * in places, which is tolerable: the url checks below are what make
   * this correct, a wrong probe only costs a redundant script tag for an
   * already cached file.
   */
  loaded(lib: LibSpec, scripts?: Set<string>): boolean {
    // The modules of a library are loaded separately, e.g. by the notebook,
    // so its probe can pass before every module assigned its global.
    const exported = (lib.modules ?? []).every(
      ({export: name}) => name == null || (globalThis as any)[name] != null,
    )
    if (!exported) {
      return false
    }
    const {probe} = lib
    if (probe != null) {
      if (probe.global != null) {
        // A `<div id="deck">` puts an element on `window.deck`, so an
        // HTMLElement is not evidence that the library loaded.
        const value = (globalThis as any)[probe.global]
        if (value != null && !(value instanceof HTMLElement)) {
          return true
        }
      }
      if (probe.custom_element != null && customElements.get(probe.custom_element) != null) {
        return true
      }
    }
    const urls = [...(lib.js ?? []), ...(lib.modules ?? []).map((m) => m.url)]
    if (urls.length === 0) {
      return true
    }
    return urls.every((url) => {
      const key = url_key(url)
      return this.urls.has(key) || (scripts != null && scripts.has(key))
    })
  }

  /**
   * Loads everything a resource spec declares, skipping what is present.
   */
  async ensure(spec: ResourceSpec | null | undefined): Promise<void> {
    if (spec == null) {
      return
    }
    const scripts = existing_urls("script[src]", "src")
    const waits: Promise<unknown>[] = []
    const js: string[] = []
    const modules: ModuleSpec[] = []
    const claimed: string[] = []
    const elements: string[] = []
    for (let lib of spec.libs ?? []) {
      if (typeof lib === "string") {
        const known = this.specs.get(lib)
        if (known == null) {
          continue
        }
        lib = known
      }
      if (!this.specs.has(lib.name)) {
        this.specs.set(lib.name, lib)
      }
      const pending = this.libs.get(lib.name)
      if (pending != null) {
        waits.push(pending)
        continue
      }
      if (this.loaded(lib, scripts)) {
        const ready = element_defined(lib)
        this.libs.set(lib.name, ready)
        waits.push(ready)
        continue
      }
      claimed.push(lib.name)
      js.push(...(lib.js ?? []))
      modules.push(...(lib.modules ?? []))
      if (lib.probe?.custom_element != null) {
        elements.push(lib.probe.custom_element)
      }
    }

    if (spec.css != null && spec.css.length > 0) {
      waits.push(this.ensure_css(spec.css))
    }
    if (js.length > 0 || modules.length > 0) {
      const loading = this._load(js, modules, elements)
      for (const name of claimed) {
        this.libs.set(name, loading)
      }
      loading.catch(() => {
        // Drop the entry so a later view can retry.
        for (const name of claimed) {
          if (this.libs.get(name) === loading) {
            this.libs.delete(name)
          }
        }
      })
      waits.push(loading)
    }
    await Promise.all(waits)
  }

  /**
   * Injects stylesheets, matching what pn.extension puts in the head.
   *
   * A stylesheet that never arrives must not keep a component from
   * rendering, so failures are reported and then ignored.
   */
  ensure_css(urls: string[]): Promise<void> {
    const links = existing_urls("link[rel~='stylesheet']", "href")
    const promises = urls.map((url) => {
      const key = url_key(url)
      let promise = this.urls.get(key)
      if (promise == null) {
        promise = links.has(key) ? Promise.resolve() : inject_link(url)
        this.urls.set(key, promise)
      }
      return promise.catch((error: Error) => {
        this.urls.delete(key)
        console.warn(`Panel: could not load stylesheet ${url}: ${error.message}`)
      })
    })
    return Promise.all(promises).then(() => undefined)
  }

  /**
   * Ensures es-module-shims is available, in shim mode.
   *
   * Shim mode cannot be enabled after es-module-shims has loaded, so the
   * options marker has to be written before the script is injected. Shim
   * mode is what makes `importShim.addImportMap` available, which the ESM
   * component machinery depends on.
   */
  ensure_shim(url?: string): Promise<void> {
    if (typeof (globalThis as any).importShim === "function") {
      return Promise.resolve()
    }
    if (this._shim != null) {
      return this._shim
    }
    if (url == null) {
      return Promise.reject(new Error("No es-module-shims url available"))
    }
    if (document.querySelector("script[type='esms-options']") == null) {
      const options = document.createElement("script")
      options.type = "esms-options"
      options.textContent = JSON.stringify({shimMode: true})
      document.head.appendChild(options)
    }
    const key = url_key(url)
    const scripts = existing_urls("script[src]", "src")
    const promise = scripts.has(key) ? Promise.resolve() : inject_script(url)
    this.urls.set(key, promise)
    this._shim = promise.catch((e) => {
      this._shim = null
      throw e
    })
    return this._shim
  }

  /**
   * Imports an ES module through es-module-shims, memoized by url.
   */
  import_module(url: string, shim?: string): Promise<any> {
    url = module_url(url)
    if (url.startsWith("blob:")) {
      // Blob urls are single use, so memoizing them only grows the map.
      return this.ensure_shim(shim).then(() => (globalThis as any).importShim(url))
    }
    let module = this.modules.get(url)
    if (module == null) {
      const fallback = cdn_url(url)
      module = this.ensure_shim(shim).then(() => (globalThis as any).importShim(url))
      if (fallback != null && fallback !== url) {
        module = module.catch(() => (globalThis as any).importShim(fallback))
      }
      this.modules.set(url, module)
      module.catch(() => this.modules.delete(url))
    }
    return module
  }

  add_import_map(map: any): void {
    try {
      (globalThis as any).importShim.addImportMap({...map})
    } catch (e) {
      console.warn(`Failed to add import map: ${e}`)
    }
  }

  protected async _load(js: string[], modules: ModuleSpec[], elements: string[] = []): Promise<void> {
    if (js.length > 0) {
      await this._load_scripts(js)
    }
    if (modules.length > 0) {
      await this._load_modules(modules)
    }
    if (elements.length > 0) {
      // A library that ships web components may register them after its
      // module has finished executing (perspective-viewer defines itself
      // once its own wasm resolves), and a component that renders before
      // then gets an inert element. The load is only complete once the
      // element the probe names actually exists.
      await Promise.all(elements.map((name) => customElements.whenDefined(name)))
    }
  }

  protected _load_scripts(urls: string[]): Promise<void> {
    const scripts = existing_urls("script[src]", "src")
    const promises = urls.map((url) => {
      const key = url_key(url)
      let promise = this.urls.get(key)
      if (promise == null) {
        promise = scripts.has(key) ? Promise.resolve() : inject_script(url)
        this.urls.set(key, promise)
        promise.catch(() => this.urls.delete(key))
      }
      return promise
    })
    return Promise.all(promises).then(() => undefined)
  }

  protected _load_modules(modules: ModuleSpec[]): Promise<void> {
    const scripts = existing_urls("script[src]", "src")
    const promises = modules.map(({url, export: name}) => {
      const key = url_key(url)
      let promise = this.urls.get(key)
      if (promise == null) {
        promise = scripts.has(key) ? Promise.resolve() : inject_module(url, name)
        this.urls.set(key, promise)
        promise.catch(() => this.urls.delete(key))
      }
      return promise
    })
    return Promise.all(promises).then(() => {
      // The wrapper assigned the global, matching the module shims
      // js_resources.html renders, which components read as
      // `(window as any).<name>`.
      for (const {export: name} of modules) {
        if (name != null && this.exports.get(name) == null) {
          const handle = (globalThis as any)[name]
          if (handle != null) {
            this.exports.set(name, handle)
          }
        }
      }
    })
  }
}

function install(): ResourceRegistry {
  const global = globalThis as any
  const existing = global.__panel_resources__
  let registry: ResourceRegistry
  if (existing != null &&
      typeof existing.ensure === "function" &&
      typeof existing.declare === "function") {
    registry = existing as ResourceRegistry
  } else {
    registry = new ResourceRegistry()
    global.__panel_resources__ = registry
  }
  // The templates emit their declare() call inline, which may run before
  // panel.js itself has executed, in which case it queues here instead.
  const queued = global.__panel_resources_declared__
  if (Array.isArray(queued)) {
    global.__panel_resources_declared__ = []
    for (const declared of queued) {
      // A queued entry carrying `ready` is a claim: some other loader, i.e.
      // the notebook's RequireJS, is fetching those libraries already.
      const ready = declared?.ready
      if (ready != null && typeof ready.then === "function") {
        registry.claim(declared, ready)
      } else {
        registry.declare(declared)
      }
    }
  }
  return registry
}

export const resources: ResourceRegistry = install()

export interface ExternalResourcesModel {
  external_resources: ResourceSpec | null
}

/**
 * Bokeh property declaration for models that carry a resource spec.
 *
 * The resource bearing models do not share a single base (`HTMLBox`
 * covers most of them, but `KaTeX` derives from `Markup`, `FileDropper`
 * from `InputWidget` and so on) and TypeScript has no multiple
 * inheritance, so the declaration is applied per class instead.
 */
export function define_external_resources(cls: any): void {
  cls.define(({Any, Nullable}: any) => ({
    external_resources: [Nullable(Any), null],
  }))
}

const _pending = new WeakMap<object, Promise<Error | null>>()

/**
 * Starts loading a model's resources.
 *
 * Called from the model's `initialize`, which runs for every model in a
 * document before the first view is built. `build_views` constructs views
 * sequentially, so starting here is what keeps the total wait at roughly
 * the slowest library rather than the sum of all of them.
 */
export function load_resources(model: ExternalResourcesModel): void {
  const spec = model.external_resources
  if (spec == null || _pending.has(model)) {
    return
  }
  const timeout = spec.timeout ?? DEFAULT_TIMEOUT
  _pending.set(model, with_timeout(resources.ensure(spec), timeout).then(
    () => null,
    (error: Error) => {
      console.error(`Panel: could not load external resources: ${error.message}`)
      return error
    },
  ))
}

/**
 * Awaits a model's resources, resolving to the error if loading failed.
 *
 * Never rejects: an exception out of `lazy_initialize` aborts the whole
 * `build_views` walk and would take unrelated components down with it.
 */
export function await_resources(model: ExternalResourcesModel): Promise<Error | null> {
  load_resources(model)
  return _pending.get(model) ?? Promise.resolve(null)
}

/**
 * Element rendered in place of a component whose resources never arrived.
 */
function resource_error_el(error: Error): HTMLElement {
  const el = document.createElement("div")
  el.className = "pn-resource-error"
  el.style.cssText = "color: red; font-family: monospace; white-space: pre-wrap; padding: 0.5em;"
  el.textContent = `Could not load the resources this component requires:\n${error.message}`
  return el
}

/**
 * Replaces a view's rendering with an error state.
 *
 * `base` (the view baseclass' own render) still runs, so the element keeps
 * its sizing and stylesheets, but the subclass render is skipped entirely.
 * That is the point: its code reads globals the library that failed to load
 * never defined, and letting it throw out of `render` takes the surrounding
 * layout down with it. Installing the override on the instance is what makes
 * it win over the subclass method on the prototype chain.
 */
export function render_resource_error(view: any, error: Error, base: () => void): void {
  view.render = () => {
    base.call(view)
    view.shadow_el.appendChild(resource_error_el(error))
  }
}

// Component stylesheets are Bokeh models whose urls never pass through the
// registry, so exported notebooks have to rewrite them where Bokeh turns
// them into a stylesheet.
const underlying = ImportedStyleSheet.prototype.underlying
ImportedStyleSheet.prototype.underlying = function(this: ImportedStyleSheet): dom.StyleSheet {
  const url = resource_url(this.url)
  return url === this.url ? underlying.call(this) : new dom.ImportedStyleSheet(url)
}
