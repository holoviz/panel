import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView} from "./layout"

export class VideoView extends PanelHTMLBoxView {
  model: Video
  protected videoEl: HTMLVideoElement
  protected dialogEl: HTMLElement
  private _blocked: boolean
  private _time: any
  private _setting: boolean

  initialize(): void {
    super.initialize()
    this._blocked = false
    this._setting = false
    this._time = Date.now()
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.loop.change, () => this.set_loop())
    this.connect(this.model.properties.paused.change, () => this.set_paused())
    this.connect(this.model.properties.time.change, () => this.set_time())
    this.connect(this.model.properties.value.change, () => this.set_value())
    this.connect(this.model.properties.volume.change, () => this.set_volume())
  }

  render(): void {
    super.render()
    this.videoEl = document.createElement('video')
    if (!this.model.sizing_mode || this.model.sizing_mode === 'fixed') {
      if (this.model.height)
        this.videoEl.height = this.model.height;
      if (this.model.width)
        this.videoEl.width = this.model.width;
    }
    this.videoEl.style.objectFit = 'fill'
    this.videoEl.style.minWidth = '100%';
    this.videoEl.style.minHeight = '100%';
    this.videoEl.controls = true
    this.videoEl.src = this.model.value
    this.videoEl.currentTime = this.model.time
    this.videoEl.loop = this.model.loop
    if (this.model.volume != null)
      this.videoEl.volume = this.model.volume/100
    else
      this.model.volume = this.videoEl.volume*100
    this.videoEl.onpause = () => this.model.paused = true
    this.videoEl.onplay = () => this.model.paused = false
    this.videoEl.ontimeupdate = () => this.update_time(this)
    this.videoEl.onvolumechange = () => this.update_volume(this)
    this.el.appendChild(this.videoEl)
    if (!this.model.paused)
      this.videoEl.play()
  }

  update_time(view: VideoView): void {
    if (view._setting) {
      view._setting = false
      return
    }
    if ((Date.now() - view._time) < view.model.throttle)
      return
    view._blocked = true
    view.model.time = view.videoEl.currentTime
    view._time = Date.now()
  }

  update_volume(view: VideoView): void {
    if (view._setting) {
      view._setting = false
      return
    }
    view._blocked = true
    view.model.volume = view.videoEl.volume*100
  }

  set_loop(): void {
    this.videoEl.loop = this.model.loop
  }

  set_paused(): void {
    if (!this.videoEl.paused && this.model.paused)
      this.videoEl.pause()
    if (this.videoEl.paused && !this.model.paused)
      this.videoEl.play()
  }

  set_volume(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true;
    if (this.model.volume != null)
      this.videoEl.volume = (this.model.volume as number)/100
  }

  set_time(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true;
    this.videoEl.currentTime = this.model.time
  }

  set_value(): void {
    this.videoEl.src = this.model.value
  }
}

export namespace Video {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    loop: p.Property<boolean>
    paused: p.Property<boolean>
    time: p.Property<number>
    throttle: p.Property<number>
    value: p.Property<any>
    volume: p.Property<number | null>
  }
}

export interface Video extends Video.Attrs {}

export class Video extends HTMLBox {
  properties: Video.Props

  constructor(attrs?: Partial<Video.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static init_Video(): void {
    this.prototype.default_view = VideoView

    this.define<Video.Props>(({Any, Boolean, Int, Number}) => ({
      loop:     [ Boolean, false ],
      paused:   [ Boolean,  true ],
      time:     [ Number,      0 ],
      throttle: [ Int,       250 ],
      value:    [ Any,        '' ],
      volume:   [ Int            ],
    }))
  }
}
