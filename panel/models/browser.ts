import * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"

export class BrowserInfoView extends View {
  model: BrowserInfo

  initialize(): void {
    super.initialize();

    if (window.matchMedia != null) {
      this.model.dark_mode = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    this.model.device_pixel_ratio = window.devicePixelRatio
    if (navigator != null) {
      this.model.language = navigator.language
      this.model.webdriver = navigator.webdriver
    }
    this.model.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    this.model.timezone_offset = new Date().getTimezoneOffset();
    this._has_finished = true
    this.notify_finished()
  }
}

export namespace BrowserInfo {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Model.Props & {
    dark_mode: p.Property<boolean | null>
    device_pixel_ratio: p.Property<number | null>
    language: p.Property<string | null>
    timezone: p.Property<string | null>
    timezone_offset: p.Property<number | null>
    webdriver: p.Property<boolean | null>
  }
}

export interface BrowserInfo extends BrowserInfo.Attrs { }

export class BrowserInfo extends Model {
  properties: BrowserInfo.Props

  static __module__ = "panel.models.browser"

  constructor(attrs?: Partial<BrowserInfo.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = BrowserInfoView

    this.define<BrowserInfo.Props>(({Boolean, Nullable, Number, String}) => ({
      dark_mode:          [ Nullable(Boolean), null ],
      device_pixel_ratio: [ Nullable(Number),  null ],
      language:           [ Nullable(String),  null ],
      timezone:           [ Nullable(String),  null ],
      timezone_offset:    [ Nullable(Number),  null ],
      webdriver:          [ Nullable(Boolean), null ]
    }))
  }
}
