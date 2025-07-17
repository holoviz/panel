import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"
import {HTMLBox, HTMLBoxView} from "./layout"

import type {Ace} from "ace-code"
import type * as AceCode from "ace-code"
declare const ace: typeof AceCode

import {ID} from "./util"

declare type ModeList = {
  getModeForPath(path: string): {mode: string}
}

export class AcePlotView extends HTMLBoxView {
  declare model: AcePlot

  protected _editor: Ace.Editor
  protected _langTools: unknown
  protected _modelist: ModeList
  protected _container: HTMLDivElement

  override connect_signals(): void {
    super.connect_signals()

    const {code, theme, language, filename, print_margin, annotations, soft_tabs, indent, readonly} = this.model.properties
    this.on_change(code, () => this._update_code_from_model())
    this.on_change(theme, () => this._update_theme())
    this.on_change(language, () => this._update_language())
    this.on_change(filename, () => this._update_filename())
    this.on_change(print_margin, () => this._update_print_margin())
    this.on_change(annotations, () => this._add_annotations())
    this.on_change(indent, () => this._editor.setOptions({tabSize: this.model.indent}))
    this.on_change(soft_tabs, () => this._editor.setOptions({useSoftTabs: this.model.soft_tabs}))
    this.on_change(readonly, () => {
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
        zIndex: "0",
      },
    })
    this.shadow_el.append(this._container)
    this._container.textContent = this.model.code
    this._editor = ace.edit(this._container)
    this._editor.renderer.attachToShadowRoot()
    this._langTools = (ace as any).require("ace/ext/language_tools")
    this._modelist = (ace as any).require("ace/ext/modelist")
    this._editor.setOptions({
      enableBasicAutocompletion: true,
      tabSize: this.model.indent,
      useSoftTabs: this.model.soft_tabs,
      enableSnippets: true,
      fontFamily: "monospace", //hack for cursor position
    })
    this._update_theme()
    this._update_filename()
    this._update_language()
    this._editor.setReadOnly(this.model.readonly)
    this._editor.setShowPrintMargin(this.model.print_margin)
    // if on keyup, update code from editor
    if (this.model.on_keyup) {
      this._editor.on("change", () => this._update_code_from_editor())
    } else {
      this._editor.on("blur", () => this._update_code_from_editor())
      this._editor.commands.addCommand({
        name: "updateCodeFromEditor",
        bindKey: {win: "Ctrl-Enter", mac: "Command-Enter"},
        exec: () => {
          this._update_code_from_editor()
        },
      })
    }
    this._editor.on("change", () => this._update_code_input_from_editor())
  }

  _update_code_from_model(): void {
    if (this._editor && this._editor.getValue() != this.model.code) {
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

  _update_code_input_from_editor(): void {
    if (this._editor.getValue() !=  this.model.code_input) {
      this.model.code_input = this._editor.getValue()
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
    code_input: p.Property<string>
    on_keyup: p.Property<boolean>
    language: p.Property<string>
    filename: p.Property<string | null>
    indent: p.Property<number>
    theme: p.Property<string>
    annotations: p.Property<any[]>
    print_margin: p.Property<boolean>
    readonly: p.Property<boolean>
    soft_tabs: p.Property<boolean>
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

    this.define<AcePlot.Props>(({Any, Bool, Int, List, Str, Nullable}) => ({
      annotations:  [ List(Any),      []  ],
      code:         [ Str,            ""  ],
      code_input:   [ Str,            ""  ],
      filename:     [ Nullable(Str), null ],
      indent:       [ Int,              4 ],
      language:     [ Str,             "" ],
      on_keyup:     [ Bool,          true ],
      print_margin: [ Bool,         false ],
      theme:        [ Str, "github_light_default" ],
      readonly:     [ Bool,         false ],
      soft_tabs:    [ Bool,         false ],
    }))

    this.override<AcePlot.Props>({
      height: 300,
      width: 300,
    })
  }
}
