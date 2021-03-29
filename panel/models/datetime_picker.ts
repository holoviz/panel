import flatpickr from "flatpickr"

import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"
import {input} from "@bokehjs/core/dom"
import {CalendarPosition} from "@bokehjs/core/enums"
import * as p from "@bokehjs/core/properties"
import {isString} from "@bokehjs/core/util/types"

import * as inputs from "@bokehjs/styles/widgets/inputs.css"
import flatpickr_css from "@bokehjs/styles/widgets/flatpickr.css"


type DateStr = string
type DatesList = (DateStr | [DateStr, DateStr])[]

function _convert_date_list(value: DatesList): flatpickr.Options.DateLimit[] {
  const result: flatpickr.Options.DateLimit[] = []
  for (const item of value) {
    if (isString(item))
      result.push(item)
    else {
      const [from, to] = item
      result.push({from, to})
    }
  }
  return result
}

export class DatetimePickerView extends InputWidgetView {
  model: DatetimePicker

  private _picker: flatpickr.Instance

  connect_signals(): void {
    super.connect_signals()

    const {value, min_date, max_date, disabled_dates, enabled_dates, position, inline,
      enable_time, enable_seconds, military_time, date_format, mode} = this.model.properties
    this.connect(value.change, () => this._picker?.setDate(this.model.value))
    this.connect(min_date.change, () => this._picker?.set("minDate", this.model.min_date))
    this.connect(max_date.change, () => this._picker?.set("maxDate", this.model.max_date))
    this.connect(disabled_dates.change, () => this._picker?.set("disable", this.model.disabled_dates))
    this.connect(enabled_dates.change, () => this._picker?.set("enable", this.model.enabled_dates))
    this.connect(position.change, () => this._picker?.set("position", this.model.position))
    this.connect(inline.change, () => this._picker?.set("inline", this.model.inline))
    this.connect(enable_time.change, () => this._picker?.set("enableTime", this.model.enable_time))
    this.connect(enable_seconds.change, () => this._picker?.set("enableSeconds", this.model.enable_seconds))
    this.connect(military_time.change, () => this._picker?.set("time_24hr", this.model.military_time))
    this.connect(mode.change, () => this._picker?.set("mode", this.model.mode))
    this.connect(date_format.change, () => this._picker?.set("dateFormat", this.model.date_format))
  }

  remove(): void {
    this._picker?.destroy()
    super.remove()
  }

  styles(): string[] {
    return [...super.styles(), flatpickr_css]
  }

  render(): void {
    if (this._picker != null)
      return

    super.render()

    this.input_el = input({type: "text", class: inputs.input, disabled: this.model.disabled})
    this.group_el.appendChild(this.input_el)
    this._picker = flatpickr(this.input_el, {
      defaultDate: this.model.value,
      minDate: this.model.min_date ?? undefined,
      maxDate: this.model.max_date ?? undefined,
      inline: this.model.inline,
      position: this.model.position,
      disable: _convert_date_list(this.model.disabled_dates),
      enable: _convert_date_list(this.model.enabled_dates),
      enableTime: this.model.enable_time,
      enableSeconds: this.model.enable_seconds,
      time_24hr: this.model.military_time,
      dateFormat: this.model.date_format,
      mode: this.model.mode,
      onClose: (selected_dates, date_string, instance) => this._on_close(selected_dates, date_string, instance),
    })
  }

  protected _on_close(_selected_dates: Date[], date_string: string, _instance: flatpickr.Instance): void {
    if (this.model.mode == "range" && !date_string.includes("to"))
      return
    this.model.value = date_string
    this.change_input()
  }
}

export namespace DatetimePicker {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    value:          p.Property<string>
    min_date:       p.Property<string | null>
    max_date:       p.Property<string | null>
    disabled_dates: p.Property<DatesList>
    enabled_dates:  p.Property<DatesList>
    position:       p.Property<CalendarPosition>
    inline:         p.Property<boolean>
    enable_time:    p.Property<boolean>
    enable_seconds: p.Property<boolean>
    military_time:  p.Property<boolean>
    date_format:    p.Property<string>
    mode:           p.Property<any>
  }
}

export interface DatetimePicker extends DatetimePicker.Attrs {}

export class DatetimePicker extends InputWidget {
  properties: DatetimePicker.Props
  __view_type__: DatetimePickerView

  constructor(attrs?: Partial<DatetimePicker.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.datetime_picker"

  static init_DatetimePicker(): void {
    this.prototype.default_view = DatetimePickerView

    this.define<DatetimePicker.Props>(({Boolean, String, Array, Tuple, Or, Nullable}) => {
      const DateStr = String
      const DatesList = Array(Or(DateStr, Tuple(DateStr, DateStr)))
      return {
        value:          [ String ],
        min_date:       [ Nullable(String), null ],
        max_date:       [ Nullable(String), null ],
        disabled_dates: [ DatesList, [] ],
        enabled_dates:  [ DatesList, [] ],
        position:       [ CalendarPosition, "auto" ],
        inline:         [ Boolean, false ],
        enable_time:    [ Boolean, true ],
        enable_seconds: [ Boolean, true ],
        military_time:  [ Boolean, true ],
        date_format:    [ String, "Y-m-d H:i:S" ],
        mode:           [ String, "single" ],
      }
    })
  }
}
