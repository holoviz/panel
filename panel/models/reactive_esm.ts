import { transform } from 'sucrase';

import {div, remove} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {HTMLBox, HTMLBoxView} from "./layout"
import {loadScript} from "./util"

function loadESMSOptions(options: any) {
  const script = document.createElement("script")
  script.type = "esms-options"
  script.innerHTML = JSON.stringify(options)
  document.head.appendChild(script)
}

let importShimLoaded : any = null;

async function ensureImportShimLoaded() {
  if(importShimLoaded == null) {
    importShimLoaded = loadScript("module", "https://ga.jspm.io/npm:es-module-shims@1.7.0/dist/es-module-shims.js")
  }
  return await importShimLoaded;
}

export class ReactiveESMView extends HTMLBoxView {
  declare model: ReactiveESM
  container: HTMLDivElement
  modelState: typeof Proxy
  rendered: string | null = null
  _changing: boolean = false
  _watchers: any = {}
  _child_callbacks: {[key: string]: () => void} = {}
  _parent_nodes: any = {}

  override initialize(): void {
    super.initialize();
    this.model.data.watch = (callback: any, prop: string) => {
      const watcher = this.model.data.properties[prop].change.connect(() => {
        callback(prop, null, this.model.data[prop])
      });
      if (!(prop in this._watchers))
	this._watchers[prop] = []
      this._watchers[prop].push(watcher)
    }
  }

  override async lazy_initialize(): Promise<void> {
    // @ts-ignore
    const esmsInitOptions = {
      shimMode: true,
    }
    loadESMSOptions(esmsInitOptions)
    await ensureImportShimLoaded()
    super.lazy_initialize()
  }

  override connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.esm.change, () => {
      this.invalidate_render()
    })
    const child_props = this.model.children.map((child: string) => this.model.data.properties[child])
    this.on_change(child_props, () => {
      this.update_children()
    })
  }


  override disconnect_signals(): void {
    super.disconnect_signals()
    this._child_callbacks = {}
    this._watchers = {}
  }

  override get child_models(): LayoutDOM[] {
    const children = []
    for (const child of this.model.children) {
      const model = this.model.data[child]
      if (model != null)
	children.push(model)
    }
    return children
  }

  override render(): void {
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this._child_callbacks = {}
    this._watchers = {}

    this.container = div({style: "display: contents;"})
    this.shadow_el.append(this.container)
    this.rendered = transform(this.model.esm, {transforms: ["jsx", "typescript"], filePath: "render.tsx"}).code;
    console.log(this.rendered)
    if (this.rendered.includes('React')) {
      this._render_esm_react()
    } else {
      this._render_esm()
    }
  }

  private _render_esm(): void {
    if (this.model.importmap) {
      const importMap = {
        "imports": this.model.importmap["imports"],
        "scopes": this.model.importmap["scopes"]
      };
      // @ts-ignore
      importShim.addImportMap(importMap);
    }

    const code = `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

const children = {}
for (const child of view.model.children) {
  children[child] = view._child_views.get(view.model.data[child])
}

${this.rendered}

render({view: view, model: view.model, data: view.model.data, el: view.container, children});
view.render_children();
`

    const url = URL.createObjectURL(
      new Blob([code], { type: "text/javascript" }),
    );
    // @ts-ignore
    importShim(url);
  }

  render_children() {
    for (const child of this.model.children) {
      const view = this._child_views.get(this.model.data[child])
      if (view && this.container.contains(view.el)) {
	const parent = view.el.parentNode
	if (parent) {
	  this._parent_nodes[child] = [parent, Array.from(parent.children).indexOf(view.el)]
	  view.render()
	  view.after_render()
	}
      }
    }
  }

  override async update_children(): Promise<void> {
    const created_children = new Set(await this.build_child_views())

    if (created_children.size != 0) {
      for (const child_view of this.child_views) {
	remove(child_view.el)
      }

      for (const child in this._child_callbacks) {
	this._child_callbacks[child]()
      }
    }

    for (const child in this._parent_nodes) {
      const [parent, index] = this._parent_nodes[child]
      const view = this._child_views.get(this.model.data[child])
      if (view) {
	const next_child = parent.children[index]
	if (next_child) {
	  parent.insertBefore(view.el, next_child)
	} else {
	  parent.append(view.el)
	}
	view.render()
	view.after_render()
      }
    }
    this._update_children()
    this.invalidate_layout()
  }

  on_child_render(child: string, callback: () => void): void {
    this._child_callbacks[child] = callback
  }

  remove_on_child_render(child: string): void {
    delete this._child_callbacks[child]
  }

  private _render_esm_react(): void {
    if (this.model.importmap) {
      const importMap = {
        "imports": {
          "react": "https://esm.sh/react@18.2.0",
          "react-dom/": "https://esm.sh/react-dom@18.2.0/",
          ...this.model.importmap['imports']
        },
        "scopes": this.model.importmap["scopes"]
      };
      // @ts-ignore
      importShim.addImportMap(importMap);
    }

    const code = `
import { createRoot } from 'react-dom/client';
import * as React from "react";

const view = Bokeh.index.find_one_by_id('${this.model.id}')

function useState_getter(target, name) {
  if (!Reflect.has(target, name))
    return undefined
  const [value, setValue] = React.useState(target.attributes[name]);
  (target).properties[name].change.connect(() => {
    setValue(target.attributes[name])
  });
  React.useEffect(() => {
    const state = {}
    state[name] = value
    target.setv(state)
  }, [value]);
  return [value, setValue]
}

const modelState = new Proxy(view.model.data, {
  get: useState_getter
})

const children = {}
for (const child of view.model.children) {
  class Child extends React.Component {
    child_name = child
    parent = view
    view = view._child_views.get(view.model.data[child])
    node = view._child_views.get(view.model.data[child]).el

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
  children[child] = React.createElement(Child)
}

${this.rendered}

const rendered = render({view: view, model: view.model, data: view.model.data, el: view.container, state: modelState, children: children});

if (rendered) {
  view._changing = true;
  const root = createRoot(view.container);
  root.render(rendered);
  view._changing = false;
}`;

    const url = URL.createObjectURL(
      new Blob([code], { type: "text/javascript" }),
    );
    // @ts-ignore
    importShim(url);
  }
}

export namespace ReactiveESM {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    children: p.Property<any>
    data: p.Property<any>
    esm: p.Property<string>
    importmap: p.Property<any>
  }
}

export interface ReactiveESM extends ReactiveESM.Attrs {}

export class ReactiveESM extends HTMLBox {
  declare properties: ReactiveESM.Props

  constructor(attrs?: Partial<ReactiveESM.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.reactive_html"

  static {
    this.prototype.default_view = ReactiveESMView
    this.define<ReactiveESM.Props>(({Any, Array, String}) => ({
      children:  [ Array(String),       [] ],
      data:      [ Any,                    ],
      importmap: [ Any,                 {} ],
      esm:       [ String,              "" ],
    }))
  }
}
