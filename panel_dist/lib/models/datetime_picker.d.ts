import flatpickr from "flatpickr";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import { CalendarPosition } from "@bokehjs/core/enums";
import type * as p from "@bokehjs/core/properties";
type DateStr = string;
type DatesList = (DateStr | [DateStr, DateStr])[];
export declare class DatetimePickerView extends InputWidgetView {
    model: DatetimePicker;
    private _picker?;
    connect_signals(): void;
    remove(): void;
    stylesheets(): StyleSheetLike[];
    _render_input(): HTMLElement;
    render(): void;
    protected _clear(): void;
    protected _on_close(_selected_dates: Date[], date_string: string, _instance: flatpickr.Instance): void;
    protected _position(self: flatpickr.Instance, custom_el: HTMLElement | undefined): void;
}
export declare namespace DatetimePicker {
    type Attrs = p.AttrsOf<Props>;
    type Props = InputWidget.Props & {
        allow_input: p.Property<boolean>;
        value: p.Property<string | null>;
        min_date: p.Property<string | null>;
        max_date: p.Property<string | null>;
        disabled_dates: p.Property<DatesList | null>;
        enabled_dates: p.Property<DatesList | null>;
        position: p.Property<CalendarPosition>;
        inline: p.Property<boolean>;
        enable_time: p.Property<boolean>;
        enable_seconds: p.Property<boolean>;
        military_time: p.Property<boolean>;
        date_format: p.Property<string>;
        mode: p.Property<any>;
    };
}
export interface DatetimePicker extends DatetimePicker.Attrs {
}
export declare class DatetimePicker extends InputWidget {
    properties: DatetimePicker.Props;
    __view_type__: DatetimePickerView;
    constructor(attrs?: Partial<DatetimePicker.Attrs>);
    static __module__: string;
}
export {};
//# sourceMappingURL=datetime_picker.d.ts.map