import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"
import { div } from 'core/dom';

function ID() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return '_' + Math.random().toString(36).substr(2, 9);
}


export class AcePlotView extends HTMLBoxView {
  model: AcePlot
  protected _ace: any
  protected _editor: any
  protected _langTools: any
  protected _container: HTMLDivElement

  initialize(): void {
    super.initialize()
    this._ace = (window as any).ace
    this._container = div({
      id: ID(),
      style: {
        width: "100%",
        height: "100%"
      }
    })
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.code.change, () => this._update_code_from_model())
    this.connect(this.model.properties.theme.change, () => this._update_theme())
    this.connect(this.model.properties.language.change, () => this._update_language())
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
      this._editor = this._ace.edit(this._container.id)
      this._editor.setTheme("ace/theme/" + `${this.model.theme}`)
      this._editor.session.setMode("ace/mode/" + `${this.model.language}`)
      this._editor.setReadOnly(this.model.readonly)
      this._langTools = this._ace.require('ace/ext/language_tools')
      this._editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        fontFamily: "monospace", //hack for cursor position
      });
      this._editor.on('change', () => this._update_code_from_editor())
  }

  _update_code_from_model(): void {
    if (this._editor && this._editor.getValue() !=  this.model.code)
      this._editor.setValue(this.model.code)
  }

  _update_code_from_editor(): void {
    if(this._editor.getValue() !=  this.model.code){
      this.model.code = this._editor.getValue()
    }
  }

  _update_theme(): void{
    this._editor.setTheme("ace/theme/" + `${this.model.theme}`)
  }

  _update_language(): void{
    this._editor.session.setMode("ace/mode/" + `${this.model.language}`)
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
    theme: p.Property<string>
    annotations: p.Property<any[]>
    readonly: p.Property<boolean>
  }
}

export interface AcePlot extends AcePlot.Attrs {}

export class AcePlot extends HTMLBox {
  properties: AcePlot.Props

  constructor(attrs?: Partial<AcePlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "AcePlot"
    this.prototype.default_view = AcePlotView

    this.define<AcePlot.Props>({
      code:        [ p.String            ],
      language:    [ p.String,  'python' ],
      theme:       [ p.String,  'chrome' ],
      annotations: [ p.Array,   []       ],
      readonly:    [ p.Boolean, false    ]
    })

    this.override({
      height: 300,
      width: 300
    })
  }
}
AcePlot.initClass()
