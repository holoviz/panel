import {select, option} from "@bokehjs/core/dom"
import {isString} from "@bokehjs/core/util/types"
import * as p from "@bokehjs/core/properties"

import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"
import * as inputs from "@bokehjs/styles/widgets/inputs.css"

export class SingleSelectView extends InputWidgetView {
  model: SingleSelect

  declare input_el: HTMLSelectElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.value.change, () => this.render_selection())
    this.connect(this.model.properties.options.change, () => this.render())
    this.connect(this.model.properties.disabled_options.change, () => this.render())
    this.connect(this.model.properties.size.change, () => this.render())
    this.connect(this.model.properties.disabled.change, () => this.render())
  }

  render(): void {
    super.render()

    const options = this.model.options.map((opt) => {
      let value, _label
      if (isString(opt))
        value = _label  = opt
      else
        [value, _label] = opt

      let disabled = this.model.disabled_options.includes(value)

      return option({value: value, disabled: disabled}, _label)
    })

    this.input_el = select({
      multiple: false,
      class: inputs.input,
      name: this.model.name,
      disabled: this.model.disabled,
    }, options)
    this.input_el.style.backgroundImage = 'none';

    this.input_el.addEventListener("change", () => this.change_input())
    this.group_el.appendChild(this.input_el)

    this.render_selection()
  }

  render_selection(): void {
    const selected = this.model.value

    for (const el of this.el.querySelectorAll('option'))
      if (el.value === selected)
        el.selected = true

    // Note that some browser implementations might not reduce
    // the number of visible options for size <= 3.
    this.input_el.size = this.model.size
  }

  change_input(): void {
    const is_focused = this.el.querySelector('select:focus') != null

    let value = null
    for (const el of this.shadow_el.querySelectorAll('option')) {
      if (el.selected) {
        value = el.value
        break
      }
    }

    this.model.value = value
    super.change_input()
    // Restore focus back to the <select> afterwards,
    // so that even if python on_change callback is invoked,
    // focus remains on <select> and one can seamlessly scroll
    // up/down.
    if (is_focused)
      this.input_el.focus()
  }
}

export namespace SingleSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    disabled_options: p.Property<string[]>
    options: p.Property<(string | [string, string])[]>
    size: p.Property<number>
    value: p.Property<string|null>
  }
}

export interface SingleSelect extends SingleSelect.Attrs {}

export class SingleSelect extends InputWidget {
  properties: SingleSelect.Props
  __view_type__: SingleSelectView

  constructor(attrs?: Partial<SingleSelect.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = SingleSelectView

    this.define<SingleSelect.Props>(({Any, Array, Int, Nullable, String}) => ({
      disabled_options: [ Array(String), [] ],
      options:          [ Array(Any), []    ],
      size:             [ Int,         4    ], // 4 is the HTML default
      value:            [ Nullable(String),     null ],
    }))
  }
}
