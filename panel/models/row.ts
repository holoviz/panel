import {Row as BokehRow, RowView as BokehRowView} from "@bokehjs/models/layouts/row"
import {CachedRow as CachedRowLayout} from "./layout"

export class RowView extends BokehRowView {
  _prev_sizing_mode: string | null
  
  _update_layout(): void {
	
    const items = this.child_views.map((child) => child.layout)
	let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
    this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedRowLayout(items, this.model.sizing_mode, changed)
    this.layout.cols = this.model.cols
    this.layout.spacing = [this.model.spacing, 0]
    this.layout.set_sizing(this.box_sizing())
  }
}

export class Row extends BokehRow {
  static __module__ = "panel.models.layout"
}
