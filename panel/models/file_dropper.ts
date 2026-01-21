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

// Mapping of file extensions to browser-reported MIME types
// as it's not yet supported by filepond, see:
// https://github.com/pqina/filepond-plugin-file-validate-type/issues/13
const EXTENSION_TO_MIME_TYPE: Record<string, string> = {
  // Images
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".bmp": "image/bmp",
  ".ico": "image/x-icon",
  ".tiff": "image/tiff",
  ".tif": "image/tiff",
  ".avif": "image/avif",

  // Video
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".mov": "video/quicktime",
  ".mkv": "video/x-matroska",
  ".avi": "video/x-msvideo",
  ".wmv": "video/x-ms-wmv",
  ".flv": "video/x-flv",

  // Audio
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".ogg": "audio/ogg",
  ".oga": "audio/ogg",
  ".m4a": "audio/mp4",
  ".aac": "audio/aac",
  ".flac": "audio/flac",

  // Text / documents
  ".txt": "text/plain",
  ".md": "text/markdown",
  ".rtf": "application/rtf",
  ".pdf": "application/pdf",

  // Structured data (browser-compatible)
  ".json": "application/json",
  ".xml": "text/xml",
  ".csv": "text/csv",
  ".tsv": "text/tab-separated-values",
  ".yaml": "text/yaml",
  ".yml": "text/yaml",

  // Web / code
  ".html": "text/html",
  ".htm": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".ts": "application/typescript",
  ".jsx": "text/jsx",
  ".tsx": "text/tsx",
  ".wasm": "application/wasm",

  // Office documents
  ".doc": "application/msword",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".xls": "application/vnd.ms-excel",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ".ppt": "application/vnd.ms-powerpoint",
  ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  ".odt": "application/vnd.oasis.opendocument.text",
  ".ods": "application/vnd.oasis.opendocument.spreadsheet",
  ".odp": "application/vnd.oasis.opendocument.presentation",

  // Archives
  ".zip": "application/zip",
  ".tar": "application/x-tar",
  ".gz": "application/gzip",
  ".tgz": "application/gzip",
  ".bz2": "application/x-bzip2",
  ".xz": "application/x-xz",
  ".7z": "application/x-7z-compressed",
  ".rar": "application/vnd.rar",

  // Fonts
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",

  // Executables / binaries
  ".exe": "application/vnd.microsoft.portable-executable",
  ".dll": "application/vnd.microsoft.portable-executable",
  ".bin": "application/octet-stream",
  ".dmg": "application/x-apple-diskimage",
  ".pkg": "application/octet-stream",
  ".deb": "application/vnd.debian.binary-package",
  ".rpm": "application/x-rpm",
};

export class FileDropperView extends InputWidgetView {
  declare model: FileDropper
  declare input_el: HTMLInputElement
  _file_pond: any | null = null
  _transfer_in_process: string | null = null

  private extensionsToMimeTypes(types: string[]): string[] {
    return types.map(type => {
      // MIME types, including wildcards like "image/*"
      if (type.includes("/")) {
        return type
      }
      // Guessing it's an extension
      if (type.startsWith(".")) {
        const lowerType = type.toLowerCase()
        return EXTENSION_TO_MIME_TYPE[lowerType] || type
      }
      return type
    })
  }

  override initialize(): void {
    super.initialize()
    const {previews} = this.model
    if (previews.includes("image")) {
      (window as any).FilePond.registerPlugin((window as any).FilePondPluginImagePreview)
    }
    if (previews.includes("pdf")) {
      (window as any).FilePond.registerPlugin((window as any).FilePondPluginPdfPreview)
    }
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginFileValidateType);
    (window as any).FilePond.registerPlugin((window as any).FilePondPluginFileValidateSize)
  }

  override connect_signals(): void {
    super.connect_signals()
    const {disabled, layout, max_file_size, max_files, max_total_file_size, multiple} = this.model.properties
    this.on_change([disabled, max_file_size, max_files, max_total_file_size, multiple, layout], () => {
      this._file_pond?.setOptions({
        acceptedFileTypes: this.extensionsToMimeTypes(this.model.accepted_filetypes),
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
      acceptedFileTypes: this.extensionsToMimeTypes(this.model.accepted_filetypes),
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
    previews: p.Property<string[]>
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
      previews:            [ List(Str), [ "image", "pdf" ]],
    }))
  }
}
