import { Control, ControlView } from '@bokehjs/models/widgets/control'
import { Tooltip, TooltipView } from '@bokehjs/models/ui/tooltip'

import { build_view, IterViews } from '@bokehjs/core/build_views'
import { div, label, StyleSheetLike } from '@bokehjs/core/dom'
import * as p from '@bokehjs/core/properties'

import inputs_css, * as inputs from '@bokehjs/styles/widgets/inputs.css'
import icons_css from '@bokehjs/styles/icons.css'

export class TooltipIconView extends ControlView {
  declare model: TooltipIcon

  protected description: TooltipView

  protected desc_el: HTMLElement

  public *controls() {}

  override *children(): IterViews {
    yield* super.children()
    yield this.description
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()

    const { description } = this.model
    this.description = await build_view(description, { parent: this })
  }

  override remove(): void {
    this.description?.remove()
    super.remove()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), inputs_css, icons_css]
  }

  override render(): void {
    super.render()

    const icon_el = div({ class: inputs.icon })
    this.desc_el = div({ class: inputs.description }, icon_el)

    const { desc_el, description } = this
    description.model.target = desc_el

    let persistent = false

    const toggle = (visible: boolean) => {
      description.model.setv({
        visible,
        closable: persistent,
      })
      icon_el.classList.toggle(inputs.opaque, visible && persistent)
    }

    this.on_change(description.model.properties.visible, () => {
      const { visible } = description.model
      if (!visible) {
        persistent = false
      }
      toggle(visible)
    })
    desc_el.addEventListener('mouseenter', () => {
      toggle(true)
    })
    desc_el.addEventListener('mouseleave', () => {
      if (!persistent) toggle(false)
    })
    document.addEventListener('mousedown', (event) => {
      const path = event.composedPath()
      if (path.includes(description.el)) {
        return
      } else if (path.includes(desc_el)) {
        persistent = !persistent
        toggle(persistent)
      } else {
        persistent = false
        toggle(false)
      }
    })
    window.addEventListener('blur', () => {
      persistent = false
      toggle(false)
    })

    // Label to get highlight when icon is hovered
    this.shadow_el.appendChild(label(this.desc_el))
  }

  change_input(): void {}
}

export namespace TooltipIcon {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Control.Props & {
    description: p.Property<Tooltip>
  }
}

export interface TooltipIcon extends TooltipIcon.Attrs {}

export class TooltipIcon extends Control {
  declare properties: TooltipIcon.Props
  declare __view_type__: TooltipIconView
  static __module__ = 'panel.models.widgets'

  constructor(attrs?: Partial<TooltipIcon.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = TooltipIconView

    this.define<TooltipIcon.Props>(({ Ref }) => ({
      description: [Ref(Tooltip), new Tooltip()],
    }))
  }
}
