import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"
import {HTMLBox, HTMLBoxView} from "./layout"

import type {Ace} from "ace-code"
import type * as AceCode from "ace-code"
declare const ace: typeof AceCode

declare type ModeList = {
  getModeForPath(path: string): {mode: string}
}

function ID() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  const id = Math.random().toString(36).substr(2, 9)
  return `_${id}`
}

export class AcePlotView extends HTMLBoxView {
  declare model: AcePlot

  protected _editor: Ace.Editor
  protected _langTools: unknown
  protected _modelist: ModeList
  protected _container: HTMLDivElement

  override connect_signals(): void {
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

  override render(): void {
    super.render()

    this._container = div({
      id: ID(),
      style: {
        width: "100%",
        height: "100%",
        zIndex: 0,
      },
    })
    this.shadow_el.append(this._container)
    this._container.textContent = this.model.code
    this._editor = ace.edit(this._container)
    this._editor.renderer.attachToShadowRoot()
    this._langTools = ace.require("ace/ext/language_tools")
    this._modelist = ace.require("ace/ext/modelist")
    this._editor.setOptions({
      enableBasicAutocompletion: true,
      enableSnippets: true,
      fontFamily: "monospace", //hack for cursor position
    })
    this._update_theme()
    this._update_filename()
    this._update_language()
    this._editor.setReadOnly(this.model.readonly)
    this._editor.setShowPrintMargin(this.model.print_margin)
    this._editor.on("change", () => this._update_code_from_editor())
  }

  _update_code_from_model(): void {
    if (this._editor && this._editor.getValue() !=  this.model.code) {
      this._editor.setValue(this.model.code)
    }
  }

  _update_print_margin(): void {
    this._editor.setShowPrintMargin(this.model.print_margin)
  }

  _update_code_from_editor(): void {
    if (this._editor.getValue() !=  this.model.code) {
      this.model.code = this._editor.getValue()
    }
  }

  _update_theme(): void {
    this._editor.setTheme(`ace/theme/${this.model.theme}`)
  }

  _update_filename(): void {
    if (this.model.filename) {
      const mode = this._modelist.getModeForPath(this.model.filename).mode
      this.model.language = mode.slice(9)
    }
  }

  _update_language(): void {
    if (this.model.language != null) {
      this._editor.session.setMode(`ace/mode/${this.model.language}`)
    }
  }

  _add_annotations(): void {
    this._editor.session.setAnnotations(this.model.annotations)
  }

  override after_layout(): void {
    super.after_layout()
    if (this._editor !== undefined) {
      this._editor.resize()
    }
  }
}

export namespace AcePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    code: p.Property<string>
    language: p.Property<string>
    filename: p.Property<string | null>
    theme: p.Property<string>
    annotations: p.Property<any[]>
    print_margin: p.Property<boolean>
    readonly: p.Property<boolean>
  }
}

export interface AcePlot extends AcePlot.Attrs {}

export class AcePlot extends HTMLBox {
  declare properties: AcePlot.Props

  constructor(attrs?: Partial<AcePlot.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.ace"

  static {
    this.prototype.default_view = AcePlotView

    this.define<AcePlot.Props>(({Any, List, Bool, Str, Nullable}) => ({
      code:         [ Str,       "" ],
      filename:     [ Nullable(Str), null],
      language:     [ Str,       "" ],
      theme:        [ Str, "chrome" ],
      annotations:  [ List(Any),   [] ],
      readonly:     [ Bool,   false ],
      print_margin: [ Bool,   false ],
    }))

    this.override<AcePlot.Props>({
      height: 300,
      width: 300,
    })
  }
}
