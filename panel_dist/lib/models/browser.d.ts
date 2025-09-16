import type * as p from "@bokehjs/core/properties";
import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
export declare class BrowserInfoView extends View {
    model: BrowserInfo;
    initialize(): void;
}
export declare namespace BrowserInfo {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        dark_mode: p.Property<boolean | null>;
        device_pixel_ratio: p.Property<number | null>;
        language: p.Property<string | null>;
        timezone: p.Property<string | null>;
        timezone_offset: p.Property<number | null>;
        webdriver: p.Property<boolean | null>;
        webgl: p.Property<boolean | null>;
    };
}
export interface BrowserInfo extends BrowserInfo.Attrs {
}
export declare class BrowserInfo extends Model {
    properties: BrowserInfo.Props;
    static __module__: string;
    constructor(attrs?: Partial<BrowserInfo.Attrs>);
}
//# sourceMappingURL=browser.d.ts.map