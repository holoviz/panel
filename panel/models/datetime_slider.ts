// adapted from bokeh
// https://github.com/bokeh/bokeh/blob/branch-3.7/bokehjs/src/lib/models/widgets/sliders/date_slider.ts

import {DEFAULT_FORMATTERS} from "@bokehjs/core/util/templating"
import type {SliderSpec} from "@bokehjs/models/widgets/sliders/abstract_slider"
import {NumericalSlider, NumericalSliderView} from "@bokehjs/models/widgets/sliders/numerical_slider"
import type {TickFormatter} from "@bokehjs/models/formatters/tick_formatter"
import type * as p from "@bokehjs/core/properties"
import {isString} from "@bokehjs/core/util/types"

export class DatetimeSliderView extends NumericalSliderView {
  declare model: DatetimeSlider

  override behaviour = "tap" as const
  override connected = [true, false]

  protected override _calc_to(): SliderSpec<number> {
    const spec = super._calc_to()
    spec.step *= 1_000  // step size is in seconds
    return spec
  }

  protected _formatter(value: number, format: string | TickFormatter): string {
    if (isString(format)) {
      return DEFAULT_FORMATTERS.datetime(value, format, {})
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
      step: 60,
      format: "%d %b %Y %H:%M:%S",
    })
  }
}
