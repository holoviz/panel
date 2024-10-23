import { TimePicker as BkTimePicker, TimePickerView as BkTimePickerView } from "@bokehjs/models/widgets/time_picker";
import type * as p from "@bokehjs/core/properties";
import type flatpickr from "flatpickr";
export declare class TimePickerView extends BkTimePickerView {
    model: TimePicker;
    private _offset_time;
    private _setDate;
    protected get flatpickr_options(): flatpickr.Options.Options;
    connect_signals(): void;
}
export declare namespace TimePicker {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkTimePicker.Props & {};
}
export interface TimePicker extends TimePicker.Attrs {
}
export declare class TimePicker extends BkTimePicker {
    properties: TimePicker.Props;
    constructor(attrs?: Partial<TimePicker.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=time_picker.d.ts.map