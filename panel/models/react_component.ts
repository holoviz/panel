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

  override render_esm(): void {
    if (this.model.usesMui) {
      this.style_cache = document.createElement("head")
      this.shadow_el.insertBefore(this.style_cache, this.container)
    }
    super.render_esm()
  }

  override after_rendered(): void {
    const handlers = (this._lifecycle_handlers.get("after_render") || [])
    for (const cb of handlers) {
      cb()
    }
    this._rendered = true
  }

  protected override _render_code(): string {
    let render_code = `
  if (rendered && view.model.usesReact) {
    view._changing = true
    const root = createRoot(view.container)
    try {
      root.render(rendered)
    } catch(e) {
      view.render_error(e)
    }
    view._changing = false
    view.after_rendered()
  }`
    let import_code = `
import * as React from "react"
import { createRoot } from "react-dom/client"`
    if (this.model.usesMui) {
      import_code = `
${import_code}
import createCache from "@emotion/cache"
import { CacheProvider } from "@emotion/react"`
      render_code = `
  if (rendered) {
    const cache = createCache({
      key: 'css-${this.model.id}',
      prepend: true,
      container: view.style_cache,
    })
    rendered = React.createElement(CacheProvider, {value: cache}, rendered)
  }
  ${render_code}`
    }
    return `
${import_code}

const view = Bokeh.index.find_one_by_id('${this.model.id}')

class Child extends React.Component {

  get view() {
    const model = this.props.parent.model.data[this.props.name]
    const models = Array.isArray(model) ? model : [model]
    return this.props.parent.get_child_view(models[this.props.index])
  }

  get element() {
    const view = this.view
    return view == null ? null : view.el
  }

  componentDidMount() {
    this.view.render()
    this.view.after_render()
    this.props.parent.on_child_render(this.props.name, (new_views) => {
      this.forceUpdate()
      const view = this.view
      if (new_views.includes(view)) {
        view.render()
        view.after_render()
      }
    })
  }

  append_child(ref) {
    if (ref != null) {
       const view = this.view
       if (view != null) {
         ref.appendChild(this.element)
       }
    }
  }

  render() {
    return React.createElement('div', {className: "child-wrapper", ref: (ref) => this.append_child(ref)})
  }
}

function react_getter(target, name) {
  if (name == "useState") {
    return (prop) => {
      const data_model = target.model.data
      if (Reflect.has(data_model, prop)) {
        const [value, setValue] = React.useState(data_model.attributes[prop]);
        react_proxy.on(prop, () => setValue(data_model.attributes[prop]))
        React.useEffect(() => data_model.setv({[prop]: value}), [value])
        return [value, setValue]
      }
      return undefined
    }
  } else if (name === "get_child") {
    return (child) => {
      const data_model = target.model.data
      const value = data_model.attributes[child]
      if (Array.isArray(value)) {
        const children = []
        for (let i = 0; i<value.length; i++) {
          children.push(
            React.createElement(Child, {parent: target, name: child, index: i, key: child+i})
          )
        }
        const [children_state, set_children] = React.useState(children);
        target.on_child_render(child, (new_views) => {
          const value = data_model.attributes[child]
          if (new_views.length && children_state.length !== value.length) {
            const children = []
            for (let i = 0; i<value.length; i++) {
              let new_child
              if (i < children_state.length) {
                new_child = children_state[i]
              } else {
                new_child = React.createElement(Child, {parent: target, name: child, index: i, key: child+i})
              }
              children.push(new_child)
            }
            set_children(children)
          }
        })
        return children_state
      } else {
        return React.createElement(Child, {parent: target, name: child, index: 0})
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
    super(props);
    // initialize the error state
    this.state = { hasError: false };
  }

  // if an error happened, set the state to true
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error) {
    this.props.view.render_error(error)
  }

  render() {
    if (this.state.hasError) {
      return React.createElement('div')
    }
    return React.createElement('div', {}, this.props.children);
  }
}

class Component extends React.Component {

  componentDidMount() {
    this.props.view.after_rendered()
  }

  render() {
    let rendered = React.createElement(this.props.view.render_fn, this.props)
    if (this.props.view.model.dev) {
       rendered = React.createElement(ErrorBoundary, {view}, rendered)
    }
    return rendered
  }
}

function render() {
  const props = {view, model: react_proxy, data: view.model.data, el: view.container}
  let rendered = React.createElement(Component, props)

  ${render_code}
}

export default {render}`
  }
}

export namespace ReactComponent {
  export type Attrs = p.AttrsOf<Props>

  export type Props = ReactiveESM.Props & {
    react_version: p.Property<string>
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

  get usesReact(): boolean {
    return this.compiled !== null && this.compiled.includes("React")
  }

  protected override _declare_importmap(): void {
    const react_version = this.react_version
    const imports = this.importmap?.imports
    const scopes = this.importmap?.scopes
    const pkg_suffix = this.dev ? "?dev": ""
    const path_suffix = this.dev ? "&dev": ""
    const importMap = {
      imports: {
        react: `https://esm.sh/react@${react_version}${pkg_suffix}`,
        "react/": `https://esm.sh/react@${react_version}${path_suffix}/`,
	"react-dom": `https://esm.sh/react-dom@${react_version}?deps=react@${react_version}${pkg_suffix}&external=react`,
        "react-dom/": `https://esm.sh/react-dom@${react_version}&deps=react@${react_version}${path_suffix}&external=react/`,
        ...imports,
      },
      scopes: scopes || {},
    }
    if (this.usesMui) {
      importMap.imports = {
        ...importMap.imports,
	"react-is": `https://esm.sh/react-is@${react_version}&external=react`,
        "@emotion/cache": `https://esm.sh/@emotion/cache?deps=react@${react_version},react-dom@${react_version}`,
        "@emotion/react": `https://esm.sh/@emotion/react?deps=react@${react_version},react-dom@${react_version}&external=react${path_suffix},react-is`,
      }
    }
    // @ts-ignore
    importShim.addImportMap(importMap)
  }

  override compile(): string | null {
    const compiled = super.compile()
    if (compiled === null || !compiled.includes("React")) {
      return compiled
    }
    return `
import * as React from "react"

${compiled}`
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = ReactComponentView

    this.define<ReactComponent.Props>(({String}) => ({
      react_version: [ String,    "18.3.1" ],
    }))
  }
}
