import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView} from "./layout"

const Jupyter = (window as any).Jupyter

export class IPyWidgetView extends PanelHTMLBoxView {
  model: IPyWidget
  private rendered: boolean = false
  private ipyview: any
  private ipychildren: any[]
  private manager: any

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    let manager: any
    if ((Jupyter != null) && (Jupyter.notebook != null))
      manager = Jupyter.notebook.kernel.widget_manager
    else if ((window as any).PyViz.widget_manager != null)
      manager = (window as any).PyViz.widget_manager
    else {
      console.warn("Panel IPyWidget model could not find a WidgetManager")
      return
    }
    this.manager = manager
    this.ipychildren = []
    const {spec, state} = this.model.bundle
    const models = await manager.set_state(state)
    const model = models.find((item: any) => item.model_id == spec.model_id)
    if (model != null) {
      const view = await this.manager.create_view(model, {el: this.el})
      this.ipyview = view
      if (view.children_views) {
        for (const child of view.children_views.views)
          this.ipychildren.push(await child)
      }
    }
  }

  render(): void {
    super.render()
    if (this.ipyview != null) {
      this.el.appendChild(this.ipyview.el)
      if (!this.rendered) {
	this.ipyview.trigger('displayed', this.ipyview)
	for (const child of this.ipychildren)
          child.trigger('displayed', child)
      }
    }
    this.rendered = true
  }

  has_finished(): boolean {
    return this.rendered && super.has_finished()
  }
}

export namespace IPyWidget {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    bundle: p.Property<any>
  }
}

export interface IPyWidget extends IPyWidget.Attrs {}

export class IPyWidget extends HTMLBox {
  properties: IPyWidget.Props

  constructor(attrs?: Partial<IPyWidget.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.ipywidget"

  static init_IPyWidget(): void {
    this.prototype.default_view = IPyWidgetView

    this.define<IPyWidget.Props>(({Any}) => ({
      bundle: [ Any, {} ],
    }))
  }
}
