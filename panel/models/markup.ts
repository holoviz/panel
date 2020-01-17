import {Layoutable} from "@bokehjs/core/layout/layoutable"
import {Size, SizeHint, Sizeable} from "@bokehjs/core/layout/types"
import {sized, content_size, extents} from "@bokehjs/core/dom"

import {MarkupView} from "@bokehjs/models/widgets/markup"

export class CachedVariadicBox extends Layoutable {
  _cache: {[key: string]: Size}
  _cache_count: {[key: string]: number}

  constructor(readonly el: HTMLElement, readonly sizing_mode: string | null, readonly changed: boolean) {
    super()
    this._cache = {};
    this._cache_count = {}
  }

  protected _measure(viewport: Size): SizeHint {
    const key = [viewport.width, viewport.height, this.sizing_mode]
    const key_str = key.toString()
    // If sizing mode is responsive and has changed since last render
	// we have to wait until second rerender to use cached value
    const min_count = (!this.changed || (this.sizing_mode == 'fixed') || (this.sizing_mode == null)) ? 0 : 1;
	console.log(this.changed, min_count, this.sizing_mode)
    if ((key_str in this._cache) && (this._cache_count[key_str] >= min_count)) {
      this._cache_count[key_str] = this._cache_count[key_str] + 1;
      return this._cache[key_str]
    }
    const bounded = new Sizeable(viewport).bounded_to(this.sizing.size)
    const size = sized(this.el, bounded, () => {
      const content = new Sizeable(content_size(this.el))
      const {border, padding} = extents(this.el)
      return content.grow_by(border).grow_by(padding).map(Math.ceil)
    })
    this._cache[key_str] = size;
    this._cache_count[key_str] = 0;
    return size;
  }
}

export class PanelMarkupView extends MarkupView {
  _prev_sizing_mode: string | null

  _update_layout(): void {
    let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
	this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedVariadicBox(this.el, this.model.sizing_mode, changed)
    this.layout.set_sizing(this.box_sizing())
  }

  render(): void {
    super.render()
    if (this.model.sizing_mode == "fixed") {
      if (this.model.width)
        this.markup_el.style.width = this.model.width + "px";
      if (this.model.height)
        this.markup_el.style.height = this.model.height + "px";
    }
    if ((this.model.sizing_mode == "stretch_both") || (this.model.sizing_mode == "stretch_width"))
      this.markup_el.style.width = "100%";
    if ((this.model.sizing_mode == "stretch_both") || (this.model.sizing_mode == "stretch_height"))
      this.markup_el.style.height = "100%";
  }
}
