import {Tooltip, TooltipView} from "@bokehjs/models/ui/tooltip"
import { build_view, IterViews} from "@bokehjs/core/build_views"
import * as p from "@bokehjs/core/properties"

import {Button as BkButton, ButtonView as BkButtonView} from "@bokehjs/models/widgets/button"


export class ButtonView extends BkButtonView {
  declare model: Button

  protected tooltip: TooltipView | null

  override *children(): IterViews {
    yield* super.children()
    if (this.tooltip != null)
      yield this.tooltip
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    const {tooltip} = this.model
    if (tooltip != null)
      this.tooltip = await build_view(tooltip, {parent: this})
  }

  override remove(): void {
    this.tooltip?.remove()
    super.remove()
  }

  override render(): void {
    super.render()

    const toggle = (visible: boolean) => {
      this.tooltip?.model.setv({
        visible,
      })
    }
    let timer: number
    this.el.addEventListener("mouseenter", () => {
      timer = setTimeout(() => toggle(true), this.model.tooltip_delay)
    })
    this.el.addEventListener("mouseleave", () => {
      clearTimeout(timer)
      toggle(false)
    })
  }

}

export namespace Button {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkButton.Props & {
    tooltip: p.Property<Tooltip | null>
    tooltip_delay: p.Property<number>
  }
}

export interface Button extends Button.Attrs {}

export class Button extends BkButton {
  declare properties: Button.Props
  declare __view_type__: ButtonView

  static __module__ = "panel.models.widgets"

  constructor(attrs?: Partial<Button.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = ButtonView

    this.define<Button.Props>(({Nullable, Ref, Float}) => ({
      tooltip: [ Nullable(Ref(Tooltip)), null ],
      tooltip_delay: [ Float, 500],
    }))
  }
}
