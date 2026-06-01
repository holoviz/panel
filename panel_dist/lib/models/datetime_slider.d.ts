import type { SliderSpec } from "@bokehjs/models/widgets/sliders/abstract_slider";
import { NumericalSlider, NumericalSliderView } from "@bokehjs/models/widgets/sliders/numerical_slider";
import type { TickFormatter } from "@bokehjs/models/formatters/tick_formatter";
import type * as p from "@bokehjs/core/properties";
export declare class DatetimeSliderView extends NumericalSliderView {
    model: DatetimeSlider;
    behaviour: "tap";
    connected: boolean[];
    protected _calc_to(): SliderSpec<number>;
    protected _formatter(value: number, format: string | TickFormatter): string;
}
export declare namespace DatetimeSlider {
    type Attrs = p.AttrsOf<Props>;
    type Props = NumericalSlider.Props;
}
export interface DatetimeSlider extends DatetimeSlider.Attrs {
}
export declare class DatetimeSlider extends NumericalSlider {
    properties: DatetimeSlider.Props;
    __view_type__: DatetimeSliderView;
    constructor(attrs?: Partial<DatetimeSlider.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=datetime_slider.d.ts.map