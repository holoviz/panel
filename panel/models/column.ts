import {Column as BokehColumn, ColumnView as BokehColumnView} from "@bokehjs/models/layouts/column"
import {CachedColumn as CachedColumnLayout} from "./layout"

export class ColumnView extends BokehColumnView {
  _prev_sizing_mode: string | null
  
  _update_layout(): void {
	
    const items = this.child_views.map((child) => child.layout)
	let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
    this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedColumnLayout(items, this.model.sizing_mode, changed)
    this.layout.rows = this.model.rows
    this.layout.spacing = [this.model.spacing, 0]
    this.layout.set_sizing(this.box_sizing())
  }
}

export class Column extends BokehColumn {
  static __module__ = "panel.models.layout"
}
