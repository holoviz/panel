import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {HTMLBox, HTMLBoxView} from "./layout"

import type {Ace} from "ace-code"
import type * as AceCode from "ace-code"
declare const ace: typeof AceCode

import {ID} from "./util"

import ace_css from "styles/models/ace.css"

type Marker = {
  start_row: number
  end_row?: number
  start_column?: number
  end_column?: number
  class?: string | null
  gutter_class?: string | null
  type?: "fullLine" | "screenLine" | "text"
}

declare type ModeList = {
  getModeForPath(path: string): {mode: string}
}

export class AcePlotView extends HTMLBoxView {
  declare model: AcePlot

  protected _editor: Ace.Editor
  protected _langTools: unknown
  protected _modelist: ModeList
  protected _container: HTMLDivElement
  protected _marker_ids: number[] = []
  protected _gutter_marks: [number, string][] = []

  override connect_signals(): void {
    super.connect_signals()

    const {code, theme, language, filename, print_margin, annotations, markers, soft_tabs, indent, readonly, keyboard_accessible, soft_wrap} = this.model.properties
    this.on_change(code, () => this._update_code_from_model())
    this.on_change(theme, () => this._update_theme())
    this.on_change(language, () => this._update_language())
    this.on_change(filename, () => this._update_filename())
    this.on_change(print_margin, () => this._update_print_margin())
    this.on_change(annotations, () => this._add_annotations())
    this.on_change(markers, () => this._update_markers())
    this.on_change(indent, () => this._editor.setOptions({tabSize: this.model.indent}))
    this.on_change(soft_tabs, () => this._editor.setOptions({useSoftTabs: this.model.soft_tabs}))
    this.on_change(keyboard_accessible, () => this._editor.setOptions({enableKeyboardAccessibility: this.model.keyboard_accessible}))
    this.on_change(soft_wrap, () => this._editor.setOptions({wrap: this.model.soft_wrap}))
    this.on_change(readonly, () => this._update_readonly())
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), ace_css]
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
      enableKeyboardAccessibility: this.model.keyboard_accessible,
      wrap: this.model.soft_wrap,
      enableSnippets: true,
      fontFamily: "monospace", //hack for cursor position
    })
    this._update_theme()
    this._update_filename()
    this._update_language()
    this._update_readonly()
    this._marker_ids = []
    this._gutter_marks = []
    this._update_markers()
    this._editor.setShowPrintMargin(this.model.print_margin)
    const {on_keyup} = this.model
    this._editor.on("change", () => {
      // code_input must reach the server before code: the server copies
      // value into value_input, so a trailing code_input could overwrite
      // a newer value_input set from Python.
      this._update_code_input_from_editor()
      if (on_keyup) {
        this._update_code_from_editor()
      }
    })
    if (!on_keyup) {
      this._editor.on("blur", () => this._update_code_from_editor())
      this._editor.commands.addCommand({
        name: "updateCodeFromEditor",
        bindKey: {win: "Ctrl-Enter", mac: "Command-Enter"},
        exec: () => {
          this._update_code_from_editor()
        },
      })
    }
  }

  _update_code_from_model(): void {
    if (this._editor && this._editor.getValue() != this.model.code) {
      // Save the current cursor position
      const cursorPosition = this._editor.getCursorPosition()
      const scrollTop = this._editor.session.getScrollTop()
      const scrollLeft = this._editor.session.getScrollLeft()

      // Update the value without selecting all text
      // The second parameter (-1) keeps cursor where it is
      this._editor.setValue(this.model.code, -1)

      // Restore cursor position only if it's valid in the new content
      const newRowCount = this._editor.session.getLength()
      if (cursorPosition.row < newRowCount) {
        const newRowLength = this._editor.session.getLine(cursorPosition.row).length
        const newColumn = Math.min(cursorPosition.column, newRowLength)
        this._editor.moveCursorToPosition({row: cursorPosition.row, column: newColumn})
      } else {
        // If the cursor was beyond the new document length, move to end
        this._editor.moveCursorToPosition({row: newRowCount - 1, column: this._editor.session.getLine(newRowCount - 1).length})
      }
      this._editor.clearSelection()
      this._editor.session.setScrollTop(scrollTop)
      this._editor.session.setScrollLeft(scrollLeft)
    }
  }

  _update_readonly(): void {
    this._editor.setReadOnly(this.model.readonly)
    // Ace creates the "Editing is disabled" tooltip on document.body, outside
    // the shadow root holding Ace's CSS, unless the editor already has one.
    // It drops the tooltip whenever read-only is turned off, so attach a new
    // one to the shadow root each time it is turned on.
    const editor = this._editor as any
    if (this.model.readonly && editor.hoverTooltip == null) {
      const {HoverTooltip} = (ace as any).require("ace/tooltip")
      editor.hoverTooltip = new HoverTooltip(this.shadow_el)
    }
  }

  _update_markers(): void {
    const session = this._editor.session
    for (const id of this._marker_ids) {
      session.removeMarker(id)
    }
    for (const [row, cls] of this._gutter_marks) {
      session.removeGutterDecoration(row, cls)
    }
    this._marker_ids = []
    this._gutter_marks = []
    const {Range} = (ace as any).require("ace/range")
    for (const marker of this.model.markers as Marker[]) {
      const start = marker.start_row
      if (typeof start !== "number") {
        continue
      }
      const end = marker.end_row ?? start
      const cls = marker.class === undefined ? "pn-ace-marker" : marker.class
      if (cls != null && cls !== "") {
        const type = marker.type ?? "fullLine"
        const range = type === "text"
          ? new Range(start, marker.start_column ?? 0, end, marker.end_column ?? Infinity)
          : new Range(start, 0, end, Infinity)
        this._marker_ids.push(session.addMarker(range, cls, type, false))
      }
      if (marker.gutter_class != null && marker.gutter_class !== "") {
        for (let row = start; row <= end; row++) {
          session.addGutterDecoration(row, marker.gutter_class)
          this._gutter_marks.push([row, marker.gutter_class])
        }
      }
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
    if (this._editor) {
      this._editor.setTheme(`ace/theme/${this.model.theme}`)
    }
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
      // Re-apply annotations after mode change, since setMode may
      // spawn a new worker that would overwrite user annotations.
      this._add_annotations()
    }
  }

  _add_annotations(): void {
    // Toggle the Ace worker BEFORE setting annotations, because
    // disabling the worker clears the session's annotations.
    this._editor.session.setUseWorker(this.model.annotations.length === 0)
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
    markers: p.Property<any[]>
    filename: p.Property<string | null>
    indent: p.Property<number>
    keyboard_accessible: p.Property<boolean>
    theme: p.Property<string>
    annotations: p.Property<any[]>
    print_margin: p.Property<boolean>
    readonly: p.Property<boolean>
    soft_tabs: p.Property<boolean>
    soft_wrap: p.Property<boolean>
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
      keyboard_accessible: [ Bool,         false ],
      language:     [ Str,             "" ],
      markers:      [ List(Any),      []  ],
      on_keyup:     [ Bool,          true ],
      print_margin: [ Bool,         false ],
      theme:        [ Str, "github_light_default" ],
      readonly:     [ Bool,         false ],
      soft_tabs:    [ Bool,         false ],
      soft_wrap:    [ Bool,         false ],
    }))

    this.override<AcePlot.Props>({
      height: 300,
      width: 300,
    })
  }
}
