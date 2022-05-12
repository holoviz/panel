import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import { div } from "@bokehjs/core/dom";

import {PanelHTMLBoxView} from "./layout"

function ID() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return '_' + Math.random().toString(36).substr(2, 9);
}


export class AcePlotView extends PanelHTMLBoxView {
  model: AcePlot
  protected _editor: any
  protected _langTools: any
  protected _modelist: any
  protected _container: HTMLDivElement

  initialize(): void {
    super.initialize()
    this._container = div({
      id: ID(),
      style: {
        width: "100%",
        height: "100%",
        zIndex: 0,
      }
    })
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.code.change, () => this._update_code_from_model())
    this.connect(this.model.properties.theme.change, () => this._update_theme())
    this.connect(this.model.properties.language.change, () => this._update_language())
    this.connect(this.model.properties.filename.change, () => this._update_filename())
    this.connect(this.model.properties.print_margin.change, () => this._update_print_margin())
    this.connect(this.model.properties.annotations.change, () => this._add_annotations())
    this.connect(this.model.properties.readonly.change, () => {
      this._editor.setReadOnly(this.model.readonly)
    })
  }

  render(): void {
    super.render()
    if (!(this._container === this.el.childNodes[0]))
      this.el.appendChild(this._container)
      this._container.textContent = this.model.code
      this._editor = (window as any).ace.edit(this._container.id)
      this._langTools = (window as any).ace.require('ace/ext/language_tools')
      this._modelist = (window as any).ace.require("ace/ext/modelist")
      this._editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        fontFamily: "monospace", //hack for cursor position
      });
      this._update_theme()
      this._update_filename()
      this._update_language()
      this._editor.setReadOnly(this.model.readonly)
      this._editor.setShowPrintMargin(this.model.print_margin);
      this._editor.on('change', () => this._update_code_from_editor())
  }

  _update_code_from_model(): void {
    if (this._editor && this._editor.getValue() !=  this.model.code)
      this._editor.setValue(this.model.code)
  }

  _update_print_margin(): void {
    this._editor.setShowPrintMargin(this.model.print_margin);
  }

  _update_code_from_editor(): void {
    if(this._editor.getValue() !=  this.model.code){
      this.model.code = this._editor.getValue()
    }
  }

  _update_theme(): void {
    this._editor.setTheme("ace/theme/" + `${this.model.theme}`)
  }

  _update_filename(): void {
    if (this.model.filename) {
      const mode = this._modelist.getModeForPath(this.model.filename).mode
      this.model.language = mode.slice(9)
    }
  }

  _update_language(): void{
    if (this.model.language != null) {
      this._editor.session.setMode("ace/mode/" + `${this.model.language}`)
    }
  }

  _add_annotations(): void{
    this._editor.session.setAnnotations(this.model.annotations)
  }

  after_layout(): void{
    super.after_layout()
    this._editor.resize()
  }
}

export namespace AcePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    code: p.Property<string>
    language: p.Property<string>
    filename: p.Property<string>
    theme: p.Property<string>
    annotations: p.Property<any[]>
    print_margin: p.Property<boolean>
    readonly: p.Property<boolean>
  }
}

export interface AcePlot extends AcePlot.Attrs {}

export class AcePlot extends HTMLBox {
  properties: AcePlot.Props

  constructor(attrs?: Partial<AcePlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.ace"

  static init_AcePlot(): void {
    this.prototype.default_view = AcePlotView

    this.define<AcePlot.Props>(({Any, Array, Boolean, String}) => ({
      code:         [ String,       '' ],
      filename:     [ String           ],
      language:     [ String           ],
      theme:        [ String, 'chrome' ],
      annotations:  [ Array(Any),   [] ],
      readonly:     [ Boolean,   false ],
      print_margin: [ Boolean,   false ]
    }))

    this.override<AcePlot.Props>({
      height: 300,
      width: 300
    })
  }
}
