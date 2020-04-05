import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"

import {bk_btn, bk_btn_type} from "@bokehjs/styles/buttons"

import {ButtonType} from "@bokehjs/core/enums"
import * as p from "@bokehjs/core/properties"

function dataURItoBlob(dataURI: string) {
  // convert base64 to raw binary data held in a string

  const byteString = atob(dataURI.split(',')[1]);

  // separate out the mime component
  const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]

  // write the bytes of the string to an ArrayBuffer
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }

  // write the ArrayBuffer to a blob, and you're done
  var bb = new Blob([ab], { type: mimeString });
  return bb;
}

export class FileDownloadView extends InputWidgetView {
  model: FileDownload

  anchor_el: HTMLAnchorElement

  _initialized: boolean = false

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.button_type.change, () => this.render())
    this.connect(this.model.properties.data.change, () => this.render())
    this.connect(this.model.properties.filename.change, () => this.render())
    this.connect(this.model.properties.label.change, () => this._update_label())
  }
  
  render(): void {
    super.render()
    this.anchor_el = document.createElement('a')
    this.anchor_el.classList.add(bk_btn)
    this.anchor_el.classList.add(bk_btn_type(this.model.button_type))
    this.anchor_el.textContent = this.model.label
    if (this.model.data === null || this.model.filename === null) {
      this.anchor_el.addEventListener("click", () => this.click())
      this.group_el.appendChild(this.anchor_el)  
      this._initialized = true
      return
    }
    const blob = dataURItoBlob(this.model.data)
    const uriContent = (URL as any).createObjectURL(blob)
    this.anchor_el.href = uriContent
    this.anchor_el.download = this.model.filename
    //this.group_el.classList.add(bk_btn_group)
    this.group_el.appendChild(this.anchor_el)
    if (this.model.auto && this._initialized)
      this.anchor_el.click()
    this._initialized = true
  }

  _update_label(): void {
    this.anchor_el.textContent = this.model.label
  }

  click(): void {
    this.model.clicks = this.model.clicks + 1
  }
}

export namespace FileDownload {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    auto: p.Property<boolean> 
    button_type: p.Property<ButtonType>
    clicks: p.Property<number>
    data: p.Property<string | null>
    label: p.Property<string>
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
      auto:     [ p.Boolean, false ],
      clicks:   [ p.Number,  0     ],
      data:     [ p.String,  null  ],
      label:    [ p.String,  "Download"  ],
      filename: [ p.String,  null  ],
      button_type: [ p.ButtonType, "default" ], // TODO (bev)
    })

    this.override({
      title: "",
    })
  }
}
