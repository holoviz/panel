import {html} from "htm/preact"
import {Component, h, render} from "preact"
import type {VNode} from "preact"

import type * as p from "@bokehjs/core/properties"
import type {UIElementView} from "@bokehjs/models/ui/ui_element"

import {ReactiveESM, ReactiveESMView} from "./reactive_esm"
import {find_attributes} from "./util"

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
  private _h = h
  // @ts-ignore
  private _htm = html
  // @ts-ignore
  private _render_htm = render

  get_child_component(child: string): VNode<ChildProps> {
    return h(Child, {name: child, parent: this})
  }

  override compile(): string | null {
    let compiled = super.compile()
    if (compiled === null) {
      return compiled
    }
    compiled = `
const _view = Bokeh.index.find_one_by_id('${this.model.id}')
const html = _view._htm

${compiled}`
    return compiled
  }

  protected override _render_code(): string {
    const rerender_vars = find_attributes(
      this.rendered || "", "data", ["send_event", "watch"],
    )
    const code = `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

const children = {}
for (const child of view.model.children) {
  children[child] = view.get_child_component(child)
}

let render;
if (view.rendered_module.default) {
  render = view.rendered_module.default.render
} else {
  render = view.rendered_module.render
}

const output = view._h(render, {view: view, model: view.model, data: view.model.data, el: view.container, children: children})

view._render_htm(output, view.container)
view.model.data.watch(() => view.render_esm(), ${JSON.stringify(rerender_vars)})`
    return code
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
