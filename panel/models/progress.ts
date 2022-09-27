import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

export class ProgressView extends HTMLBoxView {
  model: Progress
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

    // Set styling
    this.setCSS()
    for (const prop in style)
      this.progressEl.style.setProperty(prop, style[prop]);
    this.shadow_el.appendChild(this.progressEl)
  }

  setCSS(): void {
    let css = this.model.css_classes.join(" ") + " " + this.model.bar_color;
    if (this.model.active)
      css = css + " active";
    this.progressEl.className = css;
  }

  setValue(): void {
    if (this.model.value == null)
      this.progressEl.value = 0
    else if (this.model.value >= 0)
      this.progressEl.value = this.model.value
    else if (this.model.value < 0)
      this.progressEl.removeAttribute("value")
    console.log(this.progressEl)
  }

  setMax(): void {
    if (this.model.max != null)
      this.progressEl.max = this.model.max
  }
}

export namespace Progress {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    active: p.Property<boolean>
    bar_color: p.Property<string>
    // style: p.Property<{[key: string]: string}>
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

  static {
    this.prototype.default_view = ProgressView
    this.define<Progress.Props>(({Any, Boolean, Number, String}) => ({
      active:    [ Boolean, true ],
      bar_color: [ String, 'primary' ],
      // style:     [ Any, {} ],
      max:       [ Number, 100 ],
      value:     [ Any, null ],
    }))
  }
}
