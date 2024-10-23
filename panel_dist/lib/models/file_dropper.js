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
export class FileDropperView extends InputWidgetView {
    static __name__ = "FileDropperView";
    _file_pond = null;
    _transfer_in_process = null;
    initialize() {
        super.initialize();
        window.FilePond.registerPlugin(window.FilePondPluginImagePreview);
        window.FilePond.registerPlugin(window.FilePondPluginPdfPreview);
        window.FilePond.registerPlugin(window.FilePondPluginFileValidateType);
        window.FilePond.registerPlugin(window.FilePondPluginFileValidateSize);
    }
    connect_signals() {
        super.connect_signals();
        const { disabled, layout, max_file_size, max_files, max_total_file_size, multiple } = this.model.properties;
        this.on_change([disabled, max_file_size, max_files, max_total_file_size, multiple, layout], () => {
            this._file_pond?.setOptions({
                acceptedFileTypes: this.model.accepted_filetypes,
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
            acceptedFileTypes: this.model.accepted_filetypes,
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
        }));
    }
}
//# sourceMappingURL=file_dropper.js.map