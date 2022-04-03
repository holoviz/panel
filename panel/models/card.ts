import {Column, ColumnView} from "@bokehjs/models/layouts/column"
import {BBox} from "@bokehjs/core/util/bbox"
import * as DOM from "@bokehjs/core/dom"
import {classes, empty} from "@bokehjs/core/dom"
import {Column as ColumnLayout} from "@bokehjs/core/layout/grid"
import * as p from "@bokehjs/core/properties"
import {color2css} from "@bokehjs/core/util/color"

export class CardView extends ColumnView {
  model: Card
  button_el: HTMLButtonElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.collapsed.change, () => this._collapse())
    const {active_header_background, header_background, header_color, hide_header} = this.model.properties
    this.on_change([active_header_background, header_background, header_color, hide_header], () => this.render())
  }

  _update_layout(): void {
    let views: any[]
    if (this.model.hide_header)
      views = this.child_views.slice(1)
    else
      views = this.model.collapsed ? this.child_views.slice(0, 1) : this.child_views
    const items = views.map((child) => child.layout)
    this.layout = new ColumnLayout(items)
    this.layout.rows = this.model.rows
    this.layout.spacing = [this.model.spacing, 0]
    this.layout.set_sizing(this.box_sizing())
  }

  update_position(): void {
    if (this.model.collapsible && !this.model.hide_header) {
      const header = this.child_views[0]
      const obbox = header.layout.bbox
      const ibbox = header.layout.inner_bbox
      if (obbox.x1 != 0) {
	let offset: number
	if (this.model.collapsible) {
	  const icon_style = getComputedStyle(this.button_el.children[0])
	  offset = (parseFloat(icon_style.width) + parseFloat(icon_style.marginLeft)) || 0
        } else {
	  offset = 0
	}
	const outer = new BBox({x0: obbox.x0, x1: obbox.x1-offset, y0: obbox.y0, y1: obbox.y1})
	const inner = new BBox({x0: ibbox.x0, x1: ibbox.x1-offset, y0: ibbox.y0, y1: ibbox.y1})
	header.layout.set_geometry(outer, inner)
      }
    }
    super.update_position()
  }

  render(): void {
    empty(this.el)

    const {background, button_css_classes, header_color, header_tag, header_css_classes} = this.model

    this.el.style.backgroundColor = background != null ? color2css(background) : ""
    classes(this.el).clear().add(...this.css_classes())

    let header_background = this.model.header_background
    if (!this.model.collapsed && this.model.active_header_background)
      header_background = this.model.active_header_background
    const header = this.child_views[0]

    let header_el
    if (this.model.collapsible) {
      this.button_el = DOM.createElement("button", {type: "button", class: header_css_classes})
      const icon = DOM.createElement("div", {class: button_css_classes})
      icon.innerHTML = this.model.collapsed ? "\u25ba" : "\u25bc"
      this.button_el.appendChild(icon)
      this.button_el.style.backgroundColor = header_background != null ? header_background : ""
      header.el.style.backgroundColor = header_background != null ? header_background : ""
      this.button_el.appendChild(header.el)

      this.button_el.onclick = () => this._toggle_button()
      header_el = this.button_el
    } else {
      header_el = DOM.createElement((header_tag as any), {class: header_css_classes})
      header_el.style.backgroundColor = header_background != null ? header_background : ""
      header_el.appendChild(header.el)
    }

    if (!this.model.hide_header) {
      header_el.style.color = header_color != null ? header_color : ""
      this.el.appendChild(header_el)
      header.render()
    }
    for (const child_view of this.child_views.slice(1)) {
      if (!this.model.collapsed)
        this.el.appendChild(child_view.el)
      child_view.render()
    }
  }

  _toggle_button(): void {
    this.model.collapsed = !this.model.collapsed
  }

  _collapse(): void {
    this.invalidate_render()
  }

  protected _createElement(): HTMLElement {
    return DOM.createElement((this.model.tag as any), {class: this.css_classes()})
  }
}

export namespace Card {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Column.Props & {
    active_header_background: p.Property<string | null>
    button_css_classes: p.Property<string[]>
    collapsed: p.Property<boolean>
    collapsible: p.Property<boolean>
    header_background: p.Property<string | null>
    header_color: p.Property<string | null>
    header_css_classes: p.Property<string[]>
    header_tag: p.Property<string>
    hide_header: p.Property<boolean>
    tag: p.Property<string>
  }
}

export interface Card extends Card.Attrs {}

export class Card extends Column {
  properties: Card.Props

  constructor(attrs?: Partial<Card.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.layout"

  static init_Card(): void {
    this.prototype.default_view = CardView

    this.define<Card.Props>(({Array, Boolean, Nullable, String}) => ({
      active_header_background: [ Nullable(String), null ],
      button_css_classes:       [ Array(String),      [] ],
      collapsed:                [ Boolean,          true ],
      collapsible:              [ Boolean,          true ],
      header_background:        [ Nullable(String), null ],
      header_color:             [ Nullable(String), null ],
      header_css_classes:       [ Array(String),      [] ],
      header_tag:               [ String,          "div" ],
      hide_header:              [ Boolean,         false ],
      tag:                      [ String,          "div" ],
    }))
  }
}
