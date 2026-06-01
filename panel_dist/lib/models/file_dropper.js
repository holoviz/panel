import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { input } from "@bokehjs/core/dom";
import { Enum } from "@bokehjs/core/kinds";
import { InputWidget, InputWidgetView } from "@bokehjs/models/widgets/input_widget";
import * as inputs from "@bokehjs/styles/widgets/inputs.css";
import filedropper_css from "../styles/models/filedropper.css";
export class UploadEvent extends ModelEvent {
    data;
    static __name__ = "UploadEvent";
    constructor(data) {
        super();
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, data: this.data };
    }
    static {
        this.prototype.event_name = "upload_event";
    }
}
export class DeleteEvent extends ModelEvent {
    data;
    static __name__ = "DeleteEvent";
    constructor(data) {
        super();
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, data: this.data };
    }
    static {
        this.prototype.event_name = "delete_event";
    }
}
// Mapping of file extensions to browser-reported MIME types
// as it's not yet supported by filepond, see:
// https://github.com/pqina/filepond-plugin-file-validate-type/issues/13
const EXTENSION_TO_MIME_TYPE = {
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
    ".xlsb": "application/vnd.ms-excel.sheet.binary.macroenabled.12",
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
    // Columnar / big data
    ".parquet": "application/octet-stream", // browsers do NOT emit application/parquet
    ".arrow": "application/octet-stream",
    ".feather": "application/octet-stream",
    ".orc": "application/octet-stream",
    // Scientific / numerical
    ".npy": "application/octet-stream",
    ".npz": "application/octet-stream",
    ".mat": "application/octet-stream",
    ".h5": "application/octet-stream",
    ".hdf5": "application/octet-stream",
    ".zarr": "application/octet-stream",
    // R ecosystem
    ".rds": "application/octet-stream",
    ".rda": "application/octet-stream",
    ".rdata": "application/octet-stream",
    // Notebooks
    ".ipynb": "application/json",
    // ML models / artifacts
    ".pkl": "application/octet-stream",
    ".pickle": "application/octet-stream",
    ".joblib": "application/octet-stream",
    ".onnx": "application/octet-stream",
    ".pt": "application/octet-stream",
    ".pth": "application/octet-stream",
    ".h5model": "application/octet-stream",
    // Vector
    ".shp": "application/octet-stream",
    ".shx": "application/octet-stream",
    ".dbf": "application/octet-stream",
    ".geojson": "application/geo+json",
    ".gpkg": "application/octet-stream",
    // Raster
    ".geotiff": "image/tiff",
    ".asc": "text/plain",
};
export class FileDropperView extends InputWidgetView {
    static __name__ = "FileDropperView";
    _file_pond = null;
    _transfer_in_process = null;
    extensionsToMimeTypes(types) {
        return types.map(type => {
            // MIME types, including wildcards like "image/*"
            if (type.includes("/")) {
                return type;
            }
            // Guessing it's an extension
            if (type.startsWith(".")) {
                const lowerType = type.toLowerCase();
                return EXTENSION_TO_MIME_TYPE[lowerType] || type;
            }
            return type;
        });
    }
    initialize() {
        super.initialize();
        const { previews } = this.model;
        if (previews.includes("image")) {
            window.FilePond.registerPlugin(window.FilePondPluginImagePreview);
        }
        if (previews.includes("pdf")) {
            window.FilePond.registerPlugin(window.FilePondPluginPdfPreview);
        }
        window.FilePond.registerPlugin(window.FilePondPluginFileValidateType);
        window.FilePond.registerPlugin(window.FilePondPluginFileValidateSize);
    }
    connect_signals() {
        super.connect_signals();
        const { disabled, layout, max_file_size, max_files, max_total_file_size, multiple } = this.model.properties;
        this.on_change([disabled, max_file_size, max_files, max_total_file_size, multiple, layout], () => {
            this._file_pond?.setOptions({
                acceptedFileTypes: this.extensionsToMimeTypes(this.model.accepted_filetypes),
                allowMultiple: this.model.multiple,
                disabled: this.model.disabled,
                maxFiles: this.model.max_files,
                maxFileSize: this.model.max_file_size,
                maxTotalFileSize: this.model.max_total_file_size,
                stylePanelLayout: this.model.layout,
            });
        });
    }
    remove() {
        if (this._file_pond) {
            this._file_pond.destroy();
        }
        super.remove();
    }
    stylesheets() {
        return [...super.stylesheets(), filedropper_css];
    }
    _render_input() {
        const { multiple, disabled } = this.model;
        return this.input_el = input({ type: "file", class: inputs.input, multiple, disabled });
    }
    render() {
        super.render();
        this._file_pond = window.FilePond.create(this.input_el, {
            acceptedFileTypes: this.extensionsToMimeTypes(this.model.accepted_filetypes),
            allowMultiple: this.model.multiple,
            credits: false,
            disabled: this.model.disabled,
            maxFiles: this.model.max_files,
            maxFileSize: this.model.max_file_size,
            maxTotalFileSize: this.model.max_total_file_size,
            server: {
                process: (_, file, __, load, error, progress) => {
                    void this._process_upload(file, load, error, progress);
                },
                fetch: null,
                revert: (id, load) => {
                    this.model.trigger_event(new DeleteEvent({ name: id }));
                    load();
                },
            },
            stylePanelLayout: this.model.layout,
        });
    }
    async _process_upload(file, load, error, progress) {
        const buffer_size = this.model.chunk_size;
        const chunks = Math.ceil((file.size + 1) / buffer_size); // +1 is for empty files
        let abort_flag = false;
        new Promise(async (resolve, reject) => {
            for (let i = 0; i < chunks; i++) {
                if (abort_flag) {
                    reject(file.name);
                    return;
                }
                const start = i * buffer_size;
                const end = Math.min(start + buffer_size, file.size);
                this.model.trigger_event(new UploadEvent({
                    chunk: i + 1,
                    data: await file.slice(start, end).arrayBuffer(),
                    name: file._relativePath || file.name,
                    total_chunks: chunks,
                    type: file.type,
                }));
                progress(true, end, file.size);
            }
            load(file.name);
            resolve(file.name);
        }).catch(() => error("Upload failed."));
        return { abort: () => {
                abort_flag = true;
            } };
    }
}
export const DropperLayout = Enum("integrated", "compact", "circle");
export class FileDropper extends InputWidget {
    static __name__ = "FileDropper";
    static __module__ = "panel.models.file_dropper";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = FileDropperView;
        this.define(({ Any, List, Bool, Int, Nullable, Str }) => ({
            accepted_filetypes: [List(Str), []],
            chunk_size: [Int, 10000000],
            max_file_size: [Nullable(Str), null],
            max_files: [Nullable(Int), null],
            max_total_file_size: [Nullable(Str), null],
            mime_type: [Any, {}],
            multiple: [Bool, true],
            layout: [Nullable(DropperLayout), null],
            previews: [List(Str), ["image", "pdf"]],
        }));
    }
}
//# sourceMappingURL=file_dropper.js.map