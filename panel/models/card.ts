import {Column, ColumnView} from "./column"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import * as DOM from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"

import card_css from "styles/models/card.css"

const CHEVRON_RIGHT = `
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-right"><path stroke="none" d="M0 0h12v12H0z" fill="none"/><path d="M9 6l6 6l-6 6" /></svg>
`

const CHEVRON_DOWN = `
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-down"><path stroke="none" d="M0 0h12v12H0z" fill="none"/><path d="M6 9l6 6l6 -6" /></svg>
`

export class CardView extends ColumnView {
  declare model: Card

  button_el: HTMLButtonElement
  header_el: HTMLElement

  readonly collapsed_style = new DOM.InlineStyleSheet()

  override connect_signals(): void {
    super.connect_signals()

    const {active_header_background, collapsed, header_background, header_color, hide_header} = this.model.properties
    this.on_change(collapsed, () => this._collapse())
    this.on_change([header_color, hide_header], () => this.render())

    this.on_change([active_header_background, collapsed, header_background], () => {
      const header_background = this.header_background
      if (header_background == null) {
        return
      }
      this.child_views[0].el.style.backgroundColor = header_background
      this.header_el.style.backgroundColor = header_background
    })
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), card_css]
  }

  protected override *_stylesheets(): Iterable<DOM.StyleSheet> {
    yield* super._stylesheets()
    yield this.collapsed_style
  }

  get header_background(): string | null {
    let header_background = this.model.header_background
    if (!this.model.collapsed && this.model.active_header_background) {
      header_background = this.model.active_header_background
    }
    return header_background
  }

  override render(): void {
    this.empty()

    if (this.model.collapsed) {
      this.collapsed_style.replace(":host", {
        height: "fit-content",
        flex: "none",
      })
    }

    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this.class_list.add(...this.css_classes())

    const {button_css_classes, header_color, header_tag, header_css_classes} = this.model

    const header_background = this.header_background
    const header = this.child_views[0]

    let header_el
    if (this.model.collapsible) {
      this.button_el = DOM.button({class: header_css_classes})
      const icon = DOM.div({class: button_css_classes})
      icon.innerHTML = this.model.collapsed ? CHEVRON_RIGHT : CHEVRON_DOWN
      this.button_el.appendChild(icon)
      this.button_el.style.backgroundColor = header_background != null ? header_background : ""
      header.el.style.backgroundColor = header_background != null ? header_background : ""
      this.button_el.appendChild(header.el)
      this.button_el.addEventListener("click", (e: MouseEvent) => this._toggle_button(e))
      header_el = this.button_el
    } else {
      header_el = DOM.create_element((header_tag as any), {class: header_css_classes})
      header_el.style.backgroundColor = header_background != null ? header_background : ""
      header_el.appendChild(header.el)
    }
    this.header_el = header_el

    if (!this.model.hide_header) {
      header_el.style.color = header_color != null ? header_color : ""
      this.shadow_el.appendChild(header_el)
      header.render()
      header.after_render()
    }

    if (this.model.collapsed) {
      return
    }

    for (const child_view of this.child_views.slice(1)) {
      this.shadow_el.appendChild(child_view.el)
      child_view.render()
      child_view.after_render()
    }
  }

  override async update_children(): Promise<void> {
    await this.build_child_views()
    this.render()
    this.invalidate_layout()
  }

  _toggle_button(e: MouseEvent): void {
    for (const path of e.composedPath()) {
      if (path instanceof HTMLInputElement) {
        return
      }
    }
    this.model.collapsed = !this.model.collapsed
  }

  _collapse(): void {
    for (const child_view of this.child_views.slice(1)) {
      if (this.model.collapsed) {
        this.shadow_el.removeChild(child_view.el)
        child_view.model.visible = false
      } else {
        child_view.render()
        child_view.after_render()
        this.shadow_el.appendChild(child_view.el)
        child_view.model.visible = true
      }
    }
    if (this.model.collapsed) {
      this.collapsed_style.replace(":host", {
        height: "fit-content",
        flex: "none",
      })
    } else {
      this.collapsed_style.clear()
    }
    this.button_el.children[0].innerHTML = this.model.collapsed ? CHEVRON_RIGHT : CHEVRON_DOWN
    this.invalidate_layout()
  }

  protected override _create_element(): HTMLElement {
    return DOM.create_element((this.model.tag as any), {class: this.css_classes()})
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
  declare properties: Card.Props

  constructor(attrs?: Partial<Card.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.layout"

  static {
    this.prototype.default_view = CardView

    this.define<Card.Props>(({List, Bool, Nullable, Str}) => ({
      active_header_background: [ Nullable(Str), null ],
      button_css_classes:       [ List(Str),      [] ],
      collapsed:                [ Bool,          true ],
      collapsible:              [ Bool,          true ],
      header_background:        [ Nullable(Str), null ],
      header_color:             [ Nullable(Str), null ],
      header_css_classes:       [ List(Str),      [] ],
      header_tag:               [ Str,          "div" ],
      hide_header:              [ Bool,         false ],
      tag:                      [ Str,          "div" ],
    }))
  }
}
