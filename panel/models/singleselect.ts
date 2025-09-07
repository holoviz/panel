import {select, option} from "@bokehjs/core/dom"
import {isString} from "@bokehjs/core/util/types"
import type * as p from "@bokehjs/core/properties"

import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"
import * as inputs from "@bokehjs/styles/widgets/inputs.css"

export class SingleSelectView extends InputWidgetView {
  declare model: SingleSelect

  declare input_el: HTMLSelectElement

  override connect_signals(): void {
    super.connect_signals()

    const {value, options, disabled_options, size, disabled} = this.model.properties
    this.on_change(value, () => this.render_selection())
    this.on_change(options, () => this.rerender_())
    this.on_change(disabled_options, () => this.rerender_())
    this.on_change(size, () => this.rerender_())
    this.on_change(disabled, () => this.rerender_())
  }

  override render(): void {
    super.render()
    this.render_selection()
  }

  rerender_(): void {
    // Can be removed when Bokeh>3.7 (see https://github.com/holoviz/panel/pull/7815)
    if (this.rerender) {
      this.rerender()
    } else {
      this.render()
      this.r_after_render()
    }
  }

  _render_input(): HTMLElement {
    const options = this.model.options.map((opt) => {
      let value, _label
      if (isString(opt)) {
        value = _label  = opt
      } else {
        [value, _label] = opt
      }

      const disabled = this.model.disabled_options.includes(value)

      return option({value, disabled}, _label)
    })

    this.input_el = select({
      multiple: false,
      class: inputs.input,
      name: this.model.name,
      disabled: this.model.disabled,
    }, options)
    this.input_el.style.backgroundImage = "none"

    this.input_el.addEventListener("change", () => this.change_input())
    return this.input_el
  }

  render_selection(): void {
    const selected = this.model.value

    for (const el of this.input_el.querySelectorAll("option")) {
      if (el.value === selected) {
        el.selected = true
      }
    }

    // Note that some browser implementations might not reduce
    // the number of visible options for size <= 3.
    this.input_el.size = this.model.size
  }

  override change_input(): void {
    const is_focused = this.el.querySelector("select:focus") != null

    let value = null
    for (const el of this.shadow_el.querySelectorAll("option")) {
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
    if (is_focused) {
      this.input_el.focus()
    }
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
  declare properties: SingleSelect.Props
  declare __view_type__: SingleSelectView

  constructor(attrs?: Partial<SingleSelect.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = SingleSelectView

    this.define<SingleSelect.Props>(({Any, List, Int, Nullable, Str}) => ({
      disabled_options: [ List(Str), [] ],
      options:          [ List(Any), []    ],
      size:             [ Int,         4    ], // 4 is the HTML default
      value:            [ Nullable(Str),     null ],
    }))
  }
}
