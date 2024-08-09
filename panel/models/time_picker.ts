import {TimePicker as BkTimePicker, TimePickerView as BkTimePickerView} from "@bokehjs/models/widgets/time_picker"
import type * as p from "@bokehjs/core/properties"
import type flatpickr from "flatpickr"

export class TimePickerView extends BkTimePickerView {
  declare model: TimePicker

  private _offset_time(value: string | number): number {
    const baseDate = new Date(value)
    const timeZoneOffset = baseDate.getTimezoneOffset() * 60 * 1000
    return baseDate.getTime() + timeZoneOffset
  }

  private _setDate(date: string | number): void {
    date = this._offset_time(date)
    this.picker.setDate(date)
  }

  protected override get flatpickr_options(): flatpickr.Options.Options {
    // on init
    const options = super.flatpickr_options
    if (options.defaultDate != null) { options.defaultDate = this._offset_time(options.defaultDate as string) }
    return options
  }

  override connect_signals(): void {
    super.connect_signals()

    const {value} = this.model.properties
    this.connect(value.change, () => {
      const {value} = this.model
      if (value != null && typeof value === "number") {
        // we need to handle it when programmatically changed thru Python, e.g.
        // time_picker.value = "4:08" or time_picker.value = "datetime.time(4, 8)"
        // else, when changed in the UI, e.g. by typing in the input field
        // no special handling is needed
        this._setDate(value)
      }
    })
  }

}

export namespace TimePicker {
  export type Attrs = p.AttrsOf<Props>
  export type Props = BkTimePicker.Props & {
  }
}

export interface TimePicker extends TimePicker.Attrs { }

export class TimePicker extends BkTimePicker {
  declare properties: TimePicker.Props

  constructor(attrs?: Partial<TimePicker.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.time_picker"

  static {
    this.prototype.default_view = TimePickerView

    this.define<TimePicker.Props>(({ }) => ({
    }))
  }
}
