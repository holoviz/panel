import type {StyleSheetLike} from "@bokehjs/core/dom"
import {InlineStyleSheet} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"

import {HTMLBox, HTMLBoxView} from "./layout"

const Jupyter = (window as any).Jupyter

export class IPyWidgetView extends HTMLBoxView {
  declare model: IPyWidget

  private ipyview: any
  private ipychildren: any[]
  private manager: any

  override initialize(): void {
    super.initialize()
    let manager: any
    if ((Jupyter != null) && (Jupyter.notebook != null)) {
      manager = Jupyter.notebook.kernel.widget_manager
    } else if ((window as any).PyViz.widget_manager != null) {
      manager = (window as any).PyViz.widget_manager
    } else {
      console.warn("Panel IPyWidget model could not find a WidgetManager")
      return
    }
    this.manager = manager
    this.ipychildren = []
  }

  override remove(): void {
    this.ipyview.remove()
    super.remove()
  }

  protected _ipy_stylesheets(): StyleSheetLike[] {
    const stylesheets: StyleSheetLike[] = []

    for (const child of document.head.children) {
      if (child instanceof HTMLStyleElement) {
        const raw_css = child.textContent
        if (raw_css != null) {
          const css = raw_css.replace(/:root/g, ":host")
          stylesheets.push(new InlineStyleSheet(css))
        }
      }
    }

    return stylesheets
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), ...this._ipy_stylesheets()]
  }

  override render(): void {
    super.render()
    const {spec, state} = this.model.bundle
    this.manager.set_state(state).then(async (models: any) => {
      const model = models.find((item: any) => item.model_id == spec.model_id)
      if (model == null) {
        return
      }

      const view = await this.manager.create_view(model, {el: this.el})
      this.ipyview = view
      this.ipychildren = []
      if (view.children_views) {
        for (const child of view.children_views.views) {
          this.ipychildren.push(await child)
        }
      }
      this.shadow_el.appendChild(this.ipyview.el)
      this.ipyview.trigger("displayed", this.ipyview)
      for (const child of this.ipychildren) {
        child.trigger("displayed", child)
      }
      this.invalidate_layout()
    })
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
  declare properties: IPyWidget.Props

  constructor(attrs?: Partial<IPyWidget.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.ipywidget"

  static {
    this.prototype.default_view = IPyWidgetView

    this.define<IPyWidget.Props>(({Any}) => ({
      bundle: [ Any, {} ],
    }))
  }
}
