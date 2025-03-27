import type {StyleSheetLike} from "@bokehjs/core/dom"
import {ImportedStyleSheet} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

export class ProgressView extends HTMLBoxView {
  declare model: Progress

  protected progressEl: HTMLProgressElement

  override connect_signals(): void {
    super.connect_signals()

    const {
      width, height, height_policy, width_policy, sizing_mode,
      active, bar_color, css_classes, value, max,
    } = this.model.properties

    this.on_change([width, height, height_policy, width_policy, sizing_mode], () => this.rerender_())
    this.on_change([active, bar_color, css_classes], () => this.setCSS())
    this.on_change(value, () => this.setValue())
    this.on_change(max, () => this.setMax())
  }

  override render(): void {
    super.render()
    const style: any = {...this.model.styles, display: "inline-block"}
    this.progressEl = document.createElement("progress")
    this.setValue()
    this.setMax()

    // Set styling
    this.setCSS()
    for (const prop in style) {
      this.progressEl.style.setProperty(prop, style[prop])
    }
    this.shadow_el.appendChild(this.progressEl)
  }

  override stylesheets(): StyleSheetLike[] {
    const styles = super.stylesheets()
    for (const css of this.model.css) {
      styles.push(new ImportedStyleSheet(css))
    }
    return styles
  }

  setCSS(): void {
    let css = `${this.model.css_classes.join(" ")} ${this.model.bar_color}`
    if (this.model.active) {
      css = `${css} active`
    }
    this.progressEl.className = css
  }

  setValue(): void {
    if (this.model.value == null) {
      this.progressEl.value = 0
    } else if (this.model.value >= 0) {
      this.progressEl.value = this.model.value
    } else if (this.model.value < 0) {
      this.progressEl.removeAttribute("value")
    }
  }

  setMax(): void {
    if (this.model.max != null) {
      this.progressEl.max = this.model.max
    }
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
  declare properties: Progress.Props

  constructor(attrs?: Partial<Progress.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = ProgressView
    this.define<Progress.Props>(({Any, List, Bool, Float, Str}) => ({
      active:    [ Bool, true ],
      bar_color: [ Str, "primary" ],
      css:       [ List(Str), [] ],
      max:       [ Float, 100 ],
      value:     [ Any, null ],
    }))
  }
}
