import {Column, ColumnView} from "@bokehjs/models/layouts/column"
import * as DOM from "@bokehjs/core/dom"
import {classes, empty} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"

import {Column as ColumnLayout} from "@bokehjs/core/layout/grid"
import {Layoutable} from "@bokehjs/core/layout/layoutable"

import {Size} from "@bokehjs/core/layout/types"


export class CollapseableColumnLayout extends ColumnLayout {
  collapsed: boolean

  constructor(items: Layoutable[], collapsed: boolean = false) {
    super(items)
    this.collapsed = collapsed
  }

  protected _measure_totals(row_heights: number[], col_widths: number[]): Size {
    // Do not count height of collapsed height
    const heights = this.collapsed ? row_heights.slice(0, 1) : row_heights
    const last = heights.length-1
    if (!this.collapsed)
      heights[last] = heights[last] + 5
    return super._measure_totals(heights, col_widths)
  }
}

export class CardView extends ColumnView {
  model: Card
  button_el: HTMLButtonElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.collapsed.change, () => this._collapse())
  }

  _update_layout(): void {
    const items = this.child_views.map((child) => child.layout)
    this.layout = new CollapseableColumnLayout(items, this.model.collapsed)
    this.layout.rows = this.model.rows
    this.layout.spacing = [this.model.spacing, 0]
    this.layout.set_sizing(this.box_sizing())
  }

  render(): void {
    empty(this.el)

    const {background, button_color, header_background, button_css_classes, header_tag, header_css_classes} = this.model

    this.el.style.backgroundColor = background != null ? background : ""
    classes(this.el).clear().add(...this.css_classes())

    const header_el = DOM.createElement((header_tag as any), {class: header_css_classes})
    header_el.style.backgroundColor = header_background != null ? header_background : ""
    const header = this.child_views[0]
    header_el.appendChild(header.el)

    if (this.model.collapsible) {
      this.button_el = DOM.createElement("button", {class: button_css_classes, type: "button"})
      this.button_el.innerHTML = this.model.collapsed ? "+" : "-"
      this.button_el.style.color = button_color != null ? button_color : ""
      this.button_el.onclick = () => this._toggle_button()
      header_el.appendChild(this.button_el)
    }

    this.el.appendChild(header_el)
    header.render()

    for (const child_view of this.child_views.slice(1)) {
      if (!this.model.collapsed)
        this.el.appendChild(child_view.el)
      child_view.render()
    }
  }

  _toggle_button(): void {
    this.model.collapsed = !this.model.collapsed
    this._collapse()
  }

  _collapse(): void {
    this.button_el.innerHTML = this.model.collapsed ? '+': '-'
    this.rebuild()
    this.resize_layout()
  }

  protected _createElement(): HTMLElement {
    return DOM.createElement((this.model.tag as any), {class: this.css_classes()})
  }
}

export namespace Card {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Column.Props & {
    button_color: p.Property<string | null>
    button_css_classes: p.Property<string[]>
    collapsed: p.Property<boolean>
    collapsible: p.Property<boolean>
    header_background: p.Property<string | null>
    header_css_classes: p.Property<string[]>
    header_tag: p.Property<string>
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

    this.define<Card.Props>({
      button_color:       [ p.String,  null  ],
      button_css_classes: [ p.Array,   []    ],
      collapsed:          [ p.Boolean, true  ],
      collapsible:        [ p.Boolean, true  ],
      header_background:  [ p.String,  null  ],
      header_css_classes: [ p.Array,   []    ],
      header_tag:         [ p.String,  "div" ],
      tag:                [ p.String,  "div" ],
    })
  }
}
