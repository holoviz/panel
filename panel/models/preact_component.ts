import {html} from "htm/preact"
import {Component, h, render} from "preact"
import type {VNode} from "preact"

import type * as p from "@bokehjs/core/properties"
import type {UIElementView} from "@bokehjs/models/ui/ui_element"

import {ReactiveESM, ReactiveESMView} from "./reactive_esm"

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
      const child = this.props.parent.get_child_view(submodel)
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
  private _render_htm = render

  get_child_component(child: string): VNode<ChildProps> {
    return h(Child, {name: child, parent: this})
  }

  override async lazy_initialize(): Promise<void> {
    // @ts-ignore
    Bokeh.htm = html
    await super.lazy_initialize()
  }

  render_component(component: VNode): void {
    render(component, this.container)
  }

  override compile(): string | null {
    let compiled = super.compile()
    if (compiled === null) {
      return compiled
    }
    compiled = `
const html = Bokeh.htm

${compiled}`
    return compiled
  }

  protected override _render_code(): string {
    const code = `
const view = Bokeh.index.find_one_by_id('${this.model.id}')

const children = {}
for (const child of view.model.children) {
  children[child] = view.get_child_component(child)
}

const props = {view: view, model: view.model_proxy, data: view.model.data, el: view.container, children: children}
const output = view._h(view.render_fn, props)

view.render_component(output)
view.model.data.watch(() => view.render_esm(), view.accessed_properties)`
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
