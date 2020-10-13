import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

import {CachedVariadicBox, set_size} from "./layout"

export class ProgressView extends HTMLBoxView {
  model: Progress
  _prev_sizing_mode: string | null
  protected progressEl: HTMLProgressElement

  connect_signals(): void {
    super.connect_signals()
    const resize = () => {
      this.render()
      this.root.compute_layout() // XXX: invalidate_layout?
    }
    this.connect(this.model.properties.height.change, resize)
    this.connect(this.model.properties.width.change, resize)
    this.connect(this.model.properties.height_policy.change, resize)
    this.connect(this.model.properties.width_policy.change, resize)
    this.connect(this.model.properties.sizing_mode.change, resize)
    this.connect(this.model.properties.active.change, () => this.setCSS())
    this.connect(this.model.properties.bar_color.change, () => this.setCSS())
    this.connect(this.model.properties.css_classes.change, () => this.setCSS())
    this.connect(this.model.properties.value.change, () => this.setValue())
    this.connect(this.model.properties.max.change, () => this.setMax())
  }

  render(): void {
    super.render()
    const style: any = {...this.model.style, display: "inline-block"}
    this.progressEl = document.createElement('progress')
    this.setValue()
    this.setMax()
    set_size(this.progressEl, this.model)

    // Set styling
    this.setCSS()
    for (const prop in style)
      this.progressEl.style.setProperty(prop, style[prop]);
    this.el.appendChild(this.progressEl)
  }

  setCSS(): void {
    let css = this.model.css_classes.join(" ") + " " + this.model.bar_color;
    if (this.model.active)
      css = css + " active";
    this.progressEl.className = css;
  }

  setValue(): void {
    if (this.model.value != null)
      this.progressEl.value = this.model.value
  }

  setMax(): void {
    if (this.model.max != null)
      this.progressEl.max = this.model.max
  }
  
  _update_layout(): void {
    let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
    this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedVariadicBox(this.el, this.model.sizing_mode, changed)
    this.layout.set_sizing(this.box_sizing())
  }
}

export namespace Progress {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    active: p.Property<boolean>
    bar_color: p.Property<string>
    style: p.Property<{[key: string]: string}>
    max: p.Property<number | null>
    value: p.Property<number | null>
  }
}

export interface Progress extends Progress.Attrs {}

export class Progress extends HTMLBox {
  properties: Progress.Props

  constructor(attrs?: Partial<Progress.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static init_Progress(): void {
    this.prototype.default_view = ProgressView
    this.define<Progress.Props>({
      active:    [ p.Boolean, true ],
      bar_color: [ p.String, 'primary' ],
      style:     [ p.Any, {} ],
      max:       [ p.Number, 100 ],
      value:     [ p.Any, null ],
    })
  }
}
