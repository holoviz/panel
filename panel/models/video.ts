import type * as p from "@bokehjs/core/properties"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {px} from "@bokehjs/core/dom"

import {HTMLBox, HTMLBoxView} from "./layout"
import video_css from "styles/models/video.css"

export class VideoView extends HTMLBoxView {
  declare model: Video

  protected video_el: HTMLVideoElement

  private _time: number
  private _blocked: boolean = false
  private _setting: boolean = false

  override initialize(): void {
    super.initialize()
    this._time = Date.now()
  }

  override connect_signals(): void {
    super.connect_signals()

    const {loop, paused, muted, autoplay, time, value, volume} = this.model.properties
    this.on_change(loop, () => this.set_loop())
    this.on_change(paused, () => this.set_paused())
    this.on_change(muted, () => this.set_muted())
    this.on_change(autoplay, () => this.set_autoplay())
    this.on_change(time, () => this.set_time())
    this.on_change(value, () => this.set_value())
    this.on_change(volume, () => this.set_volume())
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), video_css]
  }

  override render(): void {
    super.render()

    this.video_el = document.createElement("video")
    const container_el = document.createElement("div")
    container_el.className = "pn-video-container"
    container_el.style.height = "100%"
    container_el.style.width = "100%"

    const {sizing_mode} = this.model
    if (sizing_mode == null || sizing_mode === "fixed") {
      const {width, height} = this.model
      if (width != null) {
        this.video_el.width = width
      }
      if (height != null) {
        this.video_el.height = height
      }
    }
    const {max_width, max_height} = this.model
    if (max_width != null) {
      this.video_el.style.maxWidth = px(max_width)
    }
    if (max_height != null) {
      this.video_el.style.maxHeight = px(max_height)
    }

    this.video_el.controls = true
    this.video_el.src = this.model.value
    this.video_el.currentTime = this.model.time
    this.video_el.loop = this.model.loop
    this.video_el.muted = this.model.muted
    this.video_el.autoplay = this.model.autoplay
    if (this.model.volume != null) {
      this.video_el.volume = this.model.volume/100
    } else {
      this.model.volume = this.video_el.volume*100
    }
    this.video_el.onpause = () => this.model.paused = true
    this.video_el.onplay = () => this.model.paused = false
    this.video_el.ontimeupdate = () => this.update_time()
    this.video_el.onvolumechange = () => this.update_volume()

    container_el.append(this.video_el)
    this.shadow_el.append(container_el)

    if (!this.model.paused) {
      void this.video_el.play()
    }
  }

  update_time(): void {
    if (this._setting) {
      this._setting = false
      return
    }
    if ((Date.now() - this._time) < this.model.throttle) {
      return
    }
    this._blocked = true
    this.model.time = this.video_el.currentTime
    this._time = Date.now()
  }

  update_volume(): void {
    if (this._setting) {
      this._setting = false
      return
    }
    this._blocked = true
    this.model.volume = this.video_el.volume*100
  }

  set_loop(): void {
    this.video_el.loop = this.model.loop
  }

  set_muted(): void {
    this.video_el.muted = this.model.muted
  }

  set_autoplay(): void {
    this.video_el.autoplay = this.model.autoplay
  }

  set_paused(): void {
    const {paused} = this.model
    if (!this.video_el.paused && paused) {
      this.video_el.pause()
    }
    if (this.video_el.paused && !paused) {
      void this.video_el.play()
    }
  }

  set_volume(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true
    const {volume} = this.model
    if (volume != null) {
      this.video_el.volume = volume/100
    }
  }

  set_time(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true
    this.video_el.currentTime = this.model.time
  }

  set_value(): void {
    this.video_el.src = this.model.value
  }
}

export namespace Video {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    loop: p.Property<boolean>
    paused: p.Property<boolean>
    muted: p.Property<boolean>
    autoplay: p.Property<boolean>
    time: p.Property<number>
    throttle: p.Property<number>
    value: p.Property<string>
    volume: p.Property<number | null>
  }
}

export interface Video extends Video.Attrs {}

export class Video extends HTMLBox {
  declare properties: Video.Props

  constructor(attrs?: Partial<Video.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = VideoView

    this.define<Video.Props>(({Bool, Int, Float, Str, Nullable}) => ({
      loop:     [ Bool, false ],
      paused:   [ Bool, true ],
      muted:    [ Bool, false ],
      autoplay: [ Bool, false ],
      time:     [ Float, 0 ],
      throttle: [ Int, 250 ],
      value:    [ Str, "" ],
      volume:   [ Nullable(Int), null ],
    }))
  }
}
