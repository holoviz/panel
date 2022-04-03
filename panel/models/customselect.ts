import { Select, SelectView } from "@bokehjs/models/widgets/selectbox"
import * as p from "@bokehjs/core/properties"


export class CustomSelectView extends SelectView {
  override model: CustomSelect

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.disabled_options.change, () => this._update_disabled_options())
  }

  protected options_el(): HTMLOptionElement[] | HTMLOptGroupElement[] {
    let opts = super.options_el()
    opts.forEach((element) => {
      if (this.model.disabled_options.includes(element.value)) {
        element.setAttribute('disabled', 'true')
      }
  })
    return opts
}

  protected _update_disabled_options(): void {
    for (const element of this.input_el.options) {
      if (this.model.disabled_options.includes(element.value)) {
        element.setAttribute('disabled', 'true')
      } else {
        element.removeAttribute('disabled')
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
  override properties: CustomSelect.Props
  override __view_type__: CustomSelectView

  constructor(attrs?: Partial<CustomSelect.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = CustomSelectView

    this.define<CustomSelect.Props>(({Array, String}) => {
      return {
        disabled_options:   [ Array(String), [] ],
      }
    })
  }
}
