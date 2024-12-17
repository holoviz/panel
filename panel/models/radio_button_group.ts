import type {TooltipView} from "@bokehjs/models/ui/tooltip"
import {Tooltip} from "@bokehjs/models/ui/tooltip"
import type {IterViews} from "@bokehjs/core/build_views"
import {build_view} from "@bokehjs/core/build_views"
import type * as p from "@bokehjs/core/properties"

import {
  RadioButtonGroup as bkRadioButtonGroup,
  RadioButtonGroupView as bkRadioButtonGroupView,
} from "@bokehjs/models/widgets/radio_button_group"

export class RadioButtonGroupView extends bkRadioButtonGroupView {
  declare model: RadioButtonGroup

  protected tooltip: TooltipView | null

  override *children(): IterViews {
    yield* super.children()
    if (this.tooltip != null) {
      yield this.tooltip
    }
  }

  override connect_signals(): void {
    super.connect_signals()
    const {tooltip} = this.model.properties
    this.on_change(tooltip, () => this.update_tooltip())
  }

  async update_tooltip(): Promise<void> {
    if (this.tooltip != null) {
      this.tooltip.remove()
    }
    const {tooltip} = this.model
    if (tooltip != null) {
      this.tooltip = await build_view(tooltip, {parent: this})
    }
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    const {tooltip} = this.model
    if (tooltip != null) {
      this.tooltip = await build_view(tooltip, {parent: this})
    }
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
    let timer: ReturnType<typeof setTimeout> | undefined
    this.el.addEventListener("mouseenter", () => {
      timer = setTimeout(() => toggle(true), this.model.tooltip_delay)
    })
    this.el.addEventListener("mouseleave", () => {
      clearTimeout(timer)
      toggle(false)
    })
  }

}

export namespace RadioButtonGroup {
  export type Attrs = p.AttrsOf<Props>

  export type Props = bkRadioButtonGroup.Props & {
    tooltip: p.Property<Tooltip | null>
    tooltip_delay: p.Property<number>
  }
}

export interface RadioButtonGroup extends RadioButtonGroup.Attrs {}

export class RadioButtonGroup extends bkRadioButtonGroup {
  declare properties: RadioButtonGroup.Props
  declare __view_type__: RadioButtonGroupView

  static override __module__ = "panel.models.widgets"

  constructor(attrs?: Partial<RadioButtonGroup.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = RadioButtonGroupView

    this.define<RadioButtonGroup.Props>(({Nullable, Ref, Float}) => ({
      tooltip: [ Nullable(Ref(Tooltip)), null ],
      tooltip_delay: [ Float, 500],
    }))
  }
}
