import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView} from "./layout"

const Jupyter = (window as any).Jupyter

export class IPyWidgetView extends PanelHTMLBoxView {
  model: IPyWidget
  private rendered: boolean = false
  private ipyview: any

  render(): void {
    super.render()
    this._render().then(() => {
      this.rendered = true
      this.invalidate_layout()
      this.notify_finished()
    })
  }

  has_finished(): boolean {
    return this.rendered && super.has_finished()
  }

  async _render(): Promise<void> {
    const {spec, state} = this.model.bundle
    let manager: any
    if ((Jupyter != null) && (Jupyter.notebook != null))
      manager = Jupyter.notebook.kernel.widget_manager
    else if ((window as any).PyViz.widget_manager != null)
      manager = (window as any).PyViz.widget_manager
    if (!manager) {
      console.log("Panel IPyWidget model could not find a WidgetManager")
      return
    }

    if (this.ipyview == null) {
      const models = await manager.set_state(state)
      const model = models.find((item: any) => item.model_id == spec.model_id)
      if (model != null) {
        const view = await manager.create_view(model, {el: this.el})
        this.ipyview = view
        if (view.children_views) {
          for (const child of view.children_views.views)
            await child
        }
        this.el.appendChild(view.el)
        view.trigger('displayed', view)
      }
    } else
      this.el.appendChild(this.ipyview.el)
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
