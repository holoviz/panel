import {Layoutable} from "@bokehjs/core/layout/layoutable"
import {Size, SizeHint, Sizeable} from "@bokehjs/core/layout/types"
import {sized, content_size, extents} from "@bokehjs/core/dom"

import {MarkupView} from "@bokehjs/models/widgets/markup"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

export function set_size(el: HTMLElement, model: HTMLBox): void {
  let width_policy = model.width != null ? "fixed" : "fit"
  let height_policy = model.height != null ? "fixed" : "fit"
  const {sizing_mode} = model
  if (sizing_mode != null) {
    if (sizing_mode == "fixed")
      width_policy = height_policy = "fixed"
    else if (sizing_mode == "stretch_both")
      width_policy = height_policy = "max"
    else if (sizing_mode == "stretch_width")
      width_policy = "max"
    else if (sizing_mode == "stretch_height")
      height_policy = "max"
    else {
      switch (sizing_mode) {
      case "scale_width":
        width_policy = "max"
        height_policy = "min"
        break
      case "scale_height":
        width_policy = "min"
        height_policy = "max"
        break
      case "scale_both":
        width_policy = "max"
        height_policy = "max"
        break
      default:
        throw new Error("unreachable")
      }
    }
  }
  if (width_policy == "fixed" && model.width)
    el.style.width = model.width + "px";
  else if (width_policy == "max")
    el.style.width = "100%";

  if (height_policy == "fixed" && model.height)
    el.style.height = model.height + "px";
  else if (height_policy == "max")
    el.style.height = "100%";
}
  

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
    set_size(this.markup_el, this.model)
  }
}

export class PanelHTMLBoxView extends HTMLBoxView {
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
    set_size(this.el, this.model)
  }
}
