import type * as p from "@bokehjs/core/properties"
import type {Transform} from "sucrase"

import {ReactiveESM, ReactiveESMView} from "./reactive_esm"

export class ReactComponentView extends ReactiveESMView {
  declare model: ReactComponent
  override sucrase_transforms: Transform[] = ["typescript", "jsx"]

  protected override _render_esm(): void {
    this.disconnect_watchers()
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
    let import_code = `
import * as React from "react"
import { createRoot } from 'react-dom/client'`
    let render_code = `
if (rendered) {
  view._changing = true
  const root = createRoot(view.container)
  root.render(rendered)
  view._changing = false
}`
    if (Object.keys(importMap.imports).some(k => k.startsWith("@mui"))) {
      importMap.imports = {
        ...importMap.imports,
        "@emotion/cache": "https://esm.sh/@emotion/cache",
        "@emotion/react": "https://esm.sh/@emotion/react",
      }
      import_code = `
${import_code}
import createCache from "@emotion/cache"
import { CacheProvider } from '@emotion/react'
`
      render_code = `
const headElement = document.createElement("head")
view.shadow_el.insertBefore(headElement, view.container)

const cache = createCache({
  key: 'css',
  prepend: true,
  container: headElement,
})

if (rendered) {
  view._changing = true
  const root = createRoot(view.container)
  root.render(
    React.createElement(CacheProvider, {value: cache}, rendered)
  )
  view._changing = false;
}`
    }
    // @ts-ignore
    importShim.addImportMap(importMap)

    const code = `
${import_code}

const view = Bokeh.index.find_one_by_id('${this.model.id}')

function useState_getter(target, name) {
  if (!Reflect.has(target, name)) {
    return undefined
  }
  const [value, setValue] = React.useState(target.attributes[name]);
  view.model.data.watch(() => {
    setValue(target.attributes[name])
  }, name)
  React.useEffect(() => {
    const state = {}
    state[name] = value
    target.setv(state)
  }, [value])
  return [value, setValue]
}

const modelState = new Proxy(view.model.data, {
  get: useState_getter
})

const children = {}
for (const child of view.model.children) {
  const child_model = view.model.data[child]
  const multiple = Array.isArray(child_model)
  const models = multiple ? child_model : [child_model]
  const components = []
  for (const model of models) {
    class Child extends React.Component {
      child_name = child
      parent = view
      view = view._child_views.get(model)
      node = view._child_views.get(model).el

      componentDidMount() {
        this.parent.on_child_render(this.child_name, () => this.rerender())
        this.view.render()
        this.view.after_render()
      }

      componentDidUnmount() {
        this.parent.remove_on_child_render(this.child_name)
      }

      rerender() {
        this.view = this.parent._child_views.get(view.model.data[child])
        this.node = this.view.el
        this.forceUpdate()
        this.view.render()
        this.view.after_render()
      }

      render() {
        return React.createElement('div', {className: "child-wrapper", ref: (ref) => ref && ref.appendChild(this.node)})
      }
    }
    components.push(React.createElement(Child))
  }
  children[child] = multiple ? components: components[0]
}

${this.rendered}

const rendered = render({view: view, model: view.model, data: view.model.data, el: view.container, state: modelState, children: children})

${render_code}`

    const url = URL.createObjectURL(
      new Blob([code], {type: "text/javascript"}),
    )
    // @ts-ignore
    importShim(url)
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
