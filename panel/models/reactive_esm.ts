import { transform } from 'sucrase';

import {div, remove} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {isArray} from "@bokehjs/core/util/types"
import {render} from "preact"
import {html} from "htm/preact"

import {serializeEvent} from "./event-to-object"
import {DOMEvent} from "./html"
import {HTMLBox, HTMLBoxView} from "./layout"
import {convertUndefined} from "./util"

function extractDataAttributes(text: string) {
  const regex = /\bdata\.([a-zA-Z_][a-zA-Z0-9_]*)\b/g;
  const ignored = ['send_event', 'watch']
  let matches = [];
  let match, attr;

  while ((match = regex.exec(text)) !== null && (attr = match[0].slice(5)) !== null && !ignored.includes(attr)) {
    matches.push(attr);
  }

  return matches;
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
  _htm = html
  _render_htm = render
  _rerender_vars: string[] = []

  override initialize(): void {
    super.initialize();
    this.model.data.watch = (callback: any, prop: string | string[]) => {
      const props = isArray(prop) ? prop : [prop]
      for (const p of props) {
	const cb = () => {
          callback(prop, null, this.model.data[p])
        }
        this.model.data.properties[p].change.connect(cb);
        if (p in this._watchers) {
          this._watchers[p].push(cb)
        } else {
          this._watchers[p] = [cb]
        }
      }
    }
    this.model.data.send_event = (name: string, event: Event) => {
      const serialized = convertUndefined(serializeEvent(event))
      this.model.trigger_event(new DOMEvent(name, serialized))
    }
  }

  disconnect_watchers(): void {
    for (const p in this._watchers) {
      const prop = this.model.data.properties[p]
      for (const cb of this._watchers[p]) {
	prop.change.disconnect(cb)
      }
    }
    this._watchers = {}
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
    this._rerender_vars = extractDataAttributes(this.rendered)
    if (this.rendered.includes('React')) {
      this._render_esm_react()
    } else {
      this._render_esm()
    }
  }

  private _render_esm(): void {
    this.disconnect_watchers()
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

const output = render({view: view, model: view.model, data: view.model.data, el: view.container, children, html: view._htm});

if (output instanceof Element) {
  view.container.appendChild(output)
} else if (output) {
  view._render_htm(output, view.container)
  view.model.data.watch(() => view._render_esm(), view._rerender_vars)
}

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
    this.disconnect_watchers()
    const imports = this.model.importmap?.imports
    const scopes = this.model.importmap?.scopes
    const importMap = {
      "imports": {
        "react": "https://esm.sh/react@18.2.0",
        "react-dom/": "https://esm.sh/react-dom@18.2.0/",
        ...imports
      },
      "scopes": scopes || {}
    };
    let import_code = `
import * as React from "react";
import { createRoot } from 'react-dom/client';`
    let render_code = `
if (rendered) {
  view._changing = true;
  const root = createRoot(view.container);
  root.render(rendered);
  view._changing = false;
}`
    if (Object.keys(importMap.imports).some(k => k.startsWith('@mui'))) {
      importMap.imports = {
	...importMap.imports,
	"@emotion/cache": "https://esm.sh/@emotion/cache",
	"@emotion/react": "https://esm.sh/@emotion/react",
      }
      import_code = `
${import_code}
import createCache from "@emotion/cache";
import { CacheProvider } from '@emotion/react';
`
      render_code = `
const headElement = document.createElement("head");
view.shadow_el.insertBefore(headElement, view.container);

const cache = createCache({
  key: 'css',
  prepend: true,
  container: headElement,
});

if (rendered) {
  view._changing = true;
  const root = createRoot(view.container);
  root.render(
    React.createElement(CacheProvider, {value: cache}, rendered)
  );
  view._changing = false;
}`
      // @ts-ignore
      importShim.addImportMap(importMap);
    }

    const code = `
${import_code}

const view = Bokeh.index.find_one_by_id('${this.model.id}')

function useState_getter(target, name) {
  if (!Reflect.has(target, name))
    return undefined
  const [value, setValue] = React.useState(target.attributes[name]);
  view.model.data.watch(() => {
    setValue(target.attributes[name])
  }, name);
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

${render_code}`;

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
      esm:       [ String,              "" ],
      importmap: [ Any,                 {} ],
    }))
  }
}
