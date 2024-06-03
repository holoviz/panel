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
  override sucrase_transforms: Transform[] = ["typescript", "jsx"]

  protected override _declare_importmap(): void {
    const react_version = this.model.react_version
    const imports = this.model.importmap?.imports
    const scopes = this.model.importmap?.scopes
    const importMap = {
      imports: {
        react: `https://esm.sh/react@${react_version}`,
        "react-dom/": `https://esm.sh/react-dom@${react_version}/`,
        ...imports,
      },
      scopes: scopes || {},
    }
    if (this.usesMui) {
      importMap.imports = {
        ...importMap.imports,
        "@emotion/cache": "https://esm.sh/@emotion/cache",
        "@emotion/react": "https://esm.sh/@emotion/react",
      }
    }
    // @ts-ignore
    importShim.addImportMap(importMap)
  }

  get usesMui(): boolean {
    if (this.model.importmap?.imports) {
      return Object.keys(this.model.importmap?.imports).some(k => k.startsWith("@mui"))
    }
    return false
  }

  get usesReact(): boolean {
    return this.compiled !== null && this.compiled.includes("React")
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

  override render_esm(): void {
    if (this.usesMui) {
      this.style_cache = document.createElement("head")
      this.shadow_el.insertBefore(this.style_cache, this.container)
    }
    super.render_esm()
  }

  protected override _render_code(): string {
    let render_code = `
if (rendered && view.usesReact) {
  view._changing = true
  const root = createRoot(view.container)
  root.render(rendered)
  view._changing = false
}`
    let import_code = `
import * as React from "react"
import { createRoot } from 'react-dom/client'`
    if (this.usesMui) {
      import_code = `
${import_code}
import createCache from "@emotion/cache"
import { CacheProvider } from "@emotion/react"`
      render_code = `
if (rendered) {
  const cache = createCache({
    key: 'css',
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

  get views() {
    const model = this.props.parent.model.data[this.props.name]
    const models = Array.isArray(model) ? model : [model]
    const views = []
    for (const submodel of models) {
      const child = this.props.parent.get_child_view(submodel)
      if (child) {
        views.push(child)
      }
    }
    return views
  }

  get elements() {
    return this.views.map(view => view.el)
  }

  componentDidMount() {
    this.views.map((view) => {
      view.render()
      view.after_render()
    })
    this.props.parent.on_child_render(this.props.name, (new_views) => {
      this.forceUpdate()
      this.views.map((view) => {
        if (new_views.includes(view)) {
          view.render()
          view.after_render()
        }
      })
    })
  }

  render() {
    return React.createElement('div', {className: "child-wrapper", ref: (ref) => ref && this.elements.map(el => ref.appendChild(el))})
  }
}

function react_getter(target, name) {
  if (name == "useState") {
    return (prop) => {
      const data_model = target.model.data
      if (Reflect.has(data_model, prop)) {
        const [value, setValue] = React.useState(data_model.attributes[prop]);
        react_proxy.watch(() => setValue(data_model.attributes[prop]), prop)
        React.useEffect(() => data_model.setv({[prop]: value}), [value])
        return [value, setValue]
      }
      return undefined
    }
  } else if (name === "get_child") {
    return (child) => React.createElement(Child, {parent: target, name: child})
  }
  return target.model_getter(target, name)
}

const react_proxy = new Proxy(view, {
  get: react_getter,
  set: view.model_setter
})

const props = {view, model: react_proxy, data: view.model.data, el: view.container}
let rendered = React.createElement(view.render_fn, props)

${render_code}`
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

  constructor(attrs?: Partial<ReactComponent.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = ReactComponentView

    this.define<ReactComponent.Props>(({String}) => ({
      react_version: [ String,    "18.2.0" ],
    }))
  }
}
