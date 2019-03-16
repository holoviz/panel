import * as p from "core/properties"
import {Widget, WidgetView} from "models/widgets/widget"

export class FileInputView extends WidgetView {
  model: FileInput

  protected dialogEl: HTMLInputElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.change, () => this.render())
    this.connect(this.model.properties.value.change, () => this.render())
    this.connect(this.model.properties.width.change, () => this.render())
  }

  render(): void {
    if (this.dialogEl) {
      return
    }
    this.dialogEl = document.createElement('input')
    this.dialogEl.type = "file";
    this.dialogEl.multiple = false;
    this.dialogEl.style.width = `{this.model.width}px`;
    this.dialogEl.onchange = (e) => this.load_file(e);
    this.el.appendChild(this.dialogEl)
  }

  load_file(e: any): void {
    const reader = new FileReader();
    reader.onload = (e) => this.set_value(e)
    reader.readAsDataURL(e.target.files[0])
  }

  set_value(e: any): void {
    this.model.value = e.target.result;
  }
}

export namespace FileInput {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Widget.Props & {
    value: p.Property<any>
  }
}

export interface FileInput extends FileInput.Attrs {}

export abstract class FileInput extends Widget {

  properties: FileInput.Props

  constructor(attrs?: Partial<FileInput.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "FileInput"
    this.prototype.default_view = FileInputView

    this.define<FileInput.Props>({
      value: [ p.Any,         ''            ],
    })
  }
}

FileInput.initClass()
