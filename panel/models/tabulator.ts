import {undisplay} from "@bokehjs/core/dom"
import {isArray} from "@bokehjs/core/util/types"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {div} from "@bokehjs/core/dom"
import {Enum} from "@bokehjs/core/kinds"
import * as p from "@bokehjs/core/properties";
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {TableColumn} from "@bokehjs/models/widgets/tables"
import {Attrs} from "@bokehjs/core/types"

import {debounce} from "debounce"

import {comm_settings} from "./comm_manager"
import {transform_cds_to_records} from "./data"
import {HTMLBox, HTMLBoxView} from "./layout"

export class TableEditEvent extends ModelEvent {
  constructor(readonly column: string, readonly row: number, readonly pre: boolean) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, column: this.column, row: this.row, pre: this.pre}
  }

  static {
    this.prototype.event_name = "table-edit"
  }
}

export class CellClickEvent extends ModelEvent {
  constructor(readonly column: string, readonly row: number) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, column: this.column, row: this.row}
  }

  static {
    this.prototype.event_name = "cell-click"
  }
}

declare const Tabulator: any;

function find_group(key: any, value: string, records: any[]): any {
  for (const record of records) {
    if (record[key] == value)
      return record
  }
  return null
}

function summarize(grouped: any[], columns: any[], aggregators: string[], depth: number = 0): any {
  const summary: any = {}
  if (grouped.length == 0)
    return summary
  const agg = aggregators[depth]
  for (const group of grouped) {
    const subsummary = summarize(group._children, columns, aggregators, depth+1)
    for (const col in subsummary) {
      if (isArray(subsummary[col]))
        group[col] = subsummary[col].reduce((a: any, b: any) => a + b, 0) / subsummary[col].length
      else
        group[col] = subsummary[col]
    }
    for (const column of columns.slice(1)) {
      const val = group[column.field]
      if (column.field in summary) {
        const old_val = summary[column.field]
        if (agg === 'min')
          summary[column.field] = Math.min(val, old_val)
        else if (agg === 'max')
          summary[column.field] = Math.max(val, old_val)
        else if (agg === 'sum')
          summary[column.field] = val + old_val
        else if (agg === 'mean') {
          if (isArray(summary[column.field]))
            summary[column.field].push(val)
          else
            summary[column.field] = [old_val, val]
        }
      } else
        summary[column.field] = val
    }
  }
  return summary
}

function group_data(records: any[], columns: any[], indexes: string[], aggregators: any): any[] {
  const grouped = []
  const index_field = columns[0].field
  for (const record of records) {
    const value = record[indexes[0]]
    let group = find_group(index_field, value, grouped)
    if (group == null) {
      group = {_children: []}
      group[index_field] = value
      grouped.push(group)
    }
    let subgroup = group
    const groups: any = {}
    for (const index of indexes.slice(1)) {
      subgroup = find_group(index_field, record[index], subgroup._children)
      if (subgroup == null) {
        subgroup = {_children: []}
        subgroup[index_field] = record[index]
        group._children.push(subgroup)
      }
      groups[index] = group
      for (const column of columns.slice(1))
        subgroup[column.field] = record[column]
      group = subgroup
    }
    for (const column of columns.slice(1))
      subgroup[column.field] = record[column.field]
  }
  const aggs = []
  for (const index of indexes)
    aggs.push((index in aggregators) ? aggregators[index] : 'sum')
  summarize(grouped, columns, aggs)
  return grouped
}


const timestampSorter = function(a: any, b: any, _aRow: any, _bRow: any, _column: any, _dir: any, _params: any){
  // Bokeh serializes datetime objects as UNIX timestamps.

  //a, b - the two values being compared
  //aRow, bRow - the row components for the values being compared (useful if you need to access additional fields in the row data for the sort)
  //column - the column component for the column being sorted
  //dir - the direction of the sort ("asc" or "desc")
  //sorterParams - sorterParams object from column definition array

  // Added an _ in front of some parameters as they're unused and the Typescript compiler was complaining about it.

  // const alignEmptyValues = params.alignEmptyValues
  let emptyAlign: any
  emptyAlign = 0

  const opts = {zone: new (window as any).luxon.IANAZone('UTC')}

  // NaN values are serialized to -9223372036854776 by Bokeh

  if (String(a) == '-9223372036854776') {
    a = (window as any).luxon.DateTime.fromISO('invalid')
  } else {
    a = (window as any).luxon.DateTime.fromMillis(a, opts)
  }
  if (String(b) == '-9223372036854776') {
    b = (window as any).luxon.DateTime.fromISO('invalid')
  } else {
    b = (window as any).luxon.DateTime.fromMillis(b, opts)
  }

  if(!a.isValid){
    emptyAlign = !b.isValid ? 0 : -1;
  }else if(!b.isValid){
    emptyAlign =  1;
  }else{
    //compare valid values
    return a - b;
  }

  // Invalid (e.g. NaN) always at the bottom
  emptyAlign *= -1

  return emptyAlign;
}


const dateEditor = function(cell: any, onRendered: any, success: any, cancel: any) {
  //cell - the cell component for the editable cell
  //onRendered - function to call when the editor has been rendered
  //success - function to call to pass the successfully updated value to Tabulator
  //cancel - function to call to abort the edit and return to a normal cell

  //create and style input
  const rawValue = cell.getValue()
  const opts = {zone: new (window as any).luxon.IANAZone('UTC')}
  let cellValue: any
  if (rawValue === 'NaN' || rawValue === null)
    cellValue = null
  else
    cellValue = (window as any).luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd")
  const input = document.createElement("input")

  input.setAttribute("type", "date");

  input.style.padding = "4px";
  input.style.width = "100%";
  input.style.boxSizing = "border-box";

  input.value = cellValue;

  onRendered(() => {
    input.focus();
    input.style.height = "100%";
  });

  function onChange() {
    const new_val = (window as any).luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd", opts).toMillis()
    if (new_val != cellValue)
      success(new_val)
    else
      cancel()
  }

  //submit new value on blur or change
  input.addEventListener("blur", onChange);

  //submit new value on enter
  input.addEventListener("keydown", function(e){
    if(e.keyCode == 13)
      onChange()

    if(e.keyCode == 27)
      cancel()
  });

  return input;
};



const datetimeEditor = function(cell: any, onRendered: any, success: any, cancel: any) {
  //cell - the cell component for the editable cell
  //onRendered - function to call when the editor has been rendered
  //success - function to call to pass the successfully updated value to Tabulator
  //cancel - function to call to abort the edit and return to a normal cell

  //create and style input
  const rawValue = cell.getValue()
  const opts = {zone: new (window as any).luxon.IANAZone('UTC')}
  let cellValue: any
  if (rawValue === 'NaN' || rawValue === null)
    cellValue = null
  else
    cellValue = (window as any).luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd'T'T")
  const input = document.createElement("input")

  input.setAttribute("type", "datetime-local");

  input.style.padding = "4px";
  input.style.width = "100%";
  input.style.boxSizing = "border-box";

  input.value = cellValue;

  onRendered(() => {
    input.focus();
    input.style.height = "100%";
  });

  function onChange() {
    const new_val = (window as any).luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd'T'T", opts).toMillis()
    if (new_val != cellValue)
      success(new_val)
    else
      cancel()
  }

  //submit new value on blur or change
  input.addEventListener("blur", onChange);

  //submit new value on enter
  input.addEventListener("keydown", function(e){
    if(e.keyCode == 13)
      onChange()

    if(e.keyCode == 27)
      cancel()
  });

  return input;
};


export class DataTabulatorView extends HTMLBoxView {
  model: DataTabulator;
  tabulator: any;
  columns: Map<string, any> = new Map();
  _tabulator_cell_updating: boolean=false
  _updating_page: boolean = false
  _updating_sort: boolean = false
  _selection_updating: boolean = false
  _initializing: boolean
  _lastVerticalScrollbarTopPosition: number = 0;
  _applied_styles: boolean = false
  _building: boolean = false

  connect_signals(): void {
    super.connect_signals()

    const p = this.model.properties
    const {configuration, layout, columns, groupby} = p;
    this.on_change([configuration, layout, groupby], debounce(() => {
      this.invalidate_render()
    }, 20, false))

    this.connect(this.model.properties.visible.change, () => {
      if (this.model.visible)
	this.tabulator.element.style.visibility = 'visible';
    })
    this.on_change([columns], () => {
      this.tabulator.setColumns(this.getColumns())
      this.setHidden()
    })

    this.connect(p.download.change, () => {
      const ftype = this.model.filename.endsWith('.json') ? "json" : "csv"
      this.tabulator.download(ftype, this.model.filename)
    })

    this.connect(p.children.change, () => this.renderChildren())

    this.connect(p.expanded.change, () => {
      // The first cell is the cell of the frozen _index column.
      for (const row of this.tabulator.rowManager.getRows()) {
        if (row.cells.length > 0)
          row.cells[0].layoutElement()
      }
      // Make sure the expand icon is changed when expanded is
      // changed from Python.
      for (const row of this.tabulator.rowManager.getRows()) {
        if (row.cells.length > 0) {
          const index = row.data._index
          const icon = this.model.expanded.indexOf(index) < 0 ? "►" : "▼"
          row.cells[1].element.innerText = icon
        }
      }
    })

    this.connect(p.cell_styles.change, () => {
      if (this._applied_styles)
        this.tabulator.redraw(true)
      this.setStyles()
    })
    this.connect(p.hidden_columns.change, () => {
      this.setHidden()
      this.tabulator.redraw(true)
    })
    this.connect(p.page_size.change, () => this.setPageSize())
    this.connect(p.page.change, () => {
      if (!this._updating_page)
        this.setPage()
    })
    this.connect(p.visible.change, () => this.setVisibility())
    this.connect(p.max_page.change, () => this.setMaxPage())
    this.connect(p.frozen_rows.change, () => this.setFrozen())
    this.connect(p.sorters.change, () => this.setSorters())
    this.connect(p.theme_classes.change, () => this.setCSSClasses(this.tabulator.element))
    this.connect(this.model.source.properties.data.change, () => this.setData())
    this.connect(this.model.source.streaming, () => this.addData())
    this.connect(this.model.source.patching, () => {
      const inds = this.model.source.selected.indices
      this.updateOrAddData();
      this.tabulator.rowManager.element.scrollTop = this._lastVerticalScrollbarTopPosition;
      // Restore indices since updating data may have reset checkbox column
      this.model.source.selected.indices = inds;
    })
    this.connect(this.model.source.selected.change, () => this.setSelection())
    this.connect(this.model.source.selected.properties.indices.change, () => this.setSelection())
  }

  get groupBy(): boolean | ((data: any) => string) {
    const groupby = (data: any) => {
      const groups = []
      for (const g of this.model.groupby) {
        const group = g + ': ' + data[g]
        groups.push(group)
      }
      return groups.join(', ')
    }
    return this.model.groupby.length ? groupby : false
  }

  get sorters(): any[] {
    const sorters = []
    if (this.model.sorters.length)
      sorters.push({column: '_index', dir: 'asc'})
    for (const sort of this.model.sorters.reverse()) {
      if (sort.column === undefined)
        sort.column = sort.field
      sorters.push(sort)
    }
    return sorters
  }

  invalidate_render(): void {
    this.tabulator.destroy()
    this.tabulator = null
    this.render()
  }

  redraw(): void {
    if (this._building)
      return
    if (this.tabulator.columnManager.element != null) {
      this.tabulator.columnManager.redraw(true);
    }
    if (this.tabulator.rowManager.renderer != null) {
      this.tabulator.rowManager.redraw(true)
      this.renderChildren()
      this.setStyles()
    }
  }

  after_layout(): void {
    super.after_layout()
    if (this.tabulator != null && this._initializing)
      this.redraw()
    this._initializing = false
  }

  setCSSClasses(el: HTMLDivElement): void {
    el.className = "pnx-tabulator tabulator"
    for (const cls of this.model.theme_classes)
      el.classList.add(cls)
  }

  render(): void {
    if (this.tabulator != null)
      this.tabulator.destroy()
    super.render()
    this._initializing = true
    const container = div({style: "display: contents;"})
    const el = div({style: "width: 100%; height: 100%; visibility: hidden;"})
    this.setCSSClasses(el)
    container.appendChild(el)
    this.shadow_el.appendChild(container)

    let configuration = this.getConfiguration()
    this.tabulator = new Tabulator(el, configuration)
    this.watch_stylesheets()
    this.init_callbacks()
  }

  style_redraw(): void {
    if (this.model.visible)
      this.tabulator.element.style.visibility = 'visible';
    if (!this._initializing && !this._building)
      this.redraw()
  }

  tableInit(): void {
    this._building = true
    // Patch the ajax request and page data parsing methods
    const ajax = this.tabulator.modules.ajax
    ajax.sendRequest = (_url: any, params: any, _config: any) => {
      return this.requestPage(params.page, params.sort)
    }
    this.tabulator.modules.page._parseRemoteData = (): boolean => {
      return false
    }
  }

  init_callbacks(): void {
    // Initialization
    this.tabulator.on("tableBuilding", () => this.tableInit())
    this.tabulator.on("tableBuilt", () => this.tableBuilt())

    // Rendering callbacks
    this.tabulator.on("selectableCheck", (row: any) => {
      const selectable = this.model.selectable_rows
      return (selectable == null) || selectable.includes(row._row.data._index)
    })
    this.tabulator.on("tooltips", (cell: any) => {
      return cell.getColumn().getField() + ": " + cell.getValue();
    })
    this.tabulator.on("scrollVertical", debounce(() => {
      this.setStyles()
    }, 50, false))

    // Sync state with model
    this.tabulator.on("rowSelectionChanged", (data: any, rows: any) => this.rowSelectionChanged(data, rows))
    this.tabulator.on("rowClick", (e: any, row: any) => this.rowClicked(e, row))
    this.tabulator.on("cellEdited", (cell: any) => this.cellEdited(cell))
    this.tabulator.on("dataFiltering", (filters: any) => {
      this.model.filters = filters
    })
    this.tabulator.on("dataFiltered", (_: any, rows: any[]) => {
      if (this._building)
	return
      // Ensure that after filtering empty scroll renders
      if (rows.length === 0)
	this.tabulator.rowManager.renderEmptyScroll()
      // Ensure that after filtering the page is updated
      this.updatePage(this.tabulator.getPage())
    })
    this.tabulator.on("pageLoaded", (pageno: number) => {
      this.updatePage(pageno)
    })
    this.tabulator.on("renderComplete", () => {
      if (this._building)
	return
      this.postUpdate()
    });
    this.tabulator.on("dataSorting", (sorters: any[]) => {
      const sorts = []
      for (const s of sorters) {
        if (s.field !== '_index')
          sorts.push({field: s.field, dir: s.dir})
      }
      if (this.model.pagination !== 'remote') {
        this._updating_sort = true
        this.model.sorters = sorts
        this._updating_sort = false
      }
    })
  }

  tableBuilt(): void {
    this._building = false
    this.setSelection()
    this.renderChildren()
    this.setStyles()

    if (this.model.pagination) {
      this.setMaxPage()
      this.tabulator.setPage(this.model.page)
    }
  }

  requestPage(page: number, sorters: any[]): Promise<void> {
    return new Promise((resolve: any, reject: any) => {
      try {
        if (page != null && sorters != null) {
          this._updating_sort = true
          const sorts = []
          for (const s of sorters) {
            if (s.field !== '_index')
              sorts.push({field: s.field, dir: s.dir})
          }
          this.model.sorters = sorts
          this._updating_sort = false
          this._updating_page = true
          try {
            this.model.page = page || 1
          } finally {
            this._updating_page = false
          }
        }
        resolve([])
      } catch(err) {
        reject(err)
      }
    })
  }

  getLayout(): string {
    let layout = this.model.layout
    switch (layout) {
      case "fit_data":
        return "fitData"
      case "fit_data_fill":
        return "fitDataFill"
      case "fit_data_stretch":
        return "fitDataStretch"
      case "fit_data_table":
        return "fitDataTable"
      case "fit_columns":
        return "fitColumns"
    }
  }

  getConfiguration(): any {
    // Only use selectable mode if explicitly requested otherwise manually handle selections
    let selectable = this.model.select_mode === 'toggle' ? true : NaN
    let configuration = {
      ...this.model.configuration,
      index: "_index",
      nestedFieldSeparator: false,
      movableColumns: false,
      selectable: selectable,
      columns: this.getColumns(),
      initialSort: this.sorters,
      layout: this.getLayout(),
      pagination: this.model.pagination != null,
      paginationMode: this.model.pagination,
      paginationSize: this.model.page_size,
      paginationInitialPage: 1,
      groupBy: this.groupBy,
      rowFormatter: (row: any) => this._render_row(row),
      frozenRows: (row: any) => {
	return this.model.frozen_rows.length ? this.model.frozen_rows.includes(row._row.data._index) : false
      }
    }
    if (this.model.pagination === "remote") {
      configuration['ajaxURL'] = "http://panel.pyviz.org"
      configuration['sortMode'] = "remote"
    }
    const cds: any = this.model.source;
    let data: any[]
    if (cds === null || (cds.columns().length === 0))
      data = []
    else
      data = transform_cds_to_records(cds, true)
    if (configuration.dataTree)
      data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators)
    return {
      ...configuration,
      "data": data,
    }
  }

  get child_models(): LayoutDOM[] {
    const children: LayoutDOM[] = []
    for (const idx of this.model.expanded) {
      const child = this.model.children.get?.(idx)
      if (child != null)
	children.push(child)
    }
    return children
  }

  renderChildren(): void {
    new Promise(async (resolve: any) => {
      await this.build_child_views()
      resolve(null)
    }).then(() => {
      for (const r of this.model.expanded) {
        const row = this.tabulator.getRow(r)
        this._render_row(row, false)
      }
      this._update_children()
      if (this.tabulator.rowManager.renderer != null)
	this.tabulator.rowManager.adjustTableSize()
      this.invalidate_layout()
    })
  }

  _render_row(row: any, resize: boolean = true): void {
    const index = row._row?.data._index
    if (!this.model.expanded.includes(index) || this.model.children.get(index) == null)
      return
    const model = this.model.children.get(index)
    const view = model == null ? null : this._child_views.get(model)
    if (view == null)
      return
    const rowEl = row.getElement()
    const style = getComputedStyle(this.tabulator.element.children[1].children[0])
    const bg = style.backgroundColor
    const neg_margin = rowEl.style.paddingLeft ? "-" + rowEl.style.paddingLeft : '0';
    const viewEl = div({style: "background-color: " + bg +"; margin-left:" + neg_margin + "; max-width: 100%; overflow-x: hidden;"})
    viewEl.appendChild(view.el)
    rowEl.appendChild(viewEl)
    if (!view.has_finished()) {
      view.render()
      view.after_render()
    }
    if (resize) {
      this._update_children()
      this.tabulator.rowManager.adjustTableSize()
      this.invalidate_layout()
    }
  }

  _expand_render(cell: any): string {
    const index = cell._cell.row.data._index
    const icon = this.model.expanded.indexOf(index) < 0 ? "►" : "▼"
    return "<i>" + icon + "</i>"
  }

  _update_expand(cell: any): void {
    const index = cell._cell.row.data._index
    const expanded = [...this.model.expanded]
    const exp_index = expanded.indexOf(index)
    if (exp_index < 0)
      expanded.push(index)
    else {
      const removed = expanded.splice(exp_index, 1)[0]
      const model = this.model.children.get?.(removed)
      if (model != null) {
        const view = this._child_views.get(model)
        if (view !== undefined && view.el != null)
          undisplay(view.el)
      }
    }
    this.model.expanded = expanded
    if (expanded.indexOf(index) < 0)
      return
    let ready = true
    for (const idx of this.model.expanded) {
      if (this.model.children.get?.(idx) == null) {
        ready = false
        break
      }
    }
    if (ready)
      this.renderChildren()
  }

  getData(): any[] {
    let data = transform_cds_to_records(this.model.source, true)
    if (this.model.configuration.dataTree)
      data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators)
    return data
  }

  getColumns(): any {
    this.columns = new Map()
    const config_columns: (any[] | undefined) = this.model.configuration?.columns;
    let columns = []
    columns.push({field: '_index', frozen: true, visible: false})
    if (config_columns != null) {
      for (const column of config_columns)
        if (column.columns != null) {
          const group_columns = []
          for (const col of column.columns)
            group_columns.push({...col})
          columns.push({...column, columns: group_columns})
        } else if (column.formatter === "expand") {
          const expand = {
            hozAlign: "center",
            cellClick: (_: any, cell: any) => { this._update_expand(cell) },
            formatter: (cell: any) => { return this._expand_render(cell) },
            width:40,
            frozen: true
          }
          columns.push(expand)
        } else {
          const new_column = {...column}
          if (new_column.formatter === "rowSelection") {
            new_column.cellClick = (_: any, cell: any) => {
              cell.getRow().toggleSelect();
            }
          }
          columns.push(new_column)
        }
    }
    for (const column of this.model.columns) {
      let tab_column: any = null
      if (config_columns != null) {
        for (const col of columns) {
          if (col.columns != null) {
            for (const c of col.columns) {
              if (column.field === c.field) {
                tab_column = c
                break
              }
            }
            if (tab_column != null)
              break
          } else if (column.field === col.field) {
            tab_column = col
            break
          }
        }
      }
      if (tab_column == null)
        tab_column = {field: column.field}
      this.columns.set(column.field, tab_column)
      if (tab_column.title == null)
        tab_column.title = column.title
      if (tab_column.width == null && column.width != null && column.width != 0)
        tab_column.width = column.width
      if (tab_column.formatter == null && column.formatter != null) {
        const formatter: any = column.formatter
        const ftype = formatter.type
        if (ftype === "BooleanFormatter")
          tab_column.formatter = "tickCross"
        else {
          tab_column.formatter = (cell: any) => {
            const formatted = column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, null)
            if (column.formatter.type === 'HTMLTemplateFormatter')
              return formatted
            const node = div()
            node.innerHTML = formatted
            const child = node.children[0]
            if (child.innerHTML === "function(){return c.convert(arguments)}") // If the formatter fails
              return ''
            return child
          }
        }
      }
      if (tab_column.sorter == 'timestamp') {
        tab_column.sorter = timestampSorter
      }
      if (tab_column.sorter === undefined) {
        tab_column.sorter = "string"
      }
      const editor: any = column.editor
      const ctype = editor.type
      if (tab_column.editor != null) {
        if (tab_column.editor === 'date') {
          tab_column.editor = dateEditor
        } else if (tab_column.editor === 'datetime') {
          tab_column.editor = datetimeEditor
        }
      } else if (ctype === "StringEditor") {
        if (editor.completions.length > 0) {
          tab_column.editor = "list"
          tab_column.editorParams = {values: editor.completions, autocomplete:true, listOnEmpty:true}
      } else
          tab_column.editor = "input"
      } else if (ctype === "TextEditor")
        tab_column.editor = "textarea"
      else if (ctype === "IntEditor" || ctype === "NumberEditor") {
        tab_column.editor = "number"
        tab_column.editorParams = {step: editor.step}
	if (ctype === "IntEditor")
	  tab_column.validator = "integer"
	else
	  tab_column.validator = "numeric"
      } else if (ctype === "CheckboxEditor") {
        tab_column.editor = "tickCross"
      } else if (ctype === "DateEditor") {
        tab_column.editor = dateEditor
      } else if (ctype === "SelectEditor") {
        tab_column.editor = "list"
        tab_column.editorParams = {values: editor.options}
      } else if (editor != null && editor.default_view != null) {
        tab_column.editor = (cell: any, onRendered: any, success: any, cancel: any) => {
          this.renderEditor(column, cell, onRendered, success, cancel)
        }
      }
      tab_column.visible = (tab_column.visible != false && !this.model.hidden_columns.includes(column.field))
      tab_column.editable = () => (this.model.editable && (editor.default_view != null))
      if (tab_column.headerFilter) {
        if ((typeof tab_column.headerFilter) === 'boolean' &&
            (typeof tab_column.editor) === 'string') {
          tab_column.headerFilter = tab_column.editor
          tab_column.headerFilterParams = tab_column.editorParams
        }
      }
      for (const sort of this.model.sorters) {
        if (tab_column.field === sort.field)
          tab_column.headerSortStartingDir = sort.dir
      }
      tab_column.cellClick = (_: any, cell: any) => {
        const index = cell.getData()._index
	const event = new CellClickEvent(column.field, index)
	this.model.trigger_event(event)
      }
      if (config_columns == null)
        columns.push(tab_column)
    }
    for (const col in this.model.buttons) {
      const button_formatter = () => {
        return this.model.buttons[col];
      };
      const button_column = {
        formatter: button_formatter,
        hozAlign: "center",
        cellClick: (_: any, cell: any) => {
          const index = cell.getData()._index
	  const event = new CellClickEvent(col, index)
          this.model.trigger_event(event)
        }
      }
      columns.push(button_column)
    }
    return columns
  }

  renderEditor(column: any, cell: any, onRendered: any, success: any, cancel: any): any {
    const editor = column.editor
    const view = new editor.default_view({column: column, model: editor, parent: this, container: cell._cell.element})
    view.initialize()
    view.connect_signals()
    onRendered(() => {
      view.setValue(cell.getValue())
    })

    view.inputEl.addEventListener('input', () => {
      const value = view.serializeValue()
      const old_value = cell.getValue()
      const validation = view.validate()
      if (!validation.valid)
        cancel(validation.msg)
      if (old_value != null && typeof value != typeof old_value)
        cancel("Mismatching type")
      else
        success(view.serializeValue())
    });

    return view.inputEl
  }

  // Update table

  setData(): void {
    if (this._initializing || this._building || !this.tabulator.initialized)
      return
    const data = this.getData()
    if (this.model.pagination != null)
      this.tabulator.rowManager.setData(data, true, false)
    else
      this.tabulator.setData(data)
  }

  addData(): void {
    const rows = this.tabulator.rowManager.getRows()
    const last_row = rows[rows.length-1]
    const start = ((last_row?.data._index) || 0)
    this.setData()
    if (this.model.follow && last_row)
      this.tabulator.scrollToRow(start, "top", false)
  }

  postUpdate(): void {
    this.setSelection()
    this.setStyles()
  }

  updateOrAddData(): void {
    // To avoid double updating the tabulator data
    if (this._tabulator_cell_updating)
      return

    let data = transform_cds_to_records(this.model.source, true)
    this.tabulator.setData(data)
  }

  setFrozen(): void {
    for (const row of this.model.frozen_rows) {
      this.tabulator.getRow(row).freeze()
    }
  }

  setVisibility(): void {
    if (this.tabulator == null)
      return
    this.tabulator.element.style.visibility = this.model.visible ? 'visible' : 'hidden';
  }

  updatePage(pageno: number): void {
    if (this.model.pagination === 'local' && this.model.page !== pageno) {
      this._updating_page = true
      this.model.page = pageno
      this._updating_page = false
      this.setStyles()
    }
  }

  setGroupBy(): void {
    this.tabulator.setGroupBy(this.groupBy)
  }

  setSorters(): void {
    if (this._updating_sort)
      return
    this.tabulator.setSort(this.sorters)
  }

  setStyles(): void {
    const style_data = this.model.cell_styles.data
    if (this.tabulator == null || this.tabulator.getDataCount() == 0 || style_data == null || !style_data.size)
      return
    this._applied_styles = false
    for (const r of style_data.keys()) {
      const row_style = style_data.get(r)
      const row = this.tabulator.getRow(r)
      if (!row)
        continue
      const cells = row._row.cells
      for (const c of row_style.keys()) {
        const style = row_style.get(c)
        const cell = cells[c]
        if (cell == null || !style.length)
          continue
        const element = cell.element
        for (const s of style) {
          let prop, value
          if (isArray(s))
            [prop, value] = s
          else if (!s.includes(':'))
            continue
          else
            [prop, value] = s.split(':')
          element.style.setProperty(prop, value.trimLeft())
          this._applied_styles = true
        }
      }
    }
  }

  setHidden(): void {
    for (const column of this.tabulator.getColumns()) {
      const col = column._column
      if ((col.field == '_index') || this.model.hidden_columns.includes(col.field))
        column.hide()
      else
        column.show()
    }
  }

  setMaxPage(): void {
    this.tabulator.setMaxPage(this.model.max_page)
    if (this.tabulator.modules.page.pagesElement)
      this.tabulator.modules.page._setPageButtons()
  }

  setPage(): void {
    this.tabulator.setPage(Math.min(this.model.max_page, this.model.page))
    if (this.model.pagination === "local") {
      this.renderChildren()
      this.setStyles()
    }
  }

  setPageSize(): void {
    this.tabulator.setPageSize(this.model.page_size)
    if (this.model.pagination === "local") {
      this.renderChildren()
      this.setStyles()
    }
  }

  setSelection(): void {
    if (this.tabulator == null || this._initializing || this._selection_updating || !this.tabulator.initialized)
      return

    const indices = this.model.source.selected.indices;
    const current_indices: any = this.tabulator.getSelectedData().map((row: any) => row._index)
    if (JSON.stringify(indices) == JSON.stringify(current_indices))
      return
    this._selection_updating = true
    this.tabulator.deselectRow()
    this.tabulator.selectRow(indices)
    for (const index of indices) {
      const row = this.tabulator.rowManager.findRow(index)
      if (row)
        this.tabulator.scrollToRow(index, "center", false).catch(() => {})
    }
    this._selection_updating = false
  }

  // Update model
  rowClicked(e: any, row: any) {
    if (
        this._selection_updating ||
        this._initializing ||
        (typeof this.model.select_mode) === 'string' ||
        this.model.select_mode === false ||  // selection disabled
        this.model.configuration.dataTree || // dataTree does not support selection
        e.srcElement?.innerText === "►"      // expand button
    )
      return
    let indices: number[] = []
    const selected = this.model.source.selected
    const index: number = row._row.data._index
    if (e.ctrlKey || e.metaKey) {
      indices = [...this.model.source.selected.indices]
    } else if (e.shiftKey && selected.indices.length) {
      const start = selected.indices[selected.indices.length-1]
      if (index>start) {
        for (let i = start; i<index; i++)
          indices.push(i)
      } else {
        for (let i = start; i>index; i--)
          indices.push(i)
      }
    }
    if (indices.indexOf(index) < 0)
      indices.push(index)
    else
      indices.splice(indices.indexOf(index), 1)
    // Remove the first selected indices when selectable is an int.
    if (typeof this.model.select_mode === 'number') {
      while (indices.length > this.model.select_mode) {
        indices.shift()
      }
    }
    const filtered = this._filter_selected(indices)
    this.tabulator.deselectRow()
    this.tabulator.selectRow(filtered)
    this._selection_updating = true
    selected.indices = filtered
    this._selection_updating = false
  }

  _filter_selected(indices: number[]): number[] {
    const filtered = []
    for (const ind of indices) {
      if (this.model.selectable_rows == null ||
          this.model.selectable_rows.indexOf(ind) >= 0)
        filtered.push(ind)
    }
    return filtered
  }

  rowSelectionChanged(data: any, _: any): void {
    if (
        this._selection_updating ||
        this._initializing ||
        (typeof this.model.select_mode) === 'boolean' ||
        (typeof this.model.select_mode) === 'number' ||
        this.model.configuration.dataTree
    )
      return
    const indices: number[] = data.map((row: any) => row._index)
    const filtered = this._filter_selected(indices)
    this._selection_updating = indices.length === filtered.length
    this.model.source.selected.indices = filtered
    this._selection_updating = false
  }

  cellEdited(cell: any): void {
    const field = cell._cell.column.field;
    const column_def = this.columns.get(field)
    const index = cell.getData()._index
    const value = cell._cell.value
    if (column_def.validator === 'numeric' && value === '') {
      cell.setValue(NaN, true)
      return
    }
    this._tabulator_cell_updating = true
    comm_settings.debounce = false
    this.model.trigger_event(new TableEditEvent(field, index, true))
    try {
      this.model.source.patch({[field]: [[index, value]]})
    } finally {
      comm_settings.debounce = true
      this._tabulator_cell_updating = false
    }
    this.model.trigger_event(new TableEditEvent(field, index, false))
    this.tabulator.scrollToRow(index, "top", false)
  }
}

export const TableLayout = Enum("fit_data", "fit_data_fill", "fit_data_stretch", "fit_data_table", "fit_columns")

export namespace DataTabulator {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    aggregators: p.Property<any>
    buttons: p.Property<any>
    children: p.Property<Map<number, LayoutDOM>>
    columns: p.Property<TableColumn[]>
    configuration: p.Property<any>
    download: p.Property<boolean>
    editable: p.Property<boolean>
    expanded: p.Property<number[]>
    filename: p.Property<string>
    filters: p.Property<any[]>
    follow: p.Property<boolean>
    frozen_rows: p.Property<number[]>
    groupby: p.Property<string[]>
    hidden_columns: p.Property<string[]>
    indexes: p.Property<string[]>
    layout: p.Property<typeof TableLayout["__type__"]>
    max_page: p.Property<number>
    page: p.Property<number>
    page_size: p.Property<number>
    pagination: p.Property<string | null>
    select_mode: p.Property<any>
    selectable_rows: p.Property<number[] | null>
    source: p.Property<ColumnDataSource>
    sorters: p.Property<any[]>
    cell_styles: p.Property<any>
    theme_classes: p.Property<string[]>
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

  static {
    this.prototype.default_view = DataTabulatorView;

    this.define<DataTabulator.Props>(({Any, Array, Boolean, Nullable, Number, Ref, String}) => ({
      aggregators:    [ Any,                     {} ],
      buttons:        [ Any,                     {} ],
      children:       [ Any,              new Map() ],
      configuration:  [ Any,                     {} ],
      columns:        [ Array(Ref(TableColumn)), [] ],
      download:       [ Boolean,              false ],
      editable:       [ Boolean,               true ],
      expanded:       [ Array(Number),           [] ],
      filename:       [ String,         "table.csv" ],
      filters:        [ Array(Any),              [] ],
      follow:         [ Boolean,               true ],
      frozen_rows:    [ Array(Number),           [] ],
      groupby:        [ Array(String),           [] ],
      hidden_columns: [ Array(String),           [] ],
      indexes:        [ Array(String),           [] ],
      layout:         [ TableLayout,     "fit_data" ],
      max_page:       [ Number,                   0 ],
      pagination:     [ Nullable(String),      null ],
      page:           [ Number,                   0 ],
      page_size:      [ Number,                   0 ],
      select_mode:    [ Any,                   true ],
      selectable_rows: [ Nullable(Array(Number)), null ],
      source:         [ Ref(ColumnDataSource)       ],
      sorters:        [ Array(Any),              [] ],
      cell_styles:    [ Any,                     {} ],
      theme_classes:  [ Array(String),           [] ],
    }))
  }
}
