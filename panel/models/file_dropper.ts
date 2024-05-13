import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {Enum} from "@bokehjs/core/kinds"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import {FileInput, FileInputView} from "@bokehjs/models/widgets/file_input"

import filedropper_css from "styles/models/filedropper.css"

export class UploadEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "upload_event"
  }
}

export class FileDropperView extends FileInputView {
  declare model: FileDropper
  declare input_el: HTMLInputElement
  _transfer_in_process: string | null = null

  override initialize(): void {
    super.initialize();
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginImagePreview)
  }

  override stylesheets(): StyleSheetLike[] {
    return [filedropper_css]
  }

  override render(): void {
    super.render()

    this.input_el.className = "filepond";
    (window as any).FilePond.create(this.input_el, {
      allowMultiple: this.model.multiple,
      stylePanelLayout: this.model.layout,
      server: {
        process: (fieldName: string, file: File, metadata, load, error, progress, abort) => this._process_upload(fieldName, file, metadata, load, error, progress, abort),
        fetch: null,
        revert: null,
      },
    })
  }

  async private _process_upload(fieldName: string, file: File, metadata, load, error, progress, abort): any {
    const buffer_size = this.model.chunk_size
    const chunks = Math.ceil(file.size / buffer_size)
    let abort_flag = false
    new Promise(async (resolve, reject) => {
      for (let i = 0; i < chunks; i++) {
        if (abort_flag) {
          reject(file.name)
          return
        }
        const start = i*buffer_size
        const end = Math.min(start+buffer_size, file.size)
        this.model.trigger_event(new UploadEvent({
          name: (file as any)._relativePath || file.name,
          chunk: i+1,
          total_chunks: chunks,
          data: await file.slice(start, end).arrayBuffer(),
        }))
        progress(true, end, file.size)
      }
      load(file.name)
      resolve(file.name)
    }).catch(() => error())

    return {abort: () => {
      abort_flag = true
    }}
  }
}

export const DropperLayout = Enum("integrated", "compact", "circle")

export namespace FileDropper {
  export type Attrs = p.AttrsOf<Props>
  export type Props = FileInput.Props & {
    chunk_size: p.Property<number>
    layout: p.Property<typeof DropperLayout["__type__"]>
  }
}

export interface FileDropper extends FileDropper.Attrs {}

export class FileDropper extends FileInput {
  declare properties: FileDropper.Props

  static override __module__ = "panel.models.file_dropper"

  constructor(attrs?: Partial<FileDropper.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = FileDropperView
    this.define<FileDropper.Props>(({Int}) => ({
      chunk_size: [ Int, 1000000],
      layout: [DropperLayout, "compact" ],
    }))
  }
}
