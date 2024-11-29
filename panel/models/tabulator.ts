import {display, undisplay} from "@bokehjs/core/dom"
import {sum} from "@bokehjs/core/util/arrayable"
import {isArray, isBoolean, isString, isNumber} from "@bokehjs/core/util/types"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div} from "@bokehjs/core/dom"
import {Enum} from "@bokehjs/core/kinds"
import type * as p from "@bokehjs/core/properties"
import type {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {TableColumn} from "@bokehjs/models/widgets/tables"
import type {Attrs} from "@bokehjs/core/types"

import {debounce} from "debounce"

import {comm_settings} from "./comm_manager"
import {transform_cds_to_records} from "./data"
import {HTMLBox, HTMLBoxView} from "./layout"
import {schedule_when} from "./util"

import tabulator_css from "styles/models/tabulator.css"

export class TableEditEvent extends ModelEvent {
  constructor(readonly column: string, readonly row: number, readonly pre: boolean) {
    super()
  }

  protected override get event_values(): Attrs {
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

  protected override get event_values(): Attrs {
    return {model: this.origin, column: this.column, row: this.row}
  }

  static {
    this.prototype.event_name = "cell-click"
  }
}

export class SelectionEvent extends ModelEvent {
  constructor(readonly indices: number[], readonly selected: boolean, readonly flush: boolean = false) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, indices: this.indices, selected: this.selected, flush: this.flush}
  }

  static {
    this.prototype.event_name = "selection-change"
  }
}

declare const Tabulator: any

function find_group(key: any, value: string, records: any[]): any {
  for (const record of records) {
    if (record[key] == value) {
      return record
    }
  }
  return null
}

function summarize(grouped: any[], columns: any[], aggregators: any[], depth: number = 0): any {
  const summary: any = {}
  if (grouped.length == 0) {
    return summary
  }
  // depth level 0 is the root, finish here
  let aggs = ""
  if (depth > 0) {
    aggs = aggregators[depth-1]
  }

  for (const group of grouped) {
    const subsummary = summarize(group._children, columns, aggregators, depth+1)
    for (const col in subsummary) {
      if (isArray(subsummary[col])) {
        group[col] = sum(subsummary[col] as number[]) / subsummary[col].length
      } else {
        group[col] = subsummary[col]
      }
    }

    for (const column of columns.slice(1)) {
      // if no aggregation method provided for an index level,
      // or a specific column of an index level, do not aggregate data
      let agg: string = ""
      if (typeof aggs === "string") {
        agg = aggs
      } else if (column.field in aggs) {
        agg = aggs[column.field]
      }
      const val = group[column.field]
      if (column.field in summary) {
        const old_val = summary[column.field]
        if (agg === "min") {
          summary[column.field] = (val < old_val) ? val : old_val
        } else if (agg === "max") {
          summary[column.field] = (val > old_val) ? val : old_val
        } else if (agg === "sum") {
          summary[column.field] = val + old_val
        } else if (agg === "mean") {
          if (isArray(summary[column.field])) {
            summary[column.field].push(val)
          } else {
            summary[column.field] = [old_val, val]
          }
        }
      } else {
        summary[column.field] = val
      }
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
    for (const index of indexes.slice(1)) {
      subgroup = find_group(index_field, record[index], subgroup._children)
      if (subgroup == null) {
        subgroup = {_children: []}
        subgroup[index_field] = record[index]
        group._children.push(subgroup)
      }
      for (const column of columns.slice(1)) {
        subgroup[column.field] = record[column]
      }
      group = subgroup
    }
    for (const column of columns.slice(1)) {
      subgroup[column.field] = record[column.field]
    }
  }
  const aggs = []
  for (const index of indexes) {
    if (index in aggregators) {
      if (aggregators[index] instanceof Map) {
        // when some column names are numeric, need to convert that from a Map to an Object
        aggs.push(Object.fromEntries(aggregators[index]))
      } else {
        aggs.push(aggregators[index])
      }
    } else {
      aggs.push("sum")
    }
  }
  summarize(grouped, columns, aggs)
  return grouped
}

const timestampSorter = function(a: any, b: any, _aRow: any, _bRow: any, _column: any, _dir: any, _params: any) {
  // Bokeh/Panel serializes datetime objects as UNIX timestamps (in milliseconds).

  //a, b - the two values being compared
  //aRow, bRow - the row components for the values being compared (useful if you need to access additional fields in the row data for the sort)
  //column - the column component for the column being sorted
  //dir - the direction of the sort ("asc" or "desc")
  //sorterParams - sorterParams object from column definition array

  // Added an _ in front of some parameters as they're unused and the Typescript compiler was complaining about it.

  // const alignEmptyValues = params.alignEmptyValues
  let emptyAlign: any
  emptyAlign = 0

  const opts = {zone: new (window as any).luxon.IANAZone("UTC")}

  if (Number.isNaN(a)) {
    a = (window as any).luxon.DateTime.fromISO("invalid")
  } else {
    a = (window as any).luxon.DateTime.fromMillis(a, opts)
  }
  if (Number.isNaN(b)) {
    b = (window as any).luxon.DateTime.fromISO("invalid")
  } else {
    b = (window as any).luxon.DateTime.fromMillis(b, opts)
  }

  if (!a.isValid) {
    emptyAlign = !b.isValid ? 0 : -1
  } else if (!b.isValid) {
    emptyAlign =  1
  } else {
    //compare valid values
    return a - b
  }

  // Invalid (e.g. NaN) always at the bottom
  emptyAlign *= -1

  return emptyAlign
}

const dateEditor = function(cell: any, onRendered: any, success: any, cancel: any) {
  //cell - the cell component for the editable cell
  //onRendered - function to call when the editor has been rendered
  //success - function to call to pass the successfully updated value to Tabulator
  //cancel - function to call to abort the edit and return to a normal cell

  //create and style input
  const rawValue = cell.getValue()
  const opts = {zone: new (window as any).luxon.IANAZone("UTC")}
  let cellValue: any
  if (rawValue === "NaN" || rawValue === null) {
    cellValue = null
  } else {
    cellValue = (window as any).luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd")
  }
  const input = document.createElement("input")

  input.setAttribute("type", "date")

  input.style.padding = "4px"
  input.style.width = "100%"
  input.style.boxSizing = "border-box"

  input.value = cellValue

  onRendered(() => {
    input.focus()
    input.style.height = "100%"
  })

  function onChange() {
    const new_val = (window as any).luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd", opts).toMillis()
    if (new_val != cellValue) {
      success(new_val)
    } else {
      cancel()
    }
  }

  //submit new value on blur or change
  input.addEventListener("blur", onChange)

  //submit new value on enter
  input.addEventListener("keydown", (e) => {
    if (e.key == "Enter") {
      setTimeout(onChange, 100)
    }

    if (e.key == "Escape") {
      setTimeout(cancel, 100)
    }
  })

  return input
}

const datetimeEditor = function(cell: any, onRendered: any, success: any, cancel: any) {
  //cell - the cell component for the editable cell
  //onRendered - function to call when the editor has been rendered
  //success - function to call to pass the successfully updated value to Tabulator
  //cancel - function to call to abort the edit and return to a normal cell

  //create and style input
  const rawValue = cell.getValue()
  const opts = {zone: new (window as any).luxon.IANAZone("UTC")}
  let cellValue: any
  if (rawValue === "NaN" || rawValue === null) {
    cellValue = null
  } else {
    cellValue = (window as any).luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd'T'T")
  }
  const input = document.createElement("input")

  input.setAttribute("type", "datetime-local")

  input.style.padding = "4px"
  input.style.width = "100%"
  input.style.boxSizing = "border-box"

  input.value = cellValue

  onRendered(() => {
    input.focus()
    input.style.height = "100%"
  })

  function onChange() {
    const new_val = (window as any).luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd'T'T", opts).toMillis()
    if (new_val != cellValue) {
      success(new_val)
    } else {
      cancel()
    }
  }

  //submit new value on blur or change
  input.addEventListener("blur", onChange)

  //submit new value on enter
  input.addEventListener("keydown", (e) => {
    if (e.key == "Enter") {
      setTimeout(onChange, 100)
    }

    if (e.key == "Escape") {
      setTimeout(cancel, 100)
    }
  })

  return input
}

const nestedEditor = function(cell: any, editorParams: any) {
  //cell - the cell component for the editable cell

  const row = cell.getRow().getData()
  let values = editorParams.options
  for (const i of editorParams.lookup_order) {
    values = row[i] in values ? values[row[i]] : []
    if (Array.isArray(values)) {
      break
    }
  }
  return values ? values : []
}

function find_column(group: any, field: string): any {
  if (group.columns != null) {
    for (const col of group.columns) {
      const found = find_column(col, field)
      if (found) {
        return found
      }
    }
  } else {
    return group.field === field ? group : null
  }
}

function clone_column(group: any): any {
  if (group.columns == null) {
    return {...group}
  }
  const group_columns = []
  for (const col of group.columns) {
    group_columns.push(clone_column(col))
  }
  return {...group, columns: group_columns}
}

export class DataTabulatorView extends HTMLBoxView {
  declare model: DataTabulator

  tabulator: any
  columns: Map<string, any> = new Map()
  container: HTMLDivElement | null = null
  _tabulator_cell_updating: boolean=false
  _updating_page: boolean = false
  _updating_expanded: boolean = false
  _updating_sort: boolean = false
  _selection_updating: boolean = false
  _last_selected_row: any = null
  _initializing: boolean
  _lastVerticalScrollbarTopPosition: number = 0
  _lastHorizontalScrollbarLeftPosition: number = 0
  _applied_styles: boolean = false
  _building: boolean = false
  _redrawing: boolean = false
  _debounced_redraw: any = null
  _restore_scroll: boolean | "horizontal" | "vertical" = false
  _updating_scroll: boolean = false
  _is_scrolling: boolean = false

  override connect_signals(): void {
    super.connect_signals()

    this._debounced_redraw = debounce(() => this._resize_redraw(), 20, false)
    const {
      configuration, layout, columns, groupby, visible, download,
      children, expanded, cell_styles, hidden_columns, page_size,
      page, max_page, frozen_rows, sorters, theme_classes,
    } = this.model.properties

    this.on_change([configuration, layout, groupby], debounce(() => {
      this.invalidate_render()
    }, 20, false))

    this.on_change(visible, () => {
      if (this.model.visible) {
        this.tabulator.element.style.visibility = "visible"
      }
    })
    this.on_change(columns, () => {
      this.tabulator.setColumns(this.getColumns())
      this.setHidden()
    })

    this.on_change(download, () => {
      const ftype = this.model.filename.endsWith(".json") ? "json" : "csv"
      this.tabulator.download(ftype, this.model.filename)
    })

    this.on_change(children, () => this.renderChildren())

    this.on_change(expanded, () => {
      // The first cell is the cell of the frozen _index column.
      for (const row of this.tabulator.rowManager.getRows()) {
        if (row.cells.length > 0) {
          row.cells[0].layoutElement()
        }
      }
      // Make sure the expand icon is changed when expanded is
      // changed from Python.
      for (const row of this.tabulator.rowManager.getRows()) {
        if (row.cells.length > 0) {
          const index = row.data._index
          const icon = this.model.expanded.includes(index) ? "▼" : "►"
          row.cells[1].element.innerText = icon
        }
      }
      // If content is embedded, views may not have been
      // rendered so if expanded is updated server side
      // we have to trigger a render
      if (this.model.embed_content && !this._updating_expanded) {
        this.renderChildren()
      }
    })

    this.on_change(cell_styles, () => {
      if (this._applied_styles) {
        this.tabulator.redraw(true)
      }
      this.setStyles()
    })
    this.on_change(hidden_columns, () => {
      this.setHidden()
      this.tabulator.redraw(true)
    })
    this.on_change(page_size, () => this.setPageSize())
    this.on_change(page, () => {
      if (!this._updating_page) {
        this.setPage()
      }
    })
    this.on_change(visible, () => this.setVisibility())
    this.on_change(max_page, () => this.setMaxPage())
    this.on_change(frozen_rows, () => this.setFrozen())
    this.on_change(sorters, () => this.setSorters())
    this.on_change(theme_classes, () => this.setCSSClasses(this.tabulator.element))

    this.on_change(this.model.source.properties.data, () => {
      if (this.tabulator === undefined) {
        return
      }
      this._restore_scroll = "horizontal"
      this._selection_updating = true
      this._updating_scroll = true
      this.setData()
      this._updating_scroll = false
      this._selection_updating = false
      this.postUpdate()
    })
    this.connect(this.model.source.streaming, () => this.addData())
    this.connect(this.model.source.patching, () => {
      const inds = this.model.source.selected.indices
      this._updating_scroll = true
      this.updateOrAddData()
      this._updating_scroll = false
      // Restore indices since updating data may have reset checkbox column
      this.model.source.selected.indices = inds
      this.restore_scroll()
    })
    this.connect(this.model.source.selected.change, () => this.setSelection())
    this.connect(this.model.source.selected.properties.indices.change, () => this.setSelection())
  }

  get groupBy(): boolean | ((data: any) => string) {
    const groupby = (data: any) => {
      const groups = []
      for (const g of this.model.groupby) {
        const group = `${g}: ${data[g]}`
        groups.push(group)
      }
      return groups.join(", ")
    }
    return (this.model.groupby.length > 0) ? groupby : false
  }

  get sorters(): any[] {
    const sorters = []
    if (this.model.sorters.length > 0) {
      sorters.push({column: "_index", dir: "asc"})
    }
    for (const sort of this.model.sorters.reverse()) {
      if (sort.column === undefined) {
        sort.column = sort.field
      }
      sorters.push(sort)
    }
    return sorters
  }

  override invalidate_render(): void {
    this.tabulator.destroy()
    this.tabulator = null
    this.render()
  }

  redraw(columns: boolean = true, rows: boolean = true): void {
    if (this._building || this.tabulator == null || this._redrawing) {
      return
    }
    this._redrawing = true
    if (columns && (this.tabulator.columnManager.element != null)) {
      this.tabulator.columnManager.redraw(true)
    }
    if (rows && (this.tabulator.rowManager.renderer != null)) {
      this.tabulator.rowManager.redraw(true)
      this.setStyles()
    }
    this._redrawing = false
    this._restore_scroll = true
  }

  get is_drawing(): boolean {
    return this._building || this._redrawing || !this.root.has_finished()
  }

  override after_layout(): void {
    super.after_layout()
    if (this.tabulator != null && this._initializing && !this.is_drawing) {
      this._initializing = false
      this._resize_redraw()
    }
  }

  override after_resize(): void {
    super.after_resize()
    if (!this._is_scrolling && !this._initializing && !this.is_drawing) {
      this._debounced_redraw()
    }
  }

  _resize_redraw(): void {
    if (this._initializing || !this.container || this._building) {
      return
    }
    const width = this.container.clientWidth
    const height = this.container.clientHeight
    if (!width || !height) {
      return
    }
    this.redraw(true, true)
    this.restore_scroll()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), tabulator_css]
  }

  setCSSClasses(el: HTMLDivElement): void {
    el.className = "pnx-tabulator tabulator"
    for (const cls of this.model.theme_classes) {
      el.classList.add(cls)
    }
  }

  override render(): void {
    if (this.tabulator != null) {
      this.tabulator.destroy()
    }
    super.render()
    this._initializing = true
    this._building = true
    const container = div({style: {display: "contents"}})
    const el = div({style: {width: "100%", height: "100%", visibility: "hidden"}})
    this.container = el
    this.setCSSClasses(el)
    container.appendChild(el)
    this.shadow_el.appendChild(container)

    const configuration = this.getConfiguration()
    this.tabulator = new Tabulator(el, configuration)
    this.watch_stylesheets()
    this.init_callbacks()
  }

  override style_redraw(): void {
    if (this.model.visible) {
      this.tabulator.element.style.visibility = "visible"
    }
    if (!this._initializing && !this._building) {
      this.redraw()
    }
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
    this.tabulator.on("selectableRowsCheck", (row: any) => {
      const selectable = this.model.selectable_rows
      return (selectable == null) || selectable.includes(row._row.data._index)
    })
    this.tabulator.on("tooltips", (cell: any) => {
      return `${cell.getColumn().getField()}: ${cell.getValue()}`
    })
    this.tabulator.on("scrollVertical", debounce(() => {
      this.setStyles()
    }, 50, false))

    // Sync state with model
    this.tabulator.on("rowSelectionChanged", (data: any, rows: any, selected: any, deselected: any) => {
      this.rowSelectionChanged(data, rows, selected, deselected)
    })
    this.tabulator.on("rowClick", (e: any, row: any) => this.rowClicked(e, row))
    this.tabulator.on("cellEdited", (cell: any) => this.cellEdited(cell))
    this.tabulator.on("dataFiltering", (filters: any) => {
      this.record_scroll()
      this.model.filters = filters
    })
    this.tabulator.on("dataFiltered", (_: any, rows: any[]) => {
      if (this._building) {
        return
      }
      // Ensure that after filtering empty scroll renders
      if (rows.length === 0) {
        this.tabulator.rowManager.renderEmptyScroll()
      }
      if (this.model.pagination != null) {
        // Ensure that after filtering the page is updated
        this.updatePage(this.tabulator.getPage())
      }
    })
    this.tabulator.on("pageLoaded", (pageno: number) => {
      this.updatePage(pageno)
    })
    this.tabulator.on("renderComplete", () => {
      if (this._building) {
        return
      }
      this.postUpdate()
    })
    this.tabulator.on("dataSorting", (sorters: any[]) => {
      const sorts = []
      for (const s of sorters) {
        if (s.field !== "_index") {
          sorts.push({field: s.field, dir: s.dir})
        }
      }
      if (this.model.pagination !== "remote") {
        this._updating_sort = true
        this.model.sorters = sorts.reverse()
        this._updating_sort = false
      }
    })
  }

  tableBuilt(): void {
    this.setSelection()
    this.renderChildren()
    this.setStyles()

    // Track scrolling position and active scroll
    const holder = this.shadow_el.querySelector(".tabulator-tableholder")
    let scroll_timeout: ReturnType<typeof setTimeout> | undefined
    if (holder) {
      holder.addEventListener("scroll", () => {
        this.record_scroll()
        this._is_scrolling = true
        clearTimeout(scroll_timeout)
        scroll_timeout = setTimeout(() => {
          this._is_scrolling = false
        }, 200)
      })
    }

    if (this.model.pagination) {
      if (this.model.page_size == null) {
        const table = this.shadow_el.querySelector(".tabulator-table")
        if (table != null && holder != null) {
          const table_height = holder.clientHeight
          let height = 0
          let page_size = null
          const heights = []
          for (let i = 0; i<table.children.length; i++) {
            const row_height = table.children[i].clientHeight
            heights.push(row_height)
            height += row_height
            if (height > table_height) {
              page_size = i
              break
            }
          }
          if (height < table_height) {
            page_size = table.children.length
            const remaining = table_height - height
            page_size += Math.floor(remaining / Math.min(...heights))
          }
          this.model.page_size = Math.max(page_size || 1, 1)
        }
      }
      this.setMaxPage()
      this.tabulator.setPage(this.model.page)
    }
    this._building = false
    schedule_when(() => {
      const initializing = this._initializing
      this._initializing = false
      if (initializing) {
        this._resize_redraw()
      }
    }, () => this.root.has_finished())
  }

  requestPage(page: number, sorters: any[]): Promise<void> {
    return new Promise((resolve: any, reject: any) => {
      try {
        if (page != null && sorters != null) {
          this._updating_sort = true
          const sorts = []
          for (const s of sorters) {
            if (s.field !== "_index") {
              sorts.push({field: s.field, dir: s.dir})
            }
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
      } catch (err) {
        reject(err)
      }
    })
  }

  getLayout(): string {
    const layout = this.model.layout
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
    const selectableRows = this.model.select_mode === "toggle" ? true : NaN
    const configuration = {
      ...this.model.configuration,
      index: "_index",
      nestedFieldSeparator: false,
      movableColumns: false,
      selectableRows,
      columns: this.getColumns(),
      initialSort: this.sorters,
      layout: this.getLayout(),
      pagination: this.model.pagination != null,
      paginationMode: this.model.pagination,
      paginationSize: this.model.page_size || 20,
      paginationInitialPage: 1,
      groupBy: this.groupBy,
      frozenRows: (row: any) => {
        return (this.model.frozen_rows.length > 0) ? this.model.frozen_rows.includes(row._row.data._index) : false
      },
      rowFormatter: (row: any) => this._render_row(row, false),
    }
    if (this.model.max_height != null) {
      configuration.maxHeight = this.model.max_height
    }
    if (this.model.pagination === "remote") {
      configuration.ajaxURL = "http://panel.pyviz.org"
      configuration.sortMode = "remote"
    }
    const data = this.getData()
    return {
      ...configuration,
      data,
    }
  }

  get_child(idx: number): LayoutDOM | null {
    if (this.model.children instanceof Map) {
      return this.model.children.get(idx) || null
    }
    return null
  }

  override get child_models(): LayoutDOM[] {
    const children: LayoutDOM[] = []
    for (const idx of this.model.expanded) {
      const child = this.get_child(idx)
      if (child != null) {
        children.push(child)
      }
    }
    return children
  }

  get row_index(): Map<number, any> {
    const rows = this.tabulator.getRows()
    const lookup = new Map()
    for (const row of rows) {
      const index = row._row?.data._index
      if (index != null) {
        lookup.set(index, row)
      }
    }
    return lookup
  }

  renderChildren(): void {
    void new Promise(async () => {
      await this.build_child_views()
      const lookup = this.row_index
      const expanded = this.model.expanded
      for (const index of expanded) {
        const model = this.get_child(index)
        const row = lookup.get(index)
        const view = model == null ? null : this._child_views.get(model)
        if (view != null) {
          this._render_row(row, index === expanded[expanded.length-1])
        }
      }
    })
  }

  _render_row(row: any, resize: boolean = true): void {
    const index = row._row?.data._index
    if (!this.model.expanded.includes(index)) {
      return
    }
    const model = this.get_child(index)
    const view = model == null ? null : this._child_views.get(model)
    if (view == null) {
      return
    }
    schedule_when(() => {
      const rowEl = row.getElement()
      const style = getComputedStyle(this.tabulator.element.children[1].children[0])
      const bg = style.backgroundColor
      const neg_margin = rowEl.style.paddingLeft ? `-${rowEl.style.paddingLeft}` : "0"
      const prev_child = rowEl.children[rowEl.children.length-1]
      let viewEl
      if (prev_child != null && prev_child.className == "row-content") {
        viewEl = prev_child
        if (viewEl.children.length && viewEl.children[0] === view.el) {
          return
        }
      } else {
        viewEl = div({class: "row-content", style: {background_color: bg, margin_left: neg_margin, max_width: "100%", overflow_x: "hidden"}})
        rowEl.appendChild(viewEl)
      }
      display(view.el)
      viewEl.appendChild(view.el)
      if (view.shadow_el.children.length === 0) {
        view.render()
        view.after_render()
      }
      if (resize) {
        this._update_children()
        this.resize_table()
      }
    }, () => this.root.has_finished())
  }

  resize_table(): void {
    if (this.tabulator.rowManager.renderer != null) {
      try {
        this.tabulator.rowManager.adjustTableSize()
      } catch (e) {}
    }
    this.invalidate_layout()
  }

  _expand_render(cell: any): string {
    const index = cell._cell.row.data._index
    const icon = this.model.expanded.indexOf(index) < 0 ? "►" : "▼"
    return icon
  }

  _update_expand(cell: any): void {
    const index = cell._cell.row.data._index
    const expanded = [...this.model.expanded]
    if (!expanded.includes(index)) {
      expanded.push(index)
    } else {
      const exp_index = expanded.indexOf(index)
      const removed = expanded.splice(exp_index, 1)[0]
      const model = this.get_child(removed)
      if (model != null) {
        const view = this._child_views.get(model)
        if (view !== undefined && view.el != null) {
          undisplay(view.el)
        }
      }
    }
    this._updating_expanded = true
    this.model.expanded = expanded
    this._updating_expanded = false
    if (!expanded.includes(index)) {
      return
    }
    let ready = true
    for (const idx of this.model.expanded) {
      if (this.get_child(idx) == null) {
        ready = false
        break
      }
    }
    if (ready) {
      this.renderChildren()
    }
  }

  getData(): any[] {
    const cds = this.model.source
    let data: any[]
    if (cds === null || (cds.columns().length === 0)) {
      data = []
    } else {
      data = transform_cds_to_records(cds, true)
    }
    if (this.model.configuration.dataTree) {
      data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators)
    }
    return data
  }

  getColumns(): any {
    this.columns = new Map()
    const config_columns: (any[] | undefined) = this.model.configuration?.columns
    const columns = []
    columns.push({field: "_index", frozen: true, visible: false})
    if (config_columns != null) {
      for (const column of config_columns) {
        const new_column = clone_column(column)
        if (column.formatter === "expand") {
          const expand = {
            hozAlign: "center",
            cellClick: (_: any, cell: any) => {
              this._update_expand(cell)
            },
            formatter: (cell: any) => {
              return this._expand_render(cell)
            },
            width: 40,
            frozen: true,
          }
          columns.push(expand)
        } else {
          if (new_column.formatter === "rowSelection") {
            new_column.cellClick = (_: any, cell: any) => {
              cell.getRow().toggleSelect()
            }
          }
          columns.push(new_column)
        }
      }
    }
    for (const column of this.model.columns) {
      let tab_column: any = null
      if (config_columns != null) {
        for (const col of columns) {
          tab_column = find_column(col, column.field)
          if (tab_column != null) {
            break
          }
        }
      }
      if (tab_column == null) {
        tab_column = {field: column.field}
      }
      this.columns.set(column.field, tab_column)
      if (tab_column.title == null) {
        tab_column.title = column.title
      }
      if (tab_column.width == null && column.width != null && column.width != 0) {
        tab_column.width = column.width
      }
      if (tab_column.formatter == null && column.formatter != null) {
        const formatter: any = column.formatter
        const ftype = formatter.type
        if (ftype === "BooleanFormatter") {
          tab_column.formatter = "tickCross"
        } else {
          tab_column.formatter = (cell: any) => {
            const row = cell.getRow()
            const formatted = column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, row.getData())
            if (column.formatter.type === "HTMLTemplateFormatter") {
              return formatted
            }
            const node = div()
            node.innerHTML = formatted
            const child = node.children[0]
            if (child.innerHTML === "function(){return c.convert(arguments)}") { // If the formatter fails
              return ""
            }
            return child
          }
        }
      }
      if (tab_column.sorter == "timestamp") {
        tab_column.sorter = timestampSorter
      }
      if (tab_column.sorter === undefined) {
        tab_column.sorter = "string"
      }
      const editor: any = column.editor
      const ctype = editor.type
      if (tab_column.editor != null) {
        if (tab_column.editor === "date") {
          tab_column.editor = dateEditor
        } else if (tab_column.editor === "datetime") {
          tab_column.editor = datetimeEditor
        } else if (tab_column.editor === "nested") {
          tab_column.editorParams.valuesLookup = (cell: any) => {
            return nestedEditor(cell, tab_column.editorParams)
          }
          tab_column.editor = "list"
        }
      } else if (ctype === "StringEditor") {
        if (editor.completions.length > 0) {
          tab_column.editor = "list"
          tab_column.editorParams = {values: editor.completions, autocomplete: true, listOnEmpty: true}
        } else {
          tab_column.editor = "input"
        }
      } else if (ctype === "TextEditor") {
        tab_column.editor = "textarea"
      } else if (ctype === "IntEditor" || ctype === "NumberEditor") {
        tab_column.editor = "number"
        tab_column.editorParams = {step: editor.step}
        if (ctype === "IntEditor") {
          tab_column.validator = "integer"
        } else {
          tab_column.validator = "numeric"
        }
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
        if (isBoolean(tab_column.headerFilter) && isString(tab_column.editor)) {
          tab_column.headerFilter = tab_column.editor
          tab_column.headerFilterParams = tab_column.editorParams
        }
      }
      for (const sort of this.model.sorters) {
        if (tab_column.field === sort.field) {
          tab_column.headerSortStartingDir = sort.dir
        }
      }
      tab_column.cellClick = (_: any, cell: any) => {
        const index = cell.getData()._index
        const event = new CellClickEvent(column.field, index)
        this.model.trigger_event(event)
      }
      if (config_columns == null) {
        columns.push(tab_column)
      }
    }
    for (const col in this.model.buttons) {
      const button_formatter = () => {
        return this.model.buttons[col]
      }
      const button_column = {
        formatter: button_formatter,
        hozAlign: "center",
        cellClick: (_: any, cell: any) => {
          const index = cell.getData()._index
          const event = new CellClickEvent(col, index)
          this.model.trigger_event(event)
        },
      }
      columns.push(button_column)
    }
    return columns
  }

  renderEditor(column: any, cell: any, onRendered: any, success: any, cancel: any): any {
    const editor = column.editor
    const view = new editor.default_view({column, model: editor, parent: this, container: cell._cell.element})
    view.initialize()
    view.connect_signals()
    onRendered(() => {
      view.setValue(cell.getValue())
    })

    view.inputEl.addEventListener("input", () => {
      const value = view.serializeValue()
      const old_value = cell.getValue()
      const validation = view.validate()
      if (!validation.valid) {
        cancel(validation.msg)
      }
      if (old_value != null && typeof value != typeof old_value) {
        cancel("Mismatching type")
      } else {
        success(view.serializeValue())
      }
    })

    return view.inputEl
  }

  // Update table
  setData(): Promise<void> {
    if (this._initializing || this._building || !this.tabulator.initialized) {
      return Promise.resolve(undefined)
    }
    const data = this.getData()
    if (this.model.pagination != null) {
      return this.tabulator.rowManager.setData(data, true, false)
    } else {
      return this.tabulator.setData(data)
    }
  }

  addData(): void {
    const rows = this.tabulator.rowManager.getRows()
    const last_row = rows[rows.length-1]
    const start = ((last_row?.data._index) || 0)
    this._updating_page = true
    const promise = this.setData()
    if (this.model.follow) {
      promise.then(() => {
        if (this.model.pagination) {
          this.tabulator.setPage(Math.ceil(this.tabulator.rowManager.getDataCount() / (this.model.page_size || 20)))
        }
        if (last_row) {
          this.tabulator.scrollToRow(start, "top", false)
        }
        this._updating_page = false
      })
    } else {
      this._updating_page = true
    }
  }

  postUpdate(): void {
    this.setSelection()
    this.setStyles()
    if (this._restore_scroll) {
      const vertical = this._restore_scroll === "horizontal" ? false : true
      const horizontal = this._restore_scroll === "vertical" ? false : true
      this.restore_scroll(horizontal, vertical)
      this._restore_scroll = false
    }
  }

  updateOrAddData(): void {
    // To avoid double updating the tabulator data
    if (this._tabulator_cell_updating) {
      return
    }

    // Temporarily set minHeight to avoid "scroll-to-top" issues caused
    // by Tabulator JS entirely destroying the table when .setData is called.
    // Inspired by https://github.com/olifolkerd/tabulator/issues/4155
    const prev_minheight = this.tabulator.element.style.minHeight
    this.tabulator.element.style.minHeight = `${this.tabulator.element.offsetHeight}px`

    const data = transform_cds_to_records(this.model.source, true)
    this.tabulator.setData(data).then(() => {
      this.tabulator.element.style.minHeight = prev_minheight
    })
  }

  setFrozen(): void {
    for (const row of this.model.frozen_rows) {
      this.tabulator.getRow(row).freeze()
    }
  }

  setVisibility(): void {
    if (this.tabulator == null) {
      return
    }
    this.tabulator.element.style.visibility = this.model.visible ? "visible" : "hidden"
  }

  updatePage(pageno: number): void {
    if (this.model.pagination === "local" && this.model.page !== pageno && !this._updating_page) {
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
    if (this._updating_sort) {
      return
    }
    this.tabulator.setSort(this.sorters)
  }

  setStyles(): void {
    const style_data = this.model.cell_styles.data
    if (this.tabulator == null || this.tabulator.getDataCount() == 0 || style_data == null || !style_data.size) {
      return
    }
    this._applied_styles = false
    for (const r of style_data.keys()) {
      const row_style = style_data.get(r)
      const row = this.tabulator.getRow(r)
      if (!row) {
        continue
      }
      const cells = row._row.cells
      for (const c of row_style.keys()) {
        const style = row_style.get(c)
        const cell = cells[c]
        if (cell == null || !style.length) {
          continue
        }
        const element = cell.element
        for (const s of style) {
          let prop, value
          if (isArray(s)) {
            [prop, value] = s
          } else if (!s.includes(":")) {
            continue
          } else {
            [prop, value] = s.split(":")
          }
          element.style.setProperty(prop, value.trimLeft())
          this._applied_styles = true
        }
      }
    }
  }

  setHidden(): void {
    for (const column of this.tabulator.getColumns()) {
      const col = column._column
      if ((col.field == "_index") || this.model.hidden_columns.includes(col.field)) {
        column.hide()
      } else {
        column.show()
      }
    }
  }

  setMaxPage(): void {
    this.tabulator.setMaxPage(this.model.max_page)
    if (this.tabulator.modules.page.pagesElement) {
      this.tabulator.modules.page._setPageButtons()
    }
  }

  setPage(): void {
    this.tabulator.setPage(Math.min(this.model.max_page, this.model.page))
    if (this.model.pagination === "local") {
      this.setStyles()
    }
  }

  setPageSize(): void {
    this.tabulator.setPageSize(this.model.page_size)
    if (this.model.pagination === "local") {
      this.setStyles()
    }
  }

  setSelection(): void {
    if (this.tabulator == null || this._initializing || this._selection_updating || !this.tabulator.initialized) {
      return
    }

    const indices = this.model.source.selected.indices
    const current_indices: any = this.tabulator.getSelectedData().map((row: any) => row._index)
    if (JSON.stringify(indices) == JSON.stringify(current_indices)) {
      return
    }
    this._selection_updating = true
    this.tabulator.deselectRow()
    this.tabulator.selectRow(indices)
    for (const index of indices) {
      const row = this.tabulator.rowManager.findRow(index)
      if (row) {
        this.tabulator.scrollToRow(index, "center", false).catch(() => {})
      }
    }
    this._selection_updating = false
  }

  restore_scroll(horizontal: boolean=true, vertical: boolean=true): void {
    if (!(horizontal || vertical)) {
      return
    }
    const opts: ScrollToOptions = {behavior: "instant"}
    if (vertical) {
      opts.top = this._lastVerticalScrollbarTopPosition
    }
    if (horizontal) {
      opts.left = this._lastHorizontalScrollbarLeftPosition
    }
    setTimeout(() => {
      this._updating_scroll = true
      this.tabulator.rowManager.element.scrollTo(opts)
      this._updating_scroll = false
    }, 0)
  }

  // Update model

  record_scroll() {
    if (this._updating_scroll) {
      return
    }
    this._lastVerticalScrollbarTopPosition = this.tabulator.rowManager.element.scrollTop
    this._lastHorizontalScrollbarLeftPosition = this.tabulator.rowManager.element.scrollLeft
  }

  rowClicked(e: any, row: any) {
    if (
      this._selection_updating ||
        this._initializing ||
        isString(this.model.select_mode) ||
        this.model.select_mode === false ||  // selection disabled
        this.model.configuration.dataTree || // dataTree does not support selection
        e.srcElement?.innerText === "►"      // expand button
    ) {
      return
    }
    let indices: number[] = []
    const selected = this.model.source.selected
    const index: number = row._row.data._index

    if (e.ctrlKey || e.metaKey) {
      indices = [...selected.indices]
    } else if (e.shiftKey && this._last_selected_row) {
      const rows = row._row.parent.getDisplayRows()
      const start_idx = rows.indexOf(this._last_selected_row)
      if (start_idx !== -1) {
        const end_idx = rows.indexOf(row._row)
        const reverse = start_idx > end_idx
        const [start, end] = reverse ? [end_idx+1, start_idx+1] : [start_idx, end_idx]
        indices = rows.slice(start, end).map((r: any) => r.data._index)
        if (reverse) { indices = indices.reverse() }
      }
    }
    const flush = !(e.ctrlKey || e.metaKey || e.shiftKey)
    const includes = indices.includes(index)
    const remote = this.model.pagination === "remote"

    // Toggle the index on or off (if remote we let Python do the toggling)
    if (!includes || remote) {
      indices.push(index)
    } else {
      indices.splice(indices.indexOf(index), 1)
    }
    // Remove the first selected indices when selectable is an int.
    if (isNumber(this.model.select_mode)) {
      while (indices.length > this.model.select_mode) {
        indices.shift()
      }
    }
    const filtered = this._filter_selected(indices)
    if (!remote) {
      this.tabulator.deselectRow()
      this.tabulator.selectRow(filtered)
    }
    this._last_selected_row = row._row
    this._selection_updating = true
    if (!remote) {
      selected.indices = filtered
    }
    this.model.trigger_event(new SelectionEvent(indices, !includes, flush))
    this._selection_updating = false
  }

  _filter_selected(indices: number[]): number[] {
    const filtered = []
    for (const ind of indices) {
      if (this.model.selectable_rows == null ||
          this.model.selectable_rows.indexOf(ind) >= 0) {
        filtered.push(ind)
      }
    }
    return filtered
  }

  rowSelectionChanged(data: any, _row: any, selected: any, deselected: any): void {
    if (
      this._selection_updating ||
        this._initializing ||
        isBoolean(this.model.select_mode) ||
        isNumber(this.model.select_mode) ||
        this.model.configuration.dataTree
    ) {
      return
    }
    if (this.model.pagination === "remote") {
      const selected_indices = selected.map((x: any) => x._row.data._index)
      const deselected_indices = deselected.map((x: any) => x._row.data._index)
      if (selected_indices.length > 0) {
        this._selection_updating = true
        this.model.trigger_event(new SelectionEvent(selected_indices, true, false))
      }
      if (deselected_indices.length > 0) {
        this._selection_updating = true
        this.model.trigger_event(new SelectionEvent(deselected_indices, false, false))
      }
    } else {
      const indices: number[] = data.map((row: any) => row._index)
      const filtered = this._filter_selected(indices)
      this._selection_updating = indices.length === filtered.length
      this.model.source.selected.indices = filtered
    }
    this._selection_updating = false
  }

  cellEdited(cell: any): void {
    const field = cell._cell.column.field
    const column_def = this.columns.get(field)
    const index = cell.getData()._index
    const value = cell._cell.value
    if (column_def.validator === "numeric" && value === "") {
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
    embed_content: p.Property<boolean>
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
    page_size: p.Property<number | null>
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
  declare properties: DataTabulator.Props

  constructor(attrs?: Partial<DataTabulator.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.tabulator"

  static {
    this.prototype.default_view = DataTabulatorView

    this.define<DataTabulator.Props>(({Any, List, Bool, Nullable, Float, Ref, Str}) => ({
      aggregators:    [ Any,                     {} ],
      buttons:        [ Any,                     {} ],
      children:       [ Any,              new Map() ],
      configuration:  [ Any,                     {} ],
      columns:        [ List(Ref(TableColumn)), [] ],
      download:       [ Bool,              false ],
      editable:       [ Bool,               true ],
      embed_content:  [ Bool,               false ],
      expanded:       [ List(Float),           [] ],
      filename:       [ Str,         "table.csv" ],
      filters:        [ List(Any),              [] ],
      follow:         [ Bool,               true ],
      frozen_rows:    [ List(Float),           [] ],
      groupby:        [ List(Str),           [] ],
      hidden_columns: [ List(Str),           [] ],
      indexes:        [ List(Str),           [] ],
      layout:         [ TableLayout,     "fit_data" ],
      max_page:       [ Float,                   0 ],
      pagination:     [ Nullable(Str),      null ],
      page:           [ Float,                   0 ],
      page_size:      [ Nullable(Float),       null ],
      select_mode:    [ Any,                   true ],
      selectable_rows: [ Nullable(List(Float)), null ],
      source:         [ Ref(ColumnDataSource)       ],
      sorters:        [ List(Any),              [] ],
      cell_styles:    [ Any,                     {} ],
      theme_classes:  [ List(Str),           [] ],
    }))
  }
}
