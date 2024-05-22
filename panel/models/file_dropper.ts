import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {input} from "@bokehjs/core/dom"
import {Enum} from "@bokehjs/core/kinds"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"

import * as inputs from "@bokehjs/styles/widgets/inputs.css"
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

export class DeleteEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "delete_event"
  }
}

export class FileDropperView extends InputWidgetView {
  declare model: FileDropper
  declare input_el: HTMLInputElement
  _file_pond: any | null = null
  _transfer_in_process: string | null = null

  override initialize(): void {
    super.initialize();
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginImagePreview);
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginPdfPreview);
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginFileValidateType);
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginFileValidateSize)
  }

  override connect_signals(): void {
    super.connect_signals()
    const {disabled, layout, max_file_size, max_files, max_total_file_size, multiple} = this.model.properties
    this.on_change([disabled, max_file_size, max_files, max_total_file_size, multiple, layout], () => {
      this._file_pond?.setOptions({
        acceptedFileTypes: this.model.accepted_filetypes,
        allowMultiple: this.model.multiple,
        disabled: this.model.disabled,
        maxFiles: this.model.max_files,
        maxFileSize: this.model.max_file_size,
        maxTotalFileSize: this.model.max_total_file_size,
        stylePanelLayout: this.model.layout,
      })
    })
  }

  override remove(): void {
    if (this._file_pond) {
      this._file_pond.destroy()
    }
    super.remove()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), filedropper_css]
  }

  protected _render_input(): HTMLInputElement {
    const {multiple, disabled} = this.model

    return this.input_el = input({type: "file", class: inputs.input, multiple, disabled})
  }

  override render(): void {
    super.render()

    this._file_pond = (window as any).FilePond.create(this.input_el, {
      acceptedFileTypes: this.model.accepted_filetypes,
      allowMultiple: this.model.multiple,
      credits: false,
      disabled: this.model.disabled,
      maxFiles: this.model.max_files,
      maxFileSize: this.model.max_file_size,
      maxTotalFileSize: this.model.max_total_file_size,
      server: {
        process: (
          _: string,
          file: File,
          __: any,
          load: (id: string) => void,
          error: (msg: string) => void,
          progress: (computable: boolean, loaded: number, total: number) => void,
        ) => {
          void this._process_upload(file, load, error, progress)
        },
        fetch: null,
        revert: (id: string, load: () => void): void => {
          this.model.trigger_event(new DeleteEvent({name: id}))
          load()
        },
      },
      stylePanelLayout: this.model.layout,
    })
  }

  private async _process_upload(
    file: File,
    load: (id: string) => void,
    error: (msg: string) => void,
    progress: (computable: boolean, loaded: number, total: number) => void,
  ): Promise<any> {
    const buffer_size = this.model.chunk_size
    const chunks = Math.ceil((file.size + 1)/ buffer_size) // +1 is for empty files
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
          chunk: i+1,
          data: await file.slice(start, end).arrayBuffer(),
          name: (file as any)._relativePath || file.name,
          total_chunks: chunks,
          type: file.type,
        }))
        progress(true, end, file.size)
      }
      load(file.name)
      resolve(file.name)
    }).catch(() => error("Upload failed."))

    return {abort: () => {
      abort_flag = true
    }}
  }
}

export const DropperLayout = Enum("integrated", "compact", "circle")

export namespace FileDropper {
  export type Attrs = p.AttrsOf<Props>
  export type Props = InputWidget.Props & {
    accepted_filetypes: p.Property<string[]>
    chunk_size: p.Property<number>
    layout: p.Property<typeof DropperLayout["__type__"] | null>
    max_file_size: p.Property<string | null>
    max_files: p.Property<number | null>
    max_total_file_size: p.Property<string | null>
    mime_type: p.Property<any>
    multiple: p.Property<boolean>
  }
}

export interface FileDropper extends FileDropper.Attrs {}

export class FileDropper extends InputWidget {
  declare properties: FileDropper.Props

  static override __module__ = "panel.models.file_dropper"

  constructor(attrs?: Partial<FileDropper.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = FileDropperView
    this.define<FileDropper.Props>(({Any, List, Bool, Int, Nullable, Str}) => ({
      accepted_filetypes:  [ List(Str),           [] ],
      chunk_size:          [ Int,            10000000 ],
      max_file_size:       [ Nullable(Str),      null ],
      max_files:           [ Nullable(Int),      null ],
      max_total_file_size: [ Nullable(Str),      null ],
      mime_type:           [ Any,                  {} ],
      multiple:            [ Bool,               true ],
      layout:              [ Nullable(DropperLayout), null ],
    }))
  }
}
