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
    const elements = opts.flatMap((element) => element instanceof HTMLOptGroupElement
      ? Array.from(element.querySelectorAll("option")) : [element])
    this._set_disabled_options(elements)
    return opts
  }

  protected _update_disabled_options(): void {
    this._set_disabled_options(Array.from(this.input_el.options))
  }

  private _set_disabled_options(elements: HTMLOptionElement[]): void {
    const {options, disabled_options} = this.model
    const values = Array.isArray(options) ? options : Object.values(options).flat()
    elements.forEach((element, index) => {
      const option = values[index]
      if (option === undefined) {
        return
      }
      const value = typeof option === "string" ? option : option[0]
      element.disabled = disabled_options.includes(String(value))
    })
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
