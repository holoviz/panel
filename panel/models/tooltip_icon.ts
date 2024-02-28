import {Tooltip} from "@bokehjs/models/ui/tooltip"
import type {UIElement} from "@bokehjs/models/ui/ui_element"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"

import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div, label} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"

import inputs_css, * as inputs from "@bokehjs/styles/widgets/inputs.css"
import icons_css from "@bokehjs/styles/icons.css"

export class TooltipIconView extends LayoutDOMView {
  declare model: TooltipIcon

  protected desc_el: HTMLElement

  get child_models(): UIElement[] {
    if (this.model.description == null) {
      return []
    }
    return [this.model.description]
  }

  override connect_signals(): void {
    super.connect_signals()
    const {description} = this.model.properties
    this.on_change(description, () => this.update_children())
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), inputs_css, icons_css]
  }

  override render(): void {
    super.render()

    const icon_el = div({class: inputs.icon})
    this.desc_el = div({class: inputs.description}, icon_el)

    this.model.description.target = this.desc_el

    let persistent = false

    const toggle = (visible: boolean) => {
      this.model.description.setv({
        visible,
        closable: persistent,
      })
      icon_el.classList.toggle(inputs.opaque, visible && persistent)
    }

    this.on_change(this.model.description.properties.visible, () => {
      const {visible} = this.model.description
      if (!visible) {
        persistent = false
      }
      toggle(visible)
    })
    this.desc_el.addEventListener("mouseenter", () => {
      toggle(true)
    })
    this.desc_el.addEventListener("mouseleave", () => {
      if (!persistent) {
        toggle(false)
      }
    })
    document.addEventListener("mousedown", (event) => {
      const path = event.composedPath()
      const tooltip_view = this._child_views.get(this.model.description)
      if (tooltip_view !== undefined && path.includes(tooltip_view.el)) {
        return
      } else if (path.includes(this.desc_el)) {
        persistent = !persistent
        toggle(persistent)
      } else {
        persistent = false
        toggle(false)
      }
    })
    window.addEventListener("blur", () => {
      persistent = false
      toggle(false)
    })

    // Label to get highlight when icon is hovered
    this.shadow_el.appendChild(label(this.desc_el))
  }
}

export namespace TooltipIcon {
  export type Attrs = p.AttrsOf<Props>

  export type Props = LayoutDOM.Props & {
    description: p.Property<Tooltip>
  }
}

export interface TooltipIcon extends TooltipIcon.Attrs {}

export class TooltipIcon extends LayoutDOM {
  declare properties: TooltipIcon.Props
  declare __view_type__: TooltipIconView
  static override __module__ = "panel.models.widgets"

  constructor(attrs?: Partial<TooltipIcon.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = TooltipIconView

    this.define<TooltipIcon.Props>(({Ref}) => ({
      description: [Ref(Tooltip), new Tooltip()],
    }))
  }
}
