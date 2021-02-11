import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {PanelHTMLBoxView} from "./layout"

export class JSONEditorView extends PanelHTMLBoxView {
  model: JSONEditor
  editor: any
  _menu_context: any

  connect_signals(): void {
    super.connect_signals()
    const {data, templates} = this.model.properties
    this.on_change([data], () => this.editor.update(this.model.data))
    this.on_change([templates], () => {
      this.editor.options.templates = this.model.templates
      if (this._menu_context) {
	let node = this._menu_context.node;
	node = this._menu_context.type === 'append' ? node.append : node
	console.log(this._menu_context)
	node.showContextMenu(node.dom.menu)
	this._menu_context = null
      }
    })
  }

  render(): void {
    super.render();
    this.editor = new (window as any).JSONEditor(this.el, {
      mode: 'tree',
      autocomplete: {
	trigger: focus,
	getOptions: async (text: string, path: string[], input: string) => {
	  this.model.query = {text, path, input, type: 'autocomplete'}
	  const result = await this._result_available()
	  this.model.result = null
	  return result
	}
      },
      onCreateMenu: (items: any[], node: any) => {
	let current_node = this.editor.node
	for (const path of node.path) {
	  if (current_node.type === 'array')
	    current_node = current_node.childs[path]
	  else {
	    for (const child of current_node.childs) {
	      if (child.field === path) {
		current_node = child;
		break;
	      }
	    }
	  }
	}
	this._menu_context = {type: node.type, node: current_node}
	this.model.query = {type: 'append', node}
	return items
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

  async _result_available(): Promise<any[]> {
    return new Promise(resolve => {
      const start_time = Date.now();
      const checkFlag = () => {
	if (this.model.result != null) {
          resolve(this.model.result);
	} else if (Date.now() > start_time + 3000) {
          resolve([]);
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
