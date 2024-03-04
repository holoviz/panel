import {ClickableIcon, ClickableIconView} from "./icon"
import type * as p from "@bokehjs/core/properties"

export class ButtonIconView extends ClickableIconView {
  declare model: ButtonIcon

  _click_listener: any

  public override *controls() {}

  override update_cursor(): void {
    this.icon_view.el.style.cursor = this.model.disabled ? "default" : "pointer"
  }

  override click(): void {
    if (this.model.disabled) {
      return
    }
    super.click()
    const updateState = (value: boolean, disabled: boolean) => {
      this.model.value = value
      this.model.disabled = disabled
    }
    updateState(true, true)
    new Promise(resolve => setTimeout(resolve, this.model.toggle_duration))
      .then(() => {
        updateState(false, false)
      })
  }
}

export namespace ButtonIcon {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ClickableIcon.Props & {
    toggle_duration: p.Property<number>
  }
}

export interface ButtonIcon extends ButtonIcon.Attrs { }

export class ButtonIcon extends ClickableIcon {
  declare properties: ButtonIcon.Props
  declare __view_type__: ButtonIconView
  static override __module__ = "panel.models.icon"

  constructor(attrs?: Partial<ButtonIcon.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = ButtonIconView

    this.define<ButtonIcon.Props>(({Int}) => ({
      toggle_duration: [Int, 75],
    }))
  }
}
