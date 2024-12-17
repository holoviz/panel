import type * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"

export class BrowserInfoView extends View {
  declare model: BrowserInfo

  override initialize(): void {
    super.initialize()

    if (window.matchMedia != null) {
      const darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
      darkModeMediaQuery.addEventListener("change", (e) => {
        this.model.dark_mode = e.matches
      })
      this.model.dark_mode = darkModeMediaQuery.matches
    }
    this.model.device_pixel_ratio = window.devicePixelRatio
    if (navigator != null) {
      this.model.language = navigator.language
      this.model.webdriver = navigator.webdriver
    }
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    if (timezone != null) {
      this.model.timezone = timezone
    }
    const timezone_offset = new Date().getTimezoneOffset()
    if (timezone_offset != null) {
      this.model.timezone_offset = timezone_offset
    }
    try {
      const canvas = document.createElement("canvas")
      this.model.webgl = !!(
        window.WebGLRenderingContext &&
          (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
      )
    } catch (e) {
      this.model.webgl = false
    }
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
    webgl: p.Property<boolean | null>
  }
}

export interface BrowserInfo extends BrowserInfo.Attrs { }

export class BrowserInfo extends Model {
  declare properties: BrowserInfo.Props

  static override __module__ = "panel.models.browser"

  constructor(attrs?: Partial<BrowserInfo.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = BrowserInfoView

    this.define<BrowserInfo.Props>(({Bool, Nullable, Float, Str}) => ({
      dark_mode:          [ Nullable(Bool),  null ],
      device_pixel_ratio: [ Nullable(Float), null ],
      language:           [ Nullable(Str),   null ],
      timezone:           [ Nullable(Str),   null ],
      timezone_offset:    [ Nullable(Float), null ],
      webdriver:          [ Nullable(Bool),  null ],
      webgl:              [ Nullable(Bool),  null ],
    }))
  }
}
