import type * as p from "@bokehjs/core/properties"
import type {Transform} from "sucrase"

import {
  ReactiveESM, ReactiveESMView, model_getter, model_setter,
} from "./reactive_esm"

export class ReactComponentView extends ReactiveESMView {
  declare model: ReactComponent
  declare style_cache: HTMLHeadElement
  model_getter = model_getter
  model_setter = model_setter

  _force_update_callbacks: (() => void)[] = []

  override render_esm(): void {
    if (this.model.usesMui) {
      if (this.model.root_node) {
        this.style_cache = document.head
      } else {
        this.style_cache = document.createElement("head")
        this.shadow_el.insertBefore(this.style_cache, this.container)
      }
    }
    super.render_esm()
  }

  on_force_update(cb: () => void): void {
    this._force_update_callbacks.push(cb)
  }

  force_update(): void {
    for (const cb of this._force_update_callbacks) {
      cb()
    }
  }

  override render(): void {
    this._force_update_callbacks = []
    super.render()
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
  }

  protected override _render_code(): string {
    let import_code
    const cache_key = (this.model.bundle === "url") ? this.model.esm : (this.model.bundle || `${this.model.class_name}-${this.model.esm.length}`)
    if (this.model.bundle) {
      import_code = `
const ns = await view._module_cache.get("${cache_key}")
const {React, createRoot} = ns.default`
    } else {
      import_code = `
import * as React from "react"
import { createRoot } from "react-dom/client"`
    }
    let extra_code = ""
    if (this.model.usesMui) {
      if (this.model.bundle) {
        import_code = `
const ns = await view._module_cache.get("${cache_key}")
const {CacheProvider, React, createCache, createRoot} = ns.default`
      } else {
        import_code = `
${import_code}
import createCache from "@emotion/cache"
import { CacheProvider } from "@emotion/react"`
      }
      const css_key = this.model.id.replace("-", "").replace(/\d/g, (digit) => String.fromCharCode(digit.charCodeAt(0) + 49)).toLowerCase()
      extra_code = `
  if (rendered) {
    const cache = createCache({
      key: 'css-${css_key}',
      prepend: true,
      container: view.style_cache,
    })
    rendered = React.createElement(CacheProvider, {value: cache}, rendered)
  }`
    }
    return `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

${import_code}

class Child extends React.Component {

  constructor(props) {
    super(props)
    this.render_callback = null
  }

  get view() {
    const child = this.props.parent.model.data[this.props.name]
    const model = this.props.index == null ? child : child[this.props.index]
    return this.props.parent.get_child_view(model)
  }

  get element() {
    const view = this.view
    return view == null ? null : view.el
  }

  componentDidMount() {
    this.view.render()
    this.view.r_after_render()
    this.render_callback = (new_views) => {
      const view = this.view
      if (view == null) {
        return
      }
      this.forceUpdate()
      if (new_views.includes(view)) {
        view.render()
        view.r_after_render()
      } else if (view.force_update) {
        view.force_update()
      }
    }
    this.props.parent.on_child_render(this.props.name, this.render_callback)
  }

  componentWillUnmount() {
    if (this.render_callback) {
      this.props.parent.remove_on_child_render(this.props.name, this.render_callback)
    }
  }

  render() {
    return React.createElement('div', {
      className: "child-wrapper",
      ref: (ref) => {
        if (ref != null && this.view != null) {
          ref.appendChild(this.element)
        }
      }
    })
  }
}

function react_getter(target, name) {
  if (name == "useState") {
    return (prop) => {
      const data_model = target.model.data
      const propPath = prop.split(".")
      let targetModel = data_model
      let resolvedProp = null

      for (let i = 0; i < propPath.length - 1; i++) {
        if (targetModel && targetModel.properties && propPath[i] in targetModel.properties) {
          targetModel = targetModel[propPath[i]]
        } else {
          // Stop if any part of the path is missing
          targetModel = null
          break
        }
      }
      if (targetModel && targetModel.attributes && propPath[propPath.length - 1] in targetModel.attributes) {
        resolvedProp = propPath[propPath.length - 1]
      }
      if (resolvedProp && targetModel) {
        const [value, setValue] = React.useState(targetModel.attributes[resolvedProp])

        react_proxy.on(prop, () => setValue(targetModel.attributes[resolvedProp]))

        React.useEffect(() => {
            targetModel.setv({ [resolvedProp]: value })
        }, [value])

        return [value, setValue]
      }
      throw ReferenceError("Could not resolve " + prop + " on " + target.model.class_name)
    }
  } else if (name === "get_child") {
    return (child) => {
      const data_model = target.model.data
      const value = data_model.attributes[child]
      if (Array.isArray(value)) {
        const [children_state, set_children] = React.useState(value.map((model, i) =>
          React.createElement(Child, { parent: target, name: child, key: child+i, index: i })
        ))

        React.useEffect(() => {
          target.on_child_render(child, () => {
            const current_models = data_model.attributes[child]
            const previous_models = children_state.map(child => child.props.index)
            if (current_models.length !== previous_models.length ||
                current_models.some((model, i) => i !== previous_models[i])) {
              set_children(current_models.map((model, i) => (
                React.createElement(Child, { parent: target, name: child, key: child+i, index: i })
              )))
            }
          })
        }, [])
        return children_state
      } else {
        return React.createElement(Child, {parent: target, name: child})
      }
    }
  }
  return target.model_getter(target, name)
}

const react_proxy = new Proxy(view, {
  get: react_getter,
  set: view.model_setter
})

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    // initialize the error state
    this.state = { hasError: false }
  }

  // if an error happened, set the state to true
  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error) {
    this.props.view.render_error(error)
  }

  render() {
    if (this.state.hasError) {
      return React.createElement('div')
    }
    return React.createElement('div', {className: "error-wrapper"}, this.props.children)
  }
}

class Component extends React.Component {

  componentDidMount() {
    this.props.view.on_force_update(() => {
      this.forceUpdate()
    })
    this.props.view._changing = false
    this.props.view.after_rendered()
  }

  render() {
    let rendered = React.createElement(this.props.view.render_fn, this.props)
    if (this.props.view.model.dev) {
       rendered = React.createElement(ErrorBoundary, {view}, rendered)
    }
    ${extra_code}
    return rendered
  }
}

function render() {
  const props = {view, model: react_proxy, data: view.model.data, el: view.container}
  const rendered = React.createElement(Component, props)
  if (rendered) {
    view._changing = true
    let container
    if (view.model.root_node) {
      container = document.querySelector(view.model.root_node)
      if (container == null) {
        container = document.createElement("div")
        container.id = view.model.root_node.replace("#", "")
        document.body.append(container)
      }
    } else {
      container = view.container
    }
    const root = createRoot(container)
    try {
      root.render(rendered)
    } catch(e) {
      view.render_error(e)
    }
  }
}

export default {render}`
  }
}

export namespace ReactComponent {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ReactiveESM.Props & {
    root_node: p.Property<string | null>
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
    this.define<ReactComponent.Props>(({Nullable, Str}) => ({
      root_node:  [ Nullable(Str),     null ],
    }))
  }
}
