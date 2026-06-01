import { TimePicker as BkTimePicker, TimePickerView as BkTimePickerView } from "@bokehjs/models/widgets/time_picker";
export class TimePickerView extends BkTimePickerView {
    static __name__ = "TimePickerView";
    _offset_time(value) {
        const baseDate = new Date(value);
        const timeZoneOffset = baseDate.getTimezoneOffset() * 60 * 1000;
        return baseDate.getTime() + timeZoneOffset;
    }
    _setDate(date) {
        date = this._offset_time(date);
        this.picker.setDate(date);
    }
    get flatpickr_options() {
        // on init
        const options = super.flatpickr_options;
        if (options.defaultDate != null) {
            options.defaultDate = this._offset_time(options.defaultDate);
        }
        return options;
    }
    connect_signals() {
        super.connect_signals();
        const { value } = this.model.properties;
        this.connect(value.change, () => {
            const { value } = this.model;
            if (value != null && typeof value === "number") {
                // we need to handle it when programmatically changed thru Python, e.g.
                // time_picker.value = "4:08" or time_picker.value = "datetime.time(4, 8)"
                // else, when changed in the UI, e.g. by typing in the input field
                // no special handling is needed
                this._setDate(value);
            }
        });
    }
}
export class TimePicker extends BkTimePicker {
    static __name__ = "TimePicker";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.time_picker";
    static {
        this.prototype.default_view = TimePickerView;
        this.define(({}) => ({}));
    }
}
//# sourceMappingURL=time_picker.js.map