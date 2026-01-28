// adapted from bokeh
// https://github.com/bokeh/bokeh/blob/branch-3.7/bokehjs/src/lib/models/widgets/sliders/date_slider.ts
import { DEFAULT_FORMATTERS } from "@bokehjs/core/util/templating";
import { NumericalSlider, NumericalSliderView } from "@bokehjs/models/widgets/sliders/numerical_slider";
import { isString } from "@bokehjs/core/util/types";
export class DatetimeSliderView extends NumericalSliderView {
    static __name__ = "DatetimeSliderView";
    behaviour = "tap";
    connected = [true, false];
    _calc_to() {
        const spec = super._calc_to();
        spec.step *= 1_000; // step size is in seconds
        return spec;
    }
    _formatter(value, format) {
        if (isString(format)) {
            return DEFAULT_FORMATTERS.datetime(value, format, {});
        }
        else {
            return format.compute(value);
        }
    }
}
export class DatetimeSlider extends NumericalSlider {
    static __name__ = "DatetimeSlider";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.datetime_slider";
    static {
        this.prototype.default_view = DatetimeSliderView;
        this.override({
            step: 60,
            format: "%d %b %Y %H:%M:%S",
        });
    }
}
//# sourceMappingURL=datetime_slider.js.map