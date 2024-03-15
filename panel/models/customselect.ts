import {Select, SelectView} from "@bokehjs/models/widgets/select"
import type * as p from "@bokehjs/core/properties"

export class CustomSelectView extends SelectView {
  declare model: CustomSelect

  override connect_signals(): void {
    super.connect_signals()

    const {disabled_options} = this.model.properties
    this.on_change(disabled_options, () => this._update_disabled_options())
  }

  protected override options_el(): HTMLOptionElement[] | HTMLOptGroupElement[] {
    const opts = super.options_el()
    const {disabled_options} = this.model
    opts.forEach((element) => {
      // XXX: what about HTMLOptGroupElement?
      if (element instanceof HTMLOptionElement && disabled_options.includes(element.value)) {
        element.setAttribute("disabled", "true")
      }
    })
    return opts
  }

  protected _update_disabled_options(): void {
    for (const element of this.input_el.options) {
      if (this.model.disabled_options.includes(element.value)) {
        element.setAttribute("disabled", "true")
      } else {
        element.removeAttribute("disabled")
      }
    }
  }
}

export namespace CustomSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Select.Props & {
    disabled_options: p.Property<string[]>
  }
}

export interface CustomSelect extends CustomSelect.Attrs {}

export class CustomSelect extends Select {
  declare properties: CustomSelect.Props
  declare __view_type__: CustomSelectView

  constructor(attrs?: Partial<CustomSelect.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = CustomSelectView

    this.define<CustomSelect.Props>(({List, Str}) => {
      return {
        disabled_options:   [ List(Str), [] ],
      }
    })
  }
}
