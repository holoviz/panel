import { Control, ControlView } from '@bokehjs/models/widgets/control'
import { Tooltip, TooltipView } from '@bokehjs/models/ui/tooltip'

import { assert } from '@bokehjs/core/util/assert'
import { isString } from '@bokehjs/core/util/types'
import { build_view, IterViews } from '@bokehjs/core/build_views'
import { div, label, StyleSheetLike } from '@bokehjs/core/dom'
import * as p from '@bokehjs/core/properties'

import inputs_css, * as inputs from '@bokehjs/styles/widgets/inputs.css'
import icons_css from '@bokehjs/styles/icons.css'

export class DescriptionView extends ControlView {
  declare model: Description

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
    if (description instanceof Tooltip) {
      this.description = await build_view(description, { parent: this })
    }
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

    const { description } = this.model

    const icon_el = div({ class: inputs.icon })
    this.desc_el = div({ class: inputs.description }, icon_el)

    if (isString(description)) this.desc_el.title = description
    else {
      const { description } = this
      assert(description != null)

      const { desc_el } = this
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
    }

    // Label to get highlight when icon is hovered
    this.shadow_el.appendChild(label(this.desc_el))
  }

  change_input(): void {}
}

export namespace Description {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Control.Props & {
    description: p.Property<string | Tooltip>
  }
}

export interface Description extends Description.Attrs {}

export class Description extends Control {
  declare properties: Description.Props
  declare __view_type__: DescriptionView
  static __module__ = 'panel.models.widgets'

  constructor(attrs?: Partial<Description.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = DescriptionView

    this.define<Description.Props>(({ String, Or, Ref }) => ({
      description: [Or(String, Ref(Tooltip)), ''],
    }))
  }
}
