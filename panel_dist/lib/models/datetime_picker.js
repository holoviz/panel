import flatpickr from "flatpickr";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
import { bounding_box, input } from "@bokehjs/core/dom";
import { CalendarPosition } from "@bokehjs/core/enums";
import { isString } from "@bokehjs/core/util/types";
import * as inputs from "@bokehjs/styles/widgets/inputs.css";
import flatpickr_css from "@bokehjs/styles/widgets/flatpickr.css";
function _convert_date_list(value) {
    const result = [];
    for (const item of value) {
        if (isString(item)) {
            result.push(item);
        }
        else {
            const [from, to] = item;
            result.push({ from, to });
        }
    }
    return result;
}
export class DatetimePickerView extends InputWidgetView {
    static __name__ = "DatetimePickerView";
    _picker;
    connect_signals() {
        super.connect_signals();
        const { value, min_date, max_date, disabled_dates, enabled_dates, inline, enable_time, enable_seconds, military_time, date_format, mode, } = this.model.properties;
        this.on_change(value, () => this.model.value ? this._picker?.setDate(this.model.value) : this._clear());
        this.on_change(min_date, () => this._picker?.set("minDate", this.model.min_date));
        this.on_change(max_date, () => this._picker?.set("maxDate", this.model.max_date));
        this.on_change(disabled_dates, () => {
            const { disabled_dates } = this.model;
            this._picker?.set("disable", disabled_dates != null ? _convert_date_list(disabled_dates) : []);
        });
        this.on_change(enabled_dates, () => {
            const { enabled_dates } = this.model;
            if (enabled_dates != null) {
                this._picker?.set("enable", _convert_date_list(enabled_dates));
            }
            else {
                // this reimplements `set()` for the `undefined` case
                if (this._picker) {
                    this._picker.config._enable = undefined;
                    this._picker.redraw();
                    this._picker.updateValue(true);
                }
            }
        });
        this.on_change(inline, () => this._picker?.set("inline", this.model.inline));
        this.on_change(enable_time, () => this._picker?.set("enableTime", this.model.enable_time));
        this.on_change(enable_seconds, () => this._picker?.set("enableSeconds", this.model.enable_seconds));
        this.on_change(military_time, () => this._picker?.set("time_24hr", this.model.military_time));
        this.on_change(mode, () => this._picker?.set("mode", this.model.mode));
        this.on_change(date_format, () => this._picker?.set("dateFormat", this.model.date_format));
    }
    remove() {
        this._picker?.destroy();
        super.remove();
    }
    stylesheets() {
        return [...super.stylesheets(), flatpickr_css];
    }
    _render_input() {
        return this.input_el = input({ type: "text", class: inputs.input, disabled: this.model.disabled });
    }
    render() {
        if (this._picker != null) {
            return;
        }
        super.render();
        const options = {
            allowInput: this.model.allow_input,
            appendTo: this.group_el,
            positionElement: this.input_el,
            defaultDate: this.model.value,
            inline: this.model.inline,
            position: this._position.bind(this),
            enableTime: this.model.enable_time,
            enableSeconds: this.model.enable_seconds,
            time_24hr: this.model.military_time,
            dateFormat: this.model.date_format,
            mode: this.model.mode,
            onClose: (selected_dates, date_string, instance) => this._on_close(selected_dates, date_string, instance),
        };
        const { min_date, max_date, disabled_dates, enabled_dates } = this.model;
        if (min_date != null) {
            options.minDate = min_date;
        }
        if (max_date != null) {
            options.maxDate = max_date;
        }
        if (disabled_dates != null) {
            options.disable = _convert_date_list(disabled_dates);
        }
        if (enabled_dates != null) {
            options.enable = _convert_date_list(enabled_dates);
        }
        this._picker = flatpickr(this.input_el, options);
        this._picker.maxDateHasTime = true;
        this._picker.minDateHasTime = true;
    }
    _clear() {
        this._picker?.clear();
        this.model.value = null;
    }
    _on_close(_selected_dates, date_string, _instance) {
        if (this.model.mode == "range" && !date_string.includes("to")) {
            return;
        }
        this.model.value = date_string;
        this.change_input();
    }
    _position(self, custom_el) {
        // This function is copied directly from bokehs date_picker
        const positionElement = custom_el ?? self._positionElement;
        const calendarHeight = [...self.calendarContainer.children].reduce((acc, child) => acc + bounding_box(child).height, 0);
        const calendarWidth = self.calendarContainer.offsetWidth;
        const configPos = this.model.position.split(" ");
        const configPosVertical = configPos[0];
        const configPosHorizontal = configPos.length > 1 ? configPos[1] : null;
        // const inputBounds = positionElement.getBoundingClientRect()
        const inputBounds = {
            top: positionElement.offsetTop,
            bottom: positionElement.offsetTop + positionElement.offsetHeight,
            left: positionElement.offsetLeft,
            right: positionElement.offsetLeft + positionElement.offsetWidth,
            width: positionElement.offsetWidth,
        };
        const distanceFromBottom = window.innerHeight - inputBounds.bottom;
        const showOnTop = configPosVertical === "above" ||
            (configPosVertical !== "below" &&
                distanceFromBottom < calendarHeight &&
                inputBounds.top > calendarHeight);
        // const top =
        //   window.scrollY +
        //   inputBounds.top +
        //   (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2)
        const top = self.config.appendTo
            ? inputBounds.top +
                (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2)
            : window.scrollY +
                inputBounds.top +
                (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2);
        self.calendarContainer.classList.toggle("arrowTop", !showOnTop);
        self.calendarContainer.classList.toggle("arrowBottom", showOnTop);
        if (self.config.inline) {
            return;
        }
        let left = window.scrollX + inputBounds.left;
        let isCenter = false;
        let isRight = false;
        if (configPosHorizontal === "center") {
            left -= (calendarWidth - inputBounds.width) / 2;
            isCenter = true;
        }
        else if (configPosHorizontal === "right") {
            left -= calendarWidth - inputBounds.width;
            isRight = true;
        }
        self.calendarContainer.classList.toggle("arrowLeft", !isCenter && !isRight);
        self.calendarContainer.classList.toggle("arrowCenter", isCenter);
        self.calendarContainer.classList.toggle("arrowRight", isRight);
        const right = window.document.body.offsetWidth -
            (window.scrollX + inputBounds.right);
        const rightMost = left + calendarWidth > window.document.body.offsetWidth;
        const centerMost = right + calendarWidth > window.document.body.offsetWidth;
        self.calendarContainer.classList.toggle("rightMost", rightMost);
        if (self.config.static) {
            return;
        }
        self.calendarContainer.style.top = `${top}px`;
        if (!rightMost) {
            self.calendarContainer.style.left = `${left}px`;
            self.calendarContainer.style.right = "auto";
        }
        else if (!centerMost) {
            self.calendarContainer.style.left = "auto";
            self.calendarContainer.style.right = `${right}px`;
        }
        else {
            const css = this.shadow_el.styleSheets[0];
            const bodyWidth = window.document.body.offsetWidth;
            const centerLeft = Math.max(0, bodyWidth / 2 - calendarWidth / 2);
            const centerBefore = ".flatpickr-calendar.centerMost:before";
            const centerAfter = ".flatpickr-calendar.centerMost:after";
            const centerIndex = css.cssRules.length;
            const centerStyle = `{left:${inputBounds.left}px;right:auto;}`;
            self.calendarContainer.classList.toggle("rightMost", false);
            self.calendarContainer.classList.toggle("centerMost", true);
            css.insertRule(`${centerBefore},${centerAfter}${centerStyle}`, centerIndex);
            self.calendarContainer.style.left = `${centerLeft}px`;
            self.calendarContainer.style.right = "auto";
        }
    }
}
export class DatetimePicker extends InputWidget {
    static __name__ = "DatetimePicker";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.datetime_picker";
    static {
        this.prototype.default_view = DatetimePickerView;
        this.define(({ Bool, Str, List, Tuple, Or, Nullable }) => {
            const DateStr = Str;
            const DatesList = List(Or(DateStr, Tuple(DateStr, DateStr)));
            return {
                allow_input: [Bool, false],
                value: [Nullable(Str), null],
                min_date: [Nullable(Str), null],
                max_date: [Nullable(Str), null],
                disabled_dates: [Nullable(DatesList), null],
                enabled_dates: [Nullable(DatesList), null],
                position: [CalendarPosition, "auto"],
                inline: [Bool, false],
                enable_time: [Bool, true],
                enable_seconds: [Bool, true],
                military_time: [Bool, true],
                date_format: [Str, "Y-m-d H:i:S"],
                mode: [Str, "single"],
            };
        });
    }
}
//# sourceMappingURL=datetime_picker.js.map