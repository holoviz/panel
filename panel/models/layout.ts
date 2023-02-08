import {MarkupView} from "@bokehjs/models/widgets/markup"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import * as p from "@bokehjs/core/properties"

export class PanelMarkupView extends MarkupView {

  render(): void {
    super.render()
    set_size(this.markup_el, this.model)
  }
}

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
  if (model.min_width != null)
    el.style.minWidth = model.min_width + "px";
  if (model.max_width != null)
    el.style.maxWidth = model.max_width + "px";

  if (height_policy == "fixed" && model.height)
    el.style.height = model.height + "px";
  else if (height_policy == "max")
    el.style.height = "100%";
  if (model.min_height != null)
    el.style.minHeight = model.min_height + "px";
  if (model.max_width != null)
    el.style.maxHeight = model.max_height + "px";
}

export abstract class HTMLBoxView extends LayoutDOMView {
  override model: HTMLBox

  _prev_css_classes: string[]

  connect_signals(): void {
    super.connect_signals()

    // Note due to on_change hack properties must be defined in this order.
    const {css_classes, stylesheets} = this.model.properties
    this._prev_css_classes = this.model.css_classes
    this.on_change([stylesheets], () => this.invalidate_render())
    this.on_change([css_classes], () => {
      // Note: This ensures that changes in the loading parameter in Panel
      // do NOT trigger a full re-render
      const css = []
      let skip = false
      for (const cls of this.model.css_classes) {
        if (cls === 'pn-loading')
          skip = true
        else if (skip)
          skip = false
        else
          css.push(cls)
      }
      const prev = this._prev_css_classes
      if (JSON.stringify(css) === JSON.stringify(prev))
	this.class_list.clear().add(...this.css_classes())
      else
        this.invalidate_render()
      this._prev_css_classes = css
    })
  }

  on_change(properties: any, fn: () => void): void {
    // HACKALERT: LayoutDOMView triggers re-renders whenever css_classes change
    // which is very expensive so we do not connect this signal and handle it
    // ourself
    const p = this.model.properties
    if (properties.length === 2 && properties[0] === p.css_classes && properties[1] === p.stylesheets) {
      return
    }
    super.on_change(properties, fn)
  }

  get child_models(): LayoutDOM[] {
    return []
  }
}

export namespace HTMLBox {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props
}

export interface HTMLBox extends HTMLBox.Attrs {}

export abstract class HTMLBox extends LayoutDOM {
  override properties: HTMLBox.Props

  constructor(attrs?: Partial<HTMLBox.Attrs>) {
    super(attrs)
  }
}
