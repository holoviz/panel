import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {PanelHTMLBoxView} from "./layout"

export class JSONEditorView extends PanelHTMLBoxView {
  model: JSONEditor
  editor: any

  connect_signals(): void {
    super.connect_signals()
    const {data, templates} = this.model.properties
    this.on_change([data], () => this.editor.update(this.model.data))
    this.on_change([templates], () => { this.editor.options.templates = this.model.templates })
  }

  render(): void {
    super.render();
    this.editor = new (window as any).JSONEditor(this.el, {
      mode: 'tree',
      autocomplete: {
	trigger: focus,
	getOptions: async (text: string, path: string[], input: string) => {
	  this.model.query = {text, path, input, type: 'autocomplete'}
	  await this._result_available()
	  const result = this.model.result
	  this.model.result = null
	  return result
	}
      },
      onCreateMenu: (items: any[], node: any) => {
	if (node.type == 'append') {
	  this.model.query = {type: 'append', node}
	}
	return itemsx
      },
      onChangeJSON: (json: any) => {
	this.model.data = json
      },
      onSelectionChange: (start: any, end: any) => {
	this.model.selection = [start, end];
      },
      templates: this.model.templates,
      search: this.model.search
    });
    this.editor.set(this.model.data);
  }

  async _result_available(): Promise<void> {
    return new Promise(resolve => {
      const start_time = Date.now();
      const checkFlag = () => {
	if (this.model.result != null) {
          resolve();
	} else if (Date.now() > start_time + 3000) {
          resolve();
	} else {
          window.setTimeout(checkFlag, 50); 
	}
      }
      checkFlag();
    });
  }
}

export namespace JSONEditor {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    search: p.Property<boolean>
    selection: p.Property<any[]>
    templates: p.Property<any[]>
    result: p.Property<any>
    query: p.Property<any>
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
    this.define<JSONEditor.Props>(({Any, Array, Boolean}) => ({
      data:      [ Any,          {} ],
      search:    [ Boolean,    true ],
      selection: [ Array(Any),   [] ],
      templates: [ Array(Any),   [] ],
      query:     [ Any,        null ],
      result:    [ Any,        null ]
    }))
  }
}
