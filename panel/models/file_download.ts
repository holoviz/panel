import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"

import * as p from "@bokehjs/core/properties"

export class FileDownloadView extends InputWidgetView {
  model: FileDownload

  anchor_el: HTMLAnchorElement


  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this.render())
    this.connect(this.model.properties.filename.change, () => this.render())
  }
  
  render(): void {
    super.render()
    this.anchor_el = document.createElement('a')
    if (this.model.data === null || this.model.filename === null) {
      this.anchor_el.addEventListener("click", () => this.click())
      this.anchor_el.textContent = "Transfer File"
      console.log(this.group_el)
      this.group_el.appendChild(this.anchor_el)
      return
    }
    this.anchor_el.href = this.model.data
    this.anchor_el.download = this.model.filename
    this.anchor_el.textContent = "Download File"
    this.group_el.appendChild(this.anchor_el)
  }

  click(): void {
    this.model.clicks = this.model.clicks + 1
  }
}

export namespace FileDownload {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    clicks: p.Property<number>
    data: p.Property<string | null>
    filename: p.Property<string | null>
  }
}

export interface FileDownload extends FileDownload.Attrs {}

export class FileDownload extends InputWidget {
  properties: FileDownload.Props

  constructor(attrs?: Partial<FileDownload.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static init_FileDownload(): void {
    this.prototype.default_view = FileDownloadView

    this.define<FileDownload.Props>({
      clicks: [ p.Number, 0 ], // deprecated
      data: [ p.String, null ],
      filename: [ p.String, null ],
    })

    this.override({
      title: "Transfer Files",
    })
  }
}
