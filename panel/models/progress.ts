import {StyleSheetLike, ImportedStyleSheet} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

export class ProgressView extends HTMLBoxView {
  model: Progress
  protected progressEl: HTMLProgressElement

  connect_signals(): void {
    super.connect_signals()
    const render = () => this.render()
    this.connect(this.model.properties.height.change, render)
    this.connect(this.model.properties.width.change, render)
    this.connect(this.model.properties.height_policy.change, render)
    this.connect(this.model.properties.width_policy.change, render)
    this.connect(this.model.properties.sizing_mode.change, render)
    this.connect(this.model.properties.active.change, () => this.setCSS())
    this.connect(this.model.properties.bar_color.change, () => this.setCSS())
    this.connect(this.model.properties.css_classes.change, () => this.setCSS())
    this.connect(this.model.properties.value.change, () => this.setValue())
    this.connect(this.model.properties.max.change, () => this.setMax())
  }

  render(): void {
    super.render()
    const style: any = {...this.model.styles, display: "inline-block"}
    this.progressEl = document.createElement('progress')
    this.setValue()
    this.setMax()

    // Set styling
    this.setCSS()
    for (const prop in style)
      this.progressEl.style.setProperty(prop, style[prop]);
    this.shadow_el.appendChild(this.progressEl)
  }

  override stylesheets(): StyleSheetLike[] {
    const styles = super.stylesheets()
    for (const css of this.model.css)
      styles.push(new ImportedStyleSheet(css))
    return styles
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
    css: p.Property<string[]>
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
    this.define<Progress.Props>(({Any, Array, Boolean, Number, String}) => ({
      active:    [ Boolean, true ],
      bar_color: [ String, 'primary' ],
      css:       [ Array(String), [] ],
      max:       [ Number, 100 ],
      value:     [ Any, null ],
    }))
  }
}
