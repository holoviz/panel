import {h, render, Component} from 'preact';
import {
  useCallback,
  useContext,
  useEffect,
  useErrorBoundary,
  useLayoutEffect,
  useState,
  useReducer
} from 'preact/hooks';
import { transform } from 'sucrase';

import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {Model} from "@bokehjs/model"
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {HTMLBox, HTMLBoxView} from "./layout"

function useState_getter(target: Model, name: string) {
  if (!Reflect.has(target, name))
    return undefined
  const [value, setValue] = useState(target.attributes[name]);
  (target as any).properties[name].change.connect(() => {
    setValue(target.attributes[name])
  });
  useEffect(() => {
    const state: { [key: string]: any } = {}
    state[name] = value
    target.setv(state)
  }, [value]);
  return [value, setValue]
}

export class ReactiveESMView extends HTMLBoxView {
  model: ReactiveESM
  container: HTMLDivElement
  modelState: typeof Proxy
  ns: any = {
    React: {
      Component,
      useCallback,
      useContext,
      useEffect,
      useErrorBoundary,
      useLayoutEffect,
      useState,
      useReducer,
      createElement: h,
      render
    },
  }
  _changing: boolean = false
  _watchers: any = {}

  initialize(): void {
    super.initialize()

    this.modelState = new Proxy(this.model.data, {
      get: useState_getter
    })

    this.model.data.watch = (callback: any, prop: string) => {
      const watcher = this.model.data.properties[prop].change.connect(() => {
        callback(prop, null, this.model.data[prop])
      });
      if (!(prop in this._watchers))
	this._watchers[prop] = []
      this._watchers[prop].push(watcher)
    }
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.esm.change, () => {
      this.invalidate_render()
    })
  }

  get child_models(): LayoutDOM[] {
    const models = []
    for (const parent in this.model.children) {
      for (const model of this.model.children[parent])
        if (typeof model !== 'string')
          models.push(model)
    }
    return models
  }

  render(): void {
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this.container = div({style: "display: contents;"})
    this.shadow_el.append(this.container)
    this._render_esm()
  }

  private _render_esm(): void {
    if (!this.model.esm)
	return

    const defs = []
    for (const exp in this.ns)
      defs.push(`const ${exp} = view.ns['${exp}'];`)
    const def_string = defs.join('\n    ')

    let compiledCode = transform(this.model.esm, {transforms: ["jsx", "typescript"], filePath: "test.tsx"}).code;

    let dyn = document.createElement("script")
    dyn.type = "module"
    dyn.innerHTML = `
    const root = Bokeh.index['${this.root.model.id}']
    const views = [...root.owner.query((view) => view.model.id == '${this.model.id}')]
    const view = views[0]
    console.log(views)
    ${def_string}
    ${compiledCode}

    const rendered = render({model: view.model, data: view.model.data, el: view.container, state: view.modelState});

    if (rendered) {
      view._changing = true;
      React.render(rendered, view.container);
      view._changing = false;
    }`;
    this.container.appendChild(dyn)
  }
}

export namespace ReactiveESM {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    children: p.Property<any>
    data: p.Property<any>
    esm: p.Property<string>
  }
}

export interface ReactiveESM extends ReactiveESM.Attrs {}

export class ReactiveESM extends HTMLBox {
  properties: ReactiveESM.Props

  constructor(attrs?: Partial<ReactiveESM.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.reactive_html"

  static {
    this.prototype.default_view = ReactiveESMView
    this.define<ReactiveESM.Props>(({Any, String}) => ({
      children:  [ Any,       {} ],
      data:      [ Any,          ],
      esm:       [ String,    "" ],
    }))
  }
}
