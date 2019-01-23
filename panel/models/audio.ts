import * as p from "core/properties"
import {div} from "core/dom"
import {Widget, WidgetView} from "models/widgets/widget"

export class AudioView extends WidgetView {
  model: Audio

  protected dialogEl: HTMLElement

  initialize(options: any): void {
    super.initialize(options)
    this.render()
  }

  connect_signals(): void {
    super.connect_signals()	
    this.connect(this.model.change, () => this.render())
    this.connect(this.model.properties.loop.change, () => this.set_loop())
    this.connect(this.model.properties.paused.change, () => this.set_paused())
    this.connect(this.model.properties.time.change, () => this.set_time())
    this.connect(this.model.properties.value.change, () => this.render())
    this.connect(this.model.properties.volume.change, () => this.set_volume())
  }

  render(): void {
    if (this.audioEl) {
      return
    }
    this.audioEl = document.createElement('audio')
    this.audioEl.controls = true
    this.audioEl.src = this.model.value
    this.audioEl.currentTime = this.model.time
    this.audioEl.loop = this.model.loop
    if (this.model.volume != null)
      this.audioEl.volume = this.model.volume/100
    else
      this.model.volume = this.audioEl.volume*100
    this.audioEl.ontimeupdate = () => this.model.time = this.audioEl.currentTime
	this.audioEl.onpause = () => this.model.paused = true
    this.audioEl.onplay = () => this.model.play = true
    this.audioEl.onvolumechange = () => this.model.volume = this.audioEl.volume*100
    this.el.appendChild(this.audioEl)
	if (!this.model.paused)
	  this.audioEl.play()
  }

  set_loop(): void {
    this.audioEl.loop = this.model.loop
  }

  set_paused(): void {
    if (!this.audioEl.paused && this.model.paused)
      this.audioEl.pause()
    if (this.audioEl.paused && !this.model.paused)
      this.audioEl.play()
  }

  set_volume(): void {
    this.audioEl.volume = this.model.volume/100
  }
  
  set_time(): void {
    this.audioEl.currentTime = this.model.time
  }
}

export namespace Audio {
  export interface Attrs extends Widget.Attrs {}
  export interface Props extends Widget.Props {}
}

export interface Audio extends Audio.Attrs {}

export abstract class Audio extends Widget {

  properties: Audio.Props

  constructor(attrs?: Partial<Audio.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "Audio"
    this.prototype.default_view = AudioView

    this.define({
      loop:   [ p.Bool, false  ],
      paused: [ p.Bool, true   ],
      time:   [ p.Number, 0    ],
      value:  [ p.Any,    ''   ],
      volume: [ p.Number, null ],
    })
  }
}

Audio.initClass()
