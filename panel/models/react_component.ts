import type {BuildResult, Options, ViewStorage} from "@bokehjs/core/build_views"
import {build_views} from "@bokehjs/core/build_views"
import type {HasProps} from "@bokehjs/core/has_props"
import type {ViewOf} from "@bokehjs/core/view"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import type {DOMView} from "@bokehjs/core/dom_view"
import {ClassList, InlineStyleSheet, ImportedStyleSheet} from "@bokehjs/core/dom"
import type {CSSStyles, CSSStyleSheetDecl} from "@bokehjs/core/css"
import type * as p from "@bokehjs/core/properties"
import {difference} from "@bokehjs/core/util/array"
import {assert} from "@bokehjs/core/util/assert"
import {isArray, isString} from "@bokehjs/core/util/types"
import type {UIElementView} from "@bokehjs/models/ui/ui_element"
import type {Transform} from "sucrase"

import {
  ReactiveESM, ReactiveESMView, model_getter, model_setter,
} from "./reactive_esm"

export class HostedStyleSheet extends InlineStyleSheet {
  host_id: string

  constructor(css?: string | CSSStyleSheetDecl, id?: string, override readonly persistent: boolean = false, host_id: string = "") {
    super(css, id, persistent)
    this.host_id = host_id
  }

  override replace(css: string, styles?: CSSStyles): void {
    css = css.replace(/:host\b/g, `#${this.host_id}`)
    super.replace(css, styles)
  }

  override prepend(css: string, styles?: CSSStyles): void {
    css = css.replace(/:host\b/g, `#${this.host_id}`)
    super.prepend(css, styles)
  }

  override append(css: string, styles?: CSSStyles): void {
    css = css.replace(/:host\b/g, `#${this.host_id}`)
    super.append(css, styles)
  }

}

async function _build_view<T extends HasProps>(view_cls: T["default_view"], model: T, options: Options<ViewOf<T>>): Promise<ViewOf<T>> {
  assert(view_cls != null, "model doesn't implement a view")
  const view = new view_cls({...options, model})
  view.initialize()
  await view.lazy_initialize()
  return view
}

// Custom build_views implementation which does not eagerly destroy old views
async function build_views_no_remove<T extends HasProps>(
  view_storage: ViewStorage<T>,
  models: T[],
  options: Options<ViewOf<T>> = {parent: null},
  cls: (model: T) => T["default_view"] = (model) => model.default_view,
): Promise<BuildResult<T>> {

  const to_remove = difference([...view_storage.keys()], models)

  const removed_views: ViewOf<T>[] = []
  for (const model of to_remove) {
    const view = view_storage.get(model)
    if (view != null) {
      view_storage.delete(model)
      removed_views.push(view)
    }
  }

  const created_views: ViewOf<T>[] = []
  const new_models = models.filter((model) => !view_storage.has(model))

  for (const model of new_models) {
    const view = await _build_view(cls(model), model, options)
    view_storage.set(model, view)
    created_views.push(view)
  }

  for (const view of created_views) {
    view.connect_signals()
  }

  return {
    created: created_views,
    removed: removed_views,
  }
}

export class ReactComponentView extends ReactiveESMView {
  declare model: ReactComponent
  declare style_cache: HTMLHeadElement
  model_getter = model_getter
  model_setter = model_setter
  react_root: any = null
  mounted: boolean = false

  _force_update_callbacks: (() => void)[] = []
  _mounted_resolve: (() => void) | null = null
  _scheduled_removals: DOMView[] = []
  _dom_sentinel: HTMLStyleElement | null = null

  override initialize(): void {
    super.initialize()
    if (!this.use_shadow_dom) {
      (this as any).display = new HostedStyleSheet("", "display", false, this.model.id);
      (this as any).style = new HostedStyleSheet("", "style", false, this.model.id);
      (this as any).parent_style = new HostedStyleSheet("", "parent", true, this.model.id)
    }
  }

  get use_shadow_dom(): boolean {
    return this.model.use_shadow_dom || !(this.parent instanceof ReactComponentView)
  }

  override render_esm(): void {
    if (this.model.compiled === null || this.model.render_module === null || this.container == null) {
      return
    }
    this._rendered = false
    if (this.model.usesMui) {
      if (this.model.root_node) {
        this.style_cache = document.head
      } else {
        this.style_cache = document.createElement("head")
        this.shadow_el.insertBefore(this.style_cache, this.container)
      }
    }
    this.accessed_properties = []
    for (const lf of this._lifecycle_handlers.keys()) {
      (this._lifecycle_handlers.get(lf) || []).splice(0)
    }
    this.model.disconnect_watchers(this)
    const mounted_promise = new Promise<void>((resolve) => {
      this._mounted_resolve = resolve
    })
    this.model.render_module.then((mod: any) => {
      if (this.container == null) {
        // Nothing will mount, so the ready promise has to be settled here or
        // the view never finishes and the document never goes idle.
        this._resolve_mounted()
        return
      }
      this.react_root = Promise.resolve(mod.default.render(this))
    }).catch((e: unknown) => {
      this._resolve_mounted()
      throw e
    })
    this._await_ready(mounted_promise)
  }

  override render_error(error: SyntaxError): void {
    // A component that errored will never mount and so never settles its
    // promise via `after_rendered`.
    this._resolve_mounted()
    super.render_error(error)
  }

  /**
   * Settles the promise handed to `_await_ready` by `render_esm`. Safe to call
   * more than once; only the first call has an effect.
   */
  _resolve_mounted(): void {
    const resolve = this._mounted_resolve
    if (resolve == null) {
      return
    }
    this._mounted_resolve = null
    resolve()
  }

  on_force_update(cb: () => void): void {
    this._force_update_callbacks.push(cb)
  }

  force_update(): void {
    for (const cb of this._force_update_callbacks) {
      cb()
    }
  }

  override remove(): void {
    this._force_update_callbacks = []
    this.mounted = false
    // A view removed before it mounted still owes a resolution to the promise
    // handed to `_await_ready`, otherwise the root never reaches idle.
    this._resolve_mounted()
    if (this.react_root && this.use_shadow_dom) {
      super.remove()
      this.react_root.then((root: any) => root?.unmount?.())
      this.flush_scheduled_removals()
    } else {
      this._applied_stylesheets.forEach((stylesheet) => stylesheet.uninstall())
      for (const cb of (this._lifecycle_handlers.get("remove") || [])) {
        cb()
      }
      this._child_callbacks.clear()
      this._child_rendered.clear()
      this._mounted.clear()
    }
    this.react_root = null
  }

  get root_view(): ReactComponentView {
    let root: ReactComponentView = this
    if (this.use_shadow_dom) {
      return root
    }
    while (root.parent instanceof ReactComponentView) {
      root = root.parent
    }
    return root
  }

  protected override _apply_stylesheets(stylesheets: StyleSheetLike[]): void {
    const resolved_stylesheets = stylesheets.map((style) => isString(style) ? new InlineStyleSheet(style) : style)
    const root_view = this.root_view
    const target = root_view.shadow_el
    // When shadow DOM is disabled every component in the tree installs its
    // stylesheets into the same root, so the existing CSS is indexed once and
    // looked up by value. Scanning the root per stylesheet made this quadratic
    // in the number of components times the number of stylesheets each.
    const installed_css = new Set<string | null>()
    const installed_hrefs = new Set<string>()
    if (!this.use_shadow_dom) {
      for (const style of target.querySelectorAll("style")) {
        installed_css.add(style.textContent)
      }
      for (const link of target.querySelectorAll("link")) {
        installed_hrefs.add(link.href)
      }
    }
    resolved_stylesheets.forEach((stylesheet) => {
      if (!this.use_shadow_dom) {
        if (stylesheet instanceof InlineStyleSheet) {
          if (installed_css.has(stylesheet.css)) {
            return
          }
          installed_css.add(stylesheet.css)
        } else if (stylesheet instanceof ImportedStyleSheet) {
          const {href} = (stylesheet as any).el
          if (installed_hrefs.has(href)) {
            return
          }
          installed_hrefs.add(href)
        }
      }
      this._applied_stylesheets.push(stylesheet)
      stylesheet.install(target)
    })
  }

  override render(): void {
    if (this.react_root) {
      this.react_root.then((root: any) => root?.unmount?.())
    }
    this._force_update_callbacks = []
    this.mounted = false
    // `super.render()` calls `render_esm`, which installs a fresh promise, so
    // settle any promise the previous render left outstanding first.
    this._resolve_mounted()
    super.render()
  }

  override r_after_render(): void {
    // If the DOM node was re-inserted, e.g. due to the parent
    // children changing order we must force an update in the
    // React component to ensure anything depending on the DOM
    // structure (e.g. emotion caches) is updated
    if (!this.model.use_shadow_dom) { this._apply_visible() }
    super.r_after_render()
    if (this.use_shadow_dom && this._dom_reinserted()) {
      this.force_update()
      this._mark_dom()
    }
  }

  /**
   * Re-inserting a node recreates the style sheets in its shadow root from
   * their text, dropping rules added through the CSSOM, which is how emotion
   * injects styles. A sentinel holding one CSSOM rule detects exactly that,
   * so that the parent re-rendering, which walks every child, only forces an
   * update (and a rebuild of the emotion cache) on the children it moved.
   */
  protected _dom_reinserted(): boolean {
    const sheet = this._dom_sentinel?.sheet
    return sheet == null || sheet.cssRules.length === 0
  }

  protected _mark_dom(): void {
    let sentinel = this._dom_sentinel
    if (sentinel == null || sentinel.parentNode !== this.shadow_el) {
      sentinel = document.createElement("style")
      this.shadow_el.append(sentinel)
      this._dom_sentinel = sentinel
    }
    sentinel.sheet?.insertRule(":host {}")
  }

  override _update_layout(): void {
    super._update_layout()
    const handlers = (this._lifecycle_handlers.get("update_layout") || [])
    for (const cb of handlers) {
      cb()
    }
  }

  override async build_child_views(): Promise<UIElementView[]> { // TODO BuildResult<UIElement>
    const build_fn = this.model.use_shadow_dom ? build_views_no_remove : build_views
    const {created, removed} = await build_fn(this._child_views, this.child_models, {parent: this})

    for (const view of removed) {
      this._resize_observer.unobserve(view.el)
      if (this.model.use_shadow_dom) {
        this._child_rendered.delete(view)
        if (created.length) {
          this._scheduled_removals.push(view)
        } else {
          view.remove()
        }
      }
    }

    for (const view of created) {
      this._resize_observer.observe(view.el, {box: "border-box"})
    }

    return created
  }

  protected override async _update_children_pass(): Promise<void> {
    const created_children = new Set(await this.build_child_views())

    const new_views = this._group_new_views(created_children)

    for (const child of this.model.children) {
      const callbacks = this._child_callbacks.get(child) || []
      const new_children = new_views.get(child) || []
      if (new_children) {
        for (const callback of callbacks) {
          callback(new_children)
        }
      }
    }
    this._update_children()
    // Removals are normally drained by the replacement child once it mounts,
    // but a child that never mounts would leak the old views, so flush any
    // that are still pending after React has had a chance to commit.
    setTimeout(() => this.flush_scheduled_removals(), 0)
  }

  flush_scheduled_removals(): void {
    const removals = this._scheduled_removals
    this._scheduled_removals = []
    for (const view of removals) {
      if (!view.is_destroyed) {
        view.remove()
      }
    }
  }

  override _on_mounted(): void {
    this.invalidate_layout()
    this.mounted = true
  }

  override has_finished(): boolean {
    return super.has_finished() && this._rendered
  }

  patch_container(container: HTMLDivElement): void {
    this.el = this.container = container
    this._update_stylesheets()
    this.class_list = new ClassList(this.container.classList)
    this._apply_html_attributes()
  }

  override after_rendered(): void {
    const handlers = (this._lifecycle_handlers.get("after_render") || [])
    for (const cb of handlers) {
      cb()
    }
    if (!this._rendered) {
      for (const cb of (this._lifecycle_handlers.get("after_layout") || [])) {
        cb()
      }
    }
    this._rendered = true
    if (this._mounted_resolve) {
      const child_ready: Promise<void>[] = []
      for (const child_view of this.child_views) {
        child_ready.push(child_view.ready)
      }
      if (child_ready.length > 0) {
        Promise.all(child_ready).then(() => this._resolve_mounted())
      } else {
        this._resolve_mounted()
      }
    }
    this.finish()
  }
}

type ReactLibs = {
  React: any
  createRoot: any
  createCache?: any
  CacheProvider?: any
}

const REACT_PACKAGES = ["react", "react-dom/client", "@emotion/cache", "@emotion/react"]

function react_libs_code(mui: boolean): string {
  if (mui) {
    return `
import * as React from "react"
import { createRoot } from "react-dom/client"
import createCache from "@emotion/cache"
import { CacheProvider } from "@emotion/react"
export default {React, createRoot, createCache, CacheProvider}`
  }
  return `
import * as React from "react"
import { createRoot } from "react-dom/client"
export default {React, createRoot}`
}

type ReactWrappers = {Child: any, Component: any, ErrorBoundary: any}

// Keyed by React so each React instance (one per bundle) gets its own
// classes, defined once rather than per render: a component type that is new
// on every render makes React remount the subtree and drop its state.
const REACT_WRAPPERS = new WeakMap<object, ReactWrappers>()

// A Component element is keyed by its view, so a view that replaces another
// in the same slot remounts instead of inheriting the old view's hook state.
const VIEW_KEYS = new WeakMap<ReactComponentView, number>()

let view_key_counter = 0

function view_key(view: ReactComponentView): number {
  let key = VIEW_KEYS.get(view)
  if (key === undefined) {
    key = view_key_counter++
    VIEW_KEYS.set(view, key)
  }
  return key
}

function emotion_key(id: string): string {
  return `css-${id.replace("-", "").replace(/\d/g, (digit) => String.fromCharCode(digit.charCodeAt(0) + 49)).toLowerCase()}`
}

function react_wrappers(libs: ReactLibs): ReactWrappers {
  const cached = REACT_WRAPPERS.get(libs.React)
  if (cached != null) {
    return cached
  }
  const {React, createCache, CacheProvider} = libs

  class Child extends React.PureComponent {
    declare props: any
    declare state: any
    declare setState: any
    render_callback: ((new_views: UIElementView[]) => void) | null = null
    containerRef: any = React.createRef()

    constructor(props: any) {
      super(props)
      this.state = {rendered: null}
      // Registers the child as tracked but not yet rendered. React's render
      // phase has to stay free of side effects, since a render may be
      // discarded without ever committing, so the flag is only ever flipped
      // here and from getSnapshotBeforeUpdate.
      this._mark_stale()
    }

    _mark_stale() {
      const view = this.view
      if (view) {
        this.props.parent._child_rendered.set(view, false)
      }
    }

    updateElement() {
      const el = this.view?.el
      if (el && this.containerRef.current && !this.containerRef.current.contains(el)) {
        this.containerRef.current.innerHTML = ""
        this.containerRef.current.appendChild(el)
      }
    }

    get view(): any {
      const model = this.props.model ?? this.props.parent.model.data[this.props.name]
      return this.props.parent.get_child_view(model)
    }

    get element() {
      const view = this.view
      return view == null ? null : view.el
    }

    get use_shadow_dom() {
      return this.view?.model.use_shadow_dom || (this.view?.react_root === undefined)
    }

    _render_nested(view: any, flush: boolean) {
      view.patch_container(this.containerRef.current)
      const apply = (mod: any) => {
        if (flush) {
          this.props.parent.flush_scheduled_removals()
        }
        this.setState(
          {rendered: mod.default.render(view)},
          () => {
            this.props.parent.notify_mount(this.props.name, view.model.id)
            this.view.r_after_render()
            this.view.after_rendered()
          },
        )
      }
      // Rendering synchronously once the module is loaded lets a nested tree
      // mount in one commit instead of one commit per level.
      const mod = view.model.resolved_render_module
      if (mod != null) {
        apply(mod)
      } else {
        view.model.render_module.then(apply)
      }
    }

    componentDidMount() {
      const view = this.view
      this.render_callback = (new_views: UIElementView[]) => {
        const view = this.view
        if (!view || !new_views.includes(view)) {
          return
        }
        this.updateElement()
        if (this.use_shadow_dom) {
          this.props.parent.flush_scheduled_removals()
          this.props.parent.render_child(view)
          this.props.parent._child_rendered.set(view, true)
        } else {
          this._render_nested(view, true)
        }
      }
      this.props.parent.on_child_render(this.props.name, this.render_callback)
      if (view == null) {
        return
      }
      this.props.parent.flush_scheduled_removals()
      if (this.use_shadow_dom) {
        this.updateElement()
        this.props.parent.render_child(view)
        this.props.parent._child_rendered.set(view, true)
        this.props.parent.notify_mount(this.props.name, view.model.id)
      } else {
        this._render_nested(view, false)
      }
    }

    componentWillUnmount() {
      if (this.render_callback) {
        this.props.parent.remove_on_child_render(this.props.name, this.render_callback)
      }
      // The mount bookkeeping lives on the parent, and the view may already be
      // gone by the time React unmounts us, so fall back to the model id prop.
      const id = this.view?.model.id ?? this.props.id
      if (id != null) {
        this.props.parent.notify_mount(this.props.name, id, true)
      }
    }

    getSnapshotBeforeUpdate() {
      // Commit-phase equivalent of the constructor's registration: the view
      // this Child renders may have been swapped out, so the incoming one is
      // registered as stale here rather than during render.
      this._mark_stale()
      return null
    }

    componentDidUpdate() {
      if (this.use_shadow_dom) {
        this.updateElement()
      }
    }

    render() {
      const class_name = this.use_shadow_dom ? "child-wrapper" : css_class_name(this.view.model.class_name)
      return React.createElement("div", {id: this.view?.model.id, className: class_name, ref: this.containerRef}, this.state.rendered)
    }
  }

  class ErrorBoundary extends React.Component {
    declare props: any
    declare state: any

    constructor(props: any) {
      super(props)
      this.state = {hasError: false}
    }

    static getDerivedStateFromError() {
      return {hasError: true}
    }

    componentDidCatch(error: any) {
      this.props.view.render_error(error)
    }

    render() {
      if (this.state.hasError) {
        return React.createElement("div")
      }
      return React.createElement("div", {className: "error-wrapper"}, this.props.children)
    }
  }

  class Component extends React.Component {
    declare props: any
    declare forceUpdate: any

    constructor(props: any) {
      super(props)
      this._init_cache()
    }

    _init_cache() {
      const {view} = this.props
      if (createCache != null && view.use_shadow_dom) {
        view.mui_cache = createCache({
          key: emotion_key(view.model.id),
          prepend: true,
          container: view.style_cache,
        })
      }
    }

    componentDidMount() {
      const {view} = this.props
      if (!view.use_shadow_dom) {
        return
      }
      view.on_force_update(() => {
        this._init_cache()
        this.forceUpdate()
      })
      view.after_rendered()
    }

    render() {
      const {view} = this.props
      let rendered = React.createElement(view.render_fn, this.props)
      if (view.model.dev) {
        rendered = React.createElement(ErrorBoundary, {view}, rendered)
      }
      if (CacheProvider != null && rendered && (view.parent?.react_root === undefined || view.model.use_shadow_dom)) {
        rendered = React.createElement(CacheProvider, {value: view.mui_cache}, rendered)
      }
      return rendered
    }
  }

  const wrappers = {Child, Component, ErrorBoundary}
  REACT_WRAPPERS.set(React, wrappers)
  return wrappers
}

function css_class_name(class_name: string): string {
  return class_name.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
}

function react_model_proxy(view: ReactComponentView, libs: ReactLibs, Child: any): any {
  const {React} = libs
  const react_proxy: any = new Proxy(view, {
    get(target: ReactComponentView, name: string) {
      if (name === "useMount") {
        return (callback: () => void) => React.useEffect(() => {
          target.model_proxy.on("lifecycle:mounted", callback)
          return () => target.model_proxy.off("lifecycle:mounted", callback)
        }, [])
      } else if (name === "useState") {
        return (prop: string) => {
          const path = prop.split(".")
          let model: any = target.model.data
          for (let i = 0; i < path.length - 1; i++) {
            if (model && model.properties && path[i] in model.properties) {
              model = model[path[i]]
            } else {
              model = null
              break
            }
          }
          const attr = path[path.length - 1]
          if (model == null || model.attributes == null || !(attr in model.attributes)) {
            throw ReferenceError(`Could not resolve ${prop} on ${target.model.class_name}`)
          }
          const [value, setValue] = React.useState(model.attributes[attr])

          React.useEffect(() => {
            const cb = () => {
              if (target.model.events.includes(attr)) {
                model.attributes[attr] && (setValue((v: number) => v+1) || model.setv({[attr]: false}))
              } else {
                setValue(model.attributes[attr])
              }
            }
            react_proxy.on(prop, cb, true)
            return () => react_proxy.off(prop, cb)
          }, [])

          const initialized = React.useRef(false)
          React.useEffect(() => {
            if (!target.model.events.includes(attr) && initialized.current) {
              model.setv({[attr]: value})
            } else {
              initialized.current = true
            }
          }, [value])

          return [value, setValue]
        }
      } else if (name === "get_child") {
        return (child: string) => {
          const data_model = target.model.data
          const value = data_model.attributes[child]
          if (!isArray(value)) {
            return React.createElement(Child, {parent: target, name: child})
          }
          const [children_state, set_children] = React.useState(() => value.map((model: any) =>
            React.createElement(Child, {parent: target, name: child, key: model.id, id: model.id, model}),
          ))
          React.useEffect(() => {
            // Compares against the latest state, not the closure's initial
            // one, and catches lists that only shrank.
            const cb = () => {
              const current_models = data_model.attributes[child]
              set_children((previous: any[]) => {
                if (previous.length === current_models.length &&
                    current_models.every((model: any, i: number) => model.id === previous[i].props.id)) {
                  return previous
                }
                return current_models.map((model: any) => (
                  React.createElement(Child, {parent: target, name: child, key: model.id, id: model.id, model})
                ))
              })
            }
            target.on_child_render(child, cb)
            return () => target.remove_on_child_render(child, cb)
          }, [])
          return children_state
        }
      }
      return model_getter(target, name)
    },
    set: model_setter,
  })
  return react_proxy
}

/**
 * Renders a view into a new React root, or, for a view nested in a parent
 * React tree without its own shadow root, returns the element for the parent
 * to render.
 */
function render_react(view: ReactComponentView, libs: ReactLibs): any {
  if (view.is_destroyed) {
    return null
  }
  const {React, createRoot} = libs
  const {Child, Component} = react_wrappers(libs)
  const props = {view, model: react_model_proxy(view, libs, Child), data: view.model.data, el: view.container}
  const rendered = React.createElement(Component, {...props, key: view_key(view)})
  if (!view.model.use_shadow_dom && ((view.parent as any)?.react_root !== undefined)) {
    return rendered
  }
  let container
  if (view.model.root_node) {
    container = document.querySelector(view.model.root_node)
    if (container == null) {
      container = document.createElement("div")
      container.id = view.model.root_node.replace("#", "")
      document.body.append(container)
    }
  } else if (view.container == null) {
    view._resolve_mounted()
    return null
  } else {
    container = view.container
  }
  const root = createRoot(container)
  try {
    root.render(rendered)
  } catch (e) {
    view._resolve_mounted()
    view.render_error(e as SyntaxError)
  }
  return root
}

export namespace ReactComponent {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ReactiveESM.Props & {
    root_node: p.Property<string | null>
    use_shadow_dom: p.Property<boolean>
  }
}

export interface ReactComponent extends ReactComponent.Attrs {}

export class ReactComponent extends ReactiveESM {
  declare properties: ReactComponent.Props
  override sucrase_transforms: Transform[] = ["typescript", "jsx"]

  constructor(attrs?: Partial<ReactComponent.Attrs>) {
    super(attrs)
  }

  get usesMui(): boolean {
    if (this.importmap?.imports) {
      return Object.keys(this.importmap?.imports).some(k => k.startsWith("@mui"))
    }
    return false
  }

  protected get _render_cache_key(): string {
    if (this.bundle) {
      return `react-${this.usesMui}-${this._module_cache_key}`
    }
    // Non-bundled components share one render module per set of React
    // packages, which the import map decides.
    const imports = this.importmap?.imports ?? {}
    const packages = REACT_PACKAGES.map((name) => imports[name] ?? "").join("|")
    return `react-${this.usesMui}-${packages}`
  }

  protected override _render_module(): Promise<any> {
    return this._cached_module(this._render_cache_key, async () => {
      let libs: ReactLibs
      if (this.bundle) {
        const ns = await this._cached_module(this._module_cache_key, () => Promise.resolve(null))
        libs = ns.default
      } else {
        libs = (await this._import_source(react_libs_code(this.usesMui))).default
      }
      return {default: {render: (view: ReactComponentView) => render_react(view, libs)}}
    })
  }

  override compile(): string | null {
    const compiled = super.compile()
    if (this.bundle) {
      return compiled
    } else if (compiled === null || !compiled.includes("React")) {
      return compiled
    }
    return `
import * as React from "react"

${compiled}`
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = ReactComponentView
    this.define<ReactComponent.Props>(({Bool, Nullable, Str}) => ({
      root_node:  [ Nullable(Str), null ],
      use_shadow_dom:   [ Bool,    true ],
    }))

    this.override<ReactComponent.Props>({
      render_policy: "manual",
    })
  }
}
