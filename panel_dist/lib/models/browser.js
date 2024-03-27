import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
export class BrowserInfoView extends View {
    static __name__ = "BrowserInfoView";
    initialize() {
        super.initialize();
        if (window.matchMedia != null) {
            this.model.dark_mode = window.matchMedia("(prefers-color-scheme: dark)").matches;
        }
        this.model.device_pixel_ratio = window.devicePixelRatio;
        if (navigator != null) {
            this.model.language = navigator.language;
            this.model.webdriver = navigator.webdriver;
        }
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (timezone != null) {
            this.model.timezone = timezone;
        }
        const timezone_offset = new Date().getTimezoneOffset();
        if (timezone_offset != null) {
            this.model.timezone_offset = timezone_offset;
        }
        this._has_finished = true;
        this.notify_finished();
    }
}
export class BrowserInfo extends Model {
    static __name__ = "BrowserInfo";
    static __module__ = "panel.models.browser";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = BrowserInfoView;
        this.define(({ Bool, Nullable, Float, Str }) => ({
            dark_mode: [Nullable(Bool), null],
            device_pixel_ratio: [Nullable(Float), null],
            language: [Nullable(Str), null],
            timezone: [Nullable(Str), null],
            timezone_offset: [Nullable(Float), null],
            webdriver: [Nullable(Bool), null],
        }));
    }
}
//# sourceMappingURL=browser.js.map