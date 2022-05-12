import * as p from "@bokehjs/core/properties"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {PanelHTMLBoxView} from "./layout"

export class JSONEditEvent extends ModelEvent {
  event_name: string = "json_edit"

  constructor(readonly data: any) {
    super()
  }

  protected _to_json(): JSON {
    return {model: this.origin, data: this.data}
  }
}


export class JSONEditorView extends PanelHTMLBoxView {
  model: JSONEditor
  editor: any
  _menu_context: any

  connect_signals(): void {
    super.connect_signals()
    const {data, disabled, templates, menu, mode, search, schema} = this.model.properties
    this.on_change([data], () => this.editor.update(this.model.data))
    this.on_change([templates], () => {
      this.editor.options.templates = this.model.templates
    })
    this.on_change([menu], () => {
      this.editor.options.menu = this.model.menu
    })
    this.on_change([search], () => {
      this.editor.options.search = this.model.search
    })
    this.on_change([schema], () => {
      this.editor.options.schema = this.model.schema
    })
    this.on_change([disabled, mode], () => {
      const mode = this.model.disabled ? 'view': this.model.mode;
      this.editor.setMode(mode)
    })
  }

  override remove(): void {
    super.remove()
    this.editor.destroy()
  }

  render(): void {
    super.render();
    const mode = this.model.disabled ? 'view': this.model.mode;
    this.editor = new (window as any).JSONEditor(this.el, {
      menu: this.model.menu,
      mode: mode,
      onChangeJSON: (json: any) => {
	this.model.data = json
      },
      onSelectionChange: (start: any, end: any) => {
	this.model.selection = [start, end]
      },
      search: this.model.search,
      schema: this.model.schema,
      templates: this.model.templates,
    });
    this.editor.set(this.model.data);
  }
}

export namespace JSONEditor {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    menu: p.Property<boolean>
    mode: p.Property<string>
    search: p.Property<boolean>
    selection: p.Property<any[]>
    schema: p.Property<any>
    templates: p.Property<any[]>
  }
}

export interface JSONEditor extends JSONEditor.Attrs {}

export class JSONEditor extends HTMLBox {
  properties: JSONEditor.Props

  constructor(attrs?: Partial<JSONEditor.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.json_editor"

  static init_JSONEditor(): void {
    this.prototype.default_view = JSONEditorView
    this.define<JSONEditor.Props>(({Any, Array, Boolean, String}) => ({
      data:      [ Any,          {} ],
      mode:      [ String,   'tree' ],
      menu:      [ Boolean,    true ],
      search:    [ Boolean,    true ],
      selection: [ Array(Any),   [] ],
      schema:    [ Any,        null ],
      templates: [ Array(Any),   [] ],
    }))
  }
}
