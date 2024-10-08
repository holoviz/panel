// adapted from bokeh
// https://github.com/bokeh/bokeh/blob/branch-3.7/bokehjs/src/lib/models/widgets/sliders/date_slider.ts

import tz from "timezone"

import type {SliderSpec} from "@bokehjs/models/widgets/sliders/abstract_slider"
import {NumericalSlider, NumericalSliderView} from "@bokehjs/models/widgets/sliders/numerical_slider"
import type {TickFormatter} from "@bokehjs/models/formatters/tick_formatter"
import type * as p from "@bokehjs/core/properties"
import {isString} from "@bokehjs/core/util/types"

export class DatetimeSliderView extends NumericalSliderView {
  declare model: DatetimeSlider

  override behaviour = "tap" as const
  override connected = [true, false]

  protected _formatter(value: number, format: string | TickFormatter): string {
    console.log("DatetimeSlider")
    if (isString(format)) {
      return tz(value, format)
    } else {
      return format.compute(value)
    }
  }
}

export namespace DatetimeSlider {
  export type Attrs = p.AttrsOf<Props>
  export type Props = NumericalSlider.Props
}

export interface DatetimeSlider extends DatetimeSlider.Attrs {}

export class DatetimeSlider extends NumericalSlider {
  declare properties: DatetimeSlider.Props
  declare __view_type__: DatetimeSliderView

  constructor(attrs?: Partial<DatetimeSlider.Attrs>) {
    super(attrs)
  }
  static override __module__ = "panel.models.datetime_slider"

  static {
    this.prototype.default_view = DatetimeSliderView

    this.override<DatetimeSlider.Props>({
      format: "%d %b %Y %H:%M:%S",
    })
  }
}