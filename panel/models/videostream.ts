import * as p from "core/properties"
import {Widget, WidgetView} from "models/widgets/widget"

export class VideoStreamView extends WidgetView {
  model: VideoStream
  protected videoEl: HTMLVideoElement
  protected canvasEl: HTMLCanvasElement
  protected constraints = {
    'audio': false,
    'video': true
  }

  initialize(): void {
    super.initialize()
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.snapshot.change, () => this.snapshot())
    this.connect(this.model.properties.paused.change, () => this.model.paused ? this.videoEl.pause() : this.videoEl.play())
  }

  snapshot(): void{
    this.canvasEl.width = this.videoEl.videoWidth
    this.canvasEl.height = this.videoEl.videoHeight
    const context = this.canvasEl.getContext('2d')
    if (context)
      context.drawImage(this.videoEl, 0, 0, this.canvasEl.width, this.canvasEl.height)
    this.model.value = this.canvasEl.toDataURL("image/jpeg", 0.95)
  }

  render(): void {
    super.render()
    if (this.videoEl)
      return
    this.videoEl = document.createElement('video')
    this.canvasEl = document.createElement('canvas')
    this.el.appendChild(this.videoEl)
    if (navigator.mediaDevices.getUserMedia){
      navigator.mediaDevices.getUserMedia(this.constraints)
      .then(stream => {
        this.videoEl.srcObject = stream
        if (!this.model.paused){
          this.videoEl.play()
        }
      })
      .catch(console.error)
    }
  }
  
}

export namespace VideoStream {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Widget.Props & {
    paused: p.Property<boolean>
    snapshot: p.Property<boolean>
    value: p.Property<any>
  }
}

export interface VideoStream extends VideoStream.Attrs {}

export abstract class VideoStream extends Widget {
  properties: VideoStream.Props

  constructor(attrs?: Partial<VideoStream.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VideoStream"
    this.prototype.default_view = VideoStreamView

    this.define<VideoStream.Props>({
      paused:   [ p.Boolean, false ],
      snapshot: [ p.Boolean, false ],
      value:    [ p.Any,           ]
    })
  }
}

VideoStream.initClass()
