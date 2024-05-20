import {html} from "htm/preact"
import {Component, h, render} from "preact"
import type {VNode} from "preact"

import type * as p from "@bokehjs/core/properties"
import type {UIElementView} from "@bokehjs/models/ui/ui_element"

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

interface ChildProps {
  name: string
  parent: PreactComponentView
}

class Child extends Component<ChildProps> {

  get views(): UIElementView[] {
    const model = this.props.parent.model.data[this.props.name]
    const models = Array.isArray(model) ? model : [model]
    const views = []
    for (const submodel of models) {
      const child = this.props.parent.get_child(submodel)
      if (child) {
        views.push(child)
      }
    }
    return views
  }

  get elements(): HTMLElement[] {
    return this.views.map(view => view.el)
  }

  override componentDidMount() {
    this.views.map((view) => {
      view.render()
      view.after_render()
    })
    this.props.parent.on_child_render(this.props.name, (new_views: UIElementView[]) => {
      this.forceUpdate()
      this.views.map((view) => {
        if (new_views.includes(view)) {
          view.render()
          view.after_render()
        }
      })
    })
  }

  override render() {
    return h("div", {className: "child-wrapper", ref: (ref) => ref && this.elements.map(el => ref.appendChild(el))})
  }
}

export class PreactComponentView extends ReactiveESMView {
  declare model: PreactComponent
  // @ts-ignore
  private _htm = html
  // @ts-ignore
  private _render_htm = render

  get_child_component(child: string): VNode<ChildProps> {
    return h(Child, {name: child, parent: this})
  }

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
const _view = Bokeh.index.find_one_by_id('${this.model.id}')
const html = _view._htm

const _children = {}
for (const _child of _view.model.children) {
  _children[_child] = _view.get_child_component(_child)
}

${this.rendered}

const output = render({view: _view, model: _view.model, data: _view.model.data, el: _view.container, children: _children, html: html})

_view._render_htm(output, _view.container)
_view.model.data.watch(() => _view._render_esm(), _view._rerender_vars)`

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
