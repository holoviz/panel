import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {TableColumn} from "@bokehjs/models/widgets/tables"

import {transform_cds_to_records} from "./data"
import {PanelHTMLBoxView, set_size} from "./layout"


declare const Tabulator: any;

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class DataTabulatorView extends PanelHTMLBoxView {
  model: DataTabulator;
  tabulator: any;
  _tabulator_cell_updating: boolean=false;
  // objectElement: any // Element

  connect_signals(): void {
    super.connect_signals()

    this.connect(this.model.properties.configuration.change, () => {
      this.render();
    })

    this.connect(this.model.properties.columns.change, () => {
      this.tabulator.setColumns(this.model.columns);
    })

    // this.connect(this.model.source.change, () => this.setData())
    this.connect(this.model.source.properties.data.change, () => {
      this.setData();
    })
    this.connect(this.model.source.streaming, () => this.addData())
    this.connect(this.model.source.patching, () => this.updateOrAddData())

    // this.connect(this.model.source.selected.change, () => this.updateSelection())
    this.connect(this.model.source.selected.properties.indices.change, () => this.updateSelection())
  }

  render(): void {
    super.render()
    const container = div({class: "pnx-tabulator"});
    set_size(container, this.model)
    let configuration = this.getConfiguration();
    this.tabulator = new Tabulator(container, configuration)
    this.el.appendChild(container)
    // this.objectElement.addEventListener("click", () => {this.model.clicks+=1;}, false)
  }

  getConfiguration(): any {
    // I refer to this via _view because this is the tabulator element when cellEdited is used
    let _view = this;

    function rowSelectionChanged(data: any, _: any): void {
      let indices: any = data.map((row: any) => row.index)
      _view.model.source.selected.indices = indices;
    }

    function startUpdating(): void {
      _view._tabulator_cell_updating = true;
    }
    function endUpdating(): void {
      _view._tabulator_cell_updating = false;
    }
    function cellEdited(cell: any){
      const field = cell._cell.column.field;
      const index = cell._cell.row.data.index;
      const value = cell._cell.value;
      startUpdating();
      _view.model.source.patch({[field]: [[index, value]]});
      endUpdating();
    }
    let configuration = {
      ...this.model.configuration,
	  rowSelectionChanged: rowSelectionChanged,
      cellEdited: cellEdited,
      columns: this.getColumns(),
      layout: this.model.layout
    }
    console.log(configuration)
    let data = this.model.source;
    if (data === null || Object.keys(data.data).length===0)
      return configuration;
    else {
      data = transform_cds_to_records(data)
      return {
        ...configuration,
        "data": data,
      }
    }
  }

  getColumns(): any {
	let columns = []
	let ordered = false
    if (this.model.configuration.columns != null) {
      columns = this.model.configuration.columns
	  ordered = true
    }
    for (const column of this.model.columns) {
      let tab_column: any = null
      for (const col of columns) {
        if (col.columns != null) {
          for (const c of col.columns) {
            if (column.field === c.field)
              tab_column = c
              break
          }
          if (tab_column != null)
            break
        } else if (column.field === col.field) {
          tab_column = col
          break
        }
      }
      if (tab_column == null) {
        tab_column = {
          field: column.field,
          title: column.title,
          width: column.width,
        }
      }
      if (column.formatter != null && tab_column.formatter == null) {
        tab_column.formatter = (cell: any) => {
          return column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, null)
        }
      }
      const editor: any = column.editor
      const ctype = editor.type
      if (ctype === "StringEditor") {
        if (editor.completions) {
          tab_column.editor = "autocomplete"
          tab_column.editorParams = {values: editor.completions}
        } else
          tab_column.editor = "input"
      } else if (ctype === "TextEditor")
        tab_column.editor = "textarea"
      else if (ctype === "IntEditor" || ctype === "NumberEditor") {
        tab_column.editor = "number"
        tab_column.editorParams = {step: editor.step}
      } else if (ctype === "CheckboxEditor") {
        tab_column.editor = "tickCross"
      } else if (ctype === "SelectEditor") {
        tab_column.editor = "select"
        tab_column.editorParams = {values: editor.options}
      }
      if (!ordered)
        columns.push(tab_column)
    }
    return columns
  }

  after_layout(): void {
    super.after_layout()
    this.tabulator.redraw(true);
  }

  setData(): void {
    let data = transform_cds_to_records(this.model.source);
    this.tabulator.setData(data);
  }

  addData(): void {
    let data = transform_cds_to_records(this.model.source);
    this.tabulator.setData(data);
  }

  updateOrAddData(): void {
    // To avoid double updating the tabulator data
    if (this._tabulator_cell_updating)
      return

    let data = transform_cds_to_records(this.model.source);
    this.tabulator.setData(data);
  }

  updateSelection(): void {
    if (this.tabulator==null)
      return

    let indices: number[]= this.model.source.selected.indices;
    let selectedRows: any = this.tabulator.getSelectedRows();

    for (let row of selectedRows){
      if (!indices.includes(row.getData().index))
        row.toggleSelect();
    }

    for (let index of indices){
    // Improve this
    // Maybe tabulator should use id as index?
      this.tabulator.selectRow(index);
    }
  }
}

export namespace DataTabulator {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
  columns: p.Property<TableColumn[]>
  configuration: p.Property<any>
  layout: p.Property<"fit_data" | "fit_data_fill" | "fit_data_stretch" | "fit_data_table" | "fit_columns">
  source: p.Property<ColumnDataSource>,
  }
}

export interface DataTabulator extends DataTabulator.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class DataTabulator extends HTMLBox {
  properties: DataTabulator.Props

  constructor(attrs?: Partial<DataTabulator.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.tabulator"

  static init_DataTabulator(): void {
    this.prototype.default_view = DataTabulatorView;

    this.define<DataTabulator.Props>({
      configuration: [p.Any, ],
      columns: [ p.Array, [] ],
      layout: [ p.Any, "fit_columns" ],
      source: [ p.Any, ],
    })
  }
}
