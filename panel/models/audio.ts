import type * as p from "@bokehjs/core/properties"

import {HTMLBox, HTMLBoxView, set_size} from "./layout"

export class AudioView extends HTMLBoxView {
  declare model: Audio

  protected audioEl: HTMLAudioElement
  protected dialogEl: HTMLElement
  private _blocked: boolean
  private _time: any
  private _setting: boolean

  override initialize(): void {
    super.initialize()
    this._blocked = false
    this._setting = false
    this._time = Date.now()
  }

  override connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.loop.change, () => this.set_loop())
    this.connect(this.model.properties.paused.change, () => this.set_paused())
    this.connect(this.model.properties.time.change, () => this.set_time())
    this.connect(this.model.properties.value.change, () => this.set_value())
    this.connect(this.model.properties.volume.change, () => this.set_volume())
    this.connect(this.model.properties.muted.change, () => this.set_muted())
    this.connect(this.model.properties.autoplay.change, () => this.set_autoplay())
  }

  override render(): void {
    super.render()
    this.audioEl = document.createElement("audio")
    this.audioEl.controls = true
    this.audioEl.src = this.model.value
    this.audioEl.currentTime = this.model.time
    this.audioEl.loop = this.model.loop
    this.audioEl.muted = this.model.muted
    this.audioEl.autoplay = this.model.autoplay
    if (this.model.volume != null) {
      this.audioEl.volume = this.model.volume/100
    } else {
      this.model.volume = this.audioEl.volume*100
    }
    this.audioEl.onpause = () => this.model.paused = true
    this.audioEl.onplay = () => this.model.paused = false
    this.audioEl.ontimeupdate = () => this.update_time(this)
    this.audioEl.onvolumechange = () => this.update_volume(this)
    set_size(this.audioEl, this.model, false)
    this.shadow_el.appendChild(this.audioEl)
    if (!this.model.paused) {
      this.audioEl.play()
    }
  }

  update_time(view: AudioView): void {
    if (view._setting) {
      view._setting = false
      return
    }
    if ((Date.now() - view._time) < view.model.throttle) {
      return
    }
    view._blocked = true
    view.model.time = view.audioEl.currentTime
    view._time = Date.now()
  }

  update_volume(view: AudioView): void {
    if (view._setting) {
      view._setting = false
      return
    }
    view._blocked = true
    view.model.volume = view.audioEl.volume*100
  }

  set_loop(): void {
    this.audioEl.loop = this.model.loop
  }

  set_muted(): void {
    this.audioEl.muted = this.model.muted
  }

  set_autoplay(): void {
    this.audioEl.autoplay = this.model.autoplay
  }

  set_paused(): void {
    if (!this.audioEl.paused && this.model.paused) {
      this.audioEl.pause()
    }
    if (this.audioEl.paused && !this.model.paused) {
      this.audioEl.play()
    }
  }

  set_volume(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true
    if (this.model.volume != null) {
      this.audioEl.volume = this.model.volume/100
    }
  }

  set_time(): void {
    if (this._blocked) {
      this._blocked = false
      return
    }
    this._setting = true
    this.audioEl.currentTime = this.model.time
  }

  set_value(): void {
    this.audioEl.src = this.model.value
  }
}

export namespace Audio {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    loop: p.Property<boolean>
    paused: p.Property<boolean>
    muted: p.Property<boolean>
    autoplay: p.Property<boolean>
    time: p.Property<number>
    throttle: p.Property<number>
    value: p.Property<any>
    volume: p.Property<number | null>
  }
}

export interface Audio extends Audio.Attrs {}

export class Audio extends HTMLBox {
  declare properties: Audio.Props

  constructor(attrs?: Partial<Audio.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = AudioView

    this.define<Audio.Props>(({Any, Bool, Float, Nullable}) => ({
      loop:     [ Bool, false ],
      paused:   [ Bool,  true ],
      muted:    [ Bool, false ],
      autoplay: [ Bool, false ],
      time:     [ Float,      0 ],
      throttle: [ Float,    250 ],
      value:    [ Any,        "" ],
      volume:   [ Nullable(Float), null ],
    }))
  }
}
