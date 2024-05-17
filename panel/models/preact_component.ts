import {html} from "htm/preact"
import {render} from "preact"

import type * as p from "@bokehjs/core/properties"

import {ReactiveESM, ReactiveESMView} from "./reactive_esm"

function extractDataAttributes(text: string) {
  const regex = /\bdata\.([a-zA-Z_][a-zA-Z0-9_]*)\b/g
  const ignored = ["send_event", "watch"]
  const matches = []
  let match, attr

  while ((match = regex.exec(text)) !== null && (attr = match[0].slice(5)) !== null && !ignored.includes(attr)) {
    matches.push(attr)
  }

  return matches
}

export class PreactComponentView extends ReactiveESMView {
  declare model: PreactComponent
  // @ts-ignore
  private _htm = html
  // @ts-ignore
  private _render_htm = render

  protected override _render_esm(): void {
    if (this.rendered === null) {
      return
    }
    this._rerender_vars = extractDataAttributes(this.rendered)

    this.disconnect_watchers()
    if (this.model.importmap) {
      const importMap = {...this.model.importmap}
      // @ts-ignore
      importShim.addImportMap(importMap)
    }

    const code = `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

const children = {}
for (const child of view.model.children) {
  const child_model = view.model.data[child]
  if (Array.isArray(child_model)) {
    const subchildren = children[child] = []
    for (const subchild of child_model) {
      subchildren.push(view._child_views.get(subchild).el)
    }
  } else {
    children[child] = view._child_views.get(child_model).el
  }
}

${this.rendered}

const output = render({view: view, model: view.model, data: view.model.data, el: view.container, children, html: view._htm})

view._render_htm(output, view.container)
view.model.data.watch(() => view._render_esm(), view._rerender_vars)

view.render_children();`

    const url = URL.createObjectURL(
      new Blob([code], {type: "text/javascript"}),
    )
    // @ts-ignore
    importShim(url)
  }
}

export namespace PreactComponent {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ReactiveESM.Props
}

export interface PreactComponent extends ReactiveESM.Attrs {}

export class PreactComponent extends ReactiveESM {
  declare properties: PreactComponent.Props

  constructor(attrs?: Partial<PreactComponent.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.esm"

  static {
    this.prototype.default_view = PreactComponentView
  }
}
