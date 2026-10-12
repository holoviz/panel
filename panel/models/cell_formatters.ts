// Port of the Bokeh CellFormatter models (bokehjs/src/lib/models/widgets/tables/cell_formatters.ts)
// operating on plain specs, so that Tabulator does not depend on the bokeh-tables bundle.
import {div, i} from "@bokehjs/core/dom"
import {color2css, rgba2css} from "@bokehjs/core/util/color"
import {to_fixed} from "@bokehjs/core/util/string"
import {datetime} from "@bokehjs/core/util/templating"
import {isNumber, isString} from "@bokehjs/core/util/types"
import {NumeralTickFormatter} from "@bokehjs/models/formatters/numeral_tick_formatter"
import {ColorMapper} from "@bokehjs/models/mappers/color_mapper"
import {_} from "underscore.template"

export type CellFormatterSpec = {type: string, [key: string]: any}

export type CellFormatterFn = (value: any, data: {[key: string]: any}) => string | HTMLElement

type Formatted = {value: any, data: {[key: string]: any}}

function resolve(spec: any, data: {[key: string]: any}): any {
  if (spec == null) {
    return null
  } else if ("value" in spec) {
    return spec.value
  } else if ("field" in spec) {
    return data[spec.field]
  }
  return null
}

function resolve_color(spec: any, data: {[key: string]: any}): string | null {
  if (spec == null) {
    return null
  } else if ("value" in spec) {
    return spec.value == null ? null : color2css(spec.value)
  } else if ("field" in spec) {
    const value = data[spec.field]
    if (spec.transform instanceof ColorMapper) {
      const [r, g, b, a] = spec.transform.rgba_mapper.v_compute([value])
      return rgba2css([r, g, b, a])
    }
    return color2css(value)
  }
  return null
}

function string_format(spec: CellFormatterSpec, {value, data}: Formatted): HTMLElement {
  if (Number.isNaN(value)) {
    value = spec.nan_format
  } else if (value == null) {
    value = spec.null_format
  }

  const text = div(value == null ? "" : `${value}`)

  switch (resolve(spec.font_style, data)) {
    case "italic":
      text.style.fontStyle = "italic"
      break
    case "bold":
      text.style.fontWeight = "bold"
      break
    case "bold italic":
      text.style.fontStyle = "italic"
      text.style.fontWeight = "bold"
      break
  }

  const text_align = resolve(spec.text_align, data)
  if (text_align != null) {
    text.style.textAlign = text_align
  }
  const color = resolve_color(spec.text_color, data)
  if (color != null) {
    text.style.color = color
  }
  const background_color = resolve_color(spec.background_color, data)
  if (background_color != null) {
    text.style.backgroundColor = background_color
  }
  return text
}

function scientific_value(spec: CellFormatterSpec, value: any): any {
  const need_sci = Math.abs(value) <= 10.0**spec.power_limit_low || Math.abs(value) >= 10.0**spec.power_limit_high
  // toExponential does not handle precision values < 0 correctly
  const precision = Math.max(spec.precision, 1)
  if (Number.isNaN(value)) {
    return spec.nan_format
  } else if (value == null) {
    return spec.null_format
  } else if (value == 0) {
    return to_fixed(value, 1)
  } else if (need_sci) {
    return value.toExponential(precision)
  }
  return to_fixed(value, precision)
}

function date_format(format: string): string {
  // using definitions provided here: https://api.jqueryui.com/datepicker/
  // except not implementing TICKS
  switch (format) {
    case "ATOM":
    case "W3C":
    case "RFC-3339":
    case "ISO-8601":
      return "%Y-%m-%d"
    case "COOKIE":
      return "%a, %d %b %Y"
    case "RFC-850":
      return "%A, %d-%b-%y"
    case "RFC-1123":
    case "RFC-2822":
      return "%a, %e %b %Y"
    case "RSS":
    case "RFC-822":
    case "RFC-1036":
      return "%a, %e %b %y"
    case "TIMESTAMP":
      return "@"
    default:
      return format
  }
}

function date_value(spec: CellFormatterSpec, value: any): any {
  function parse(date: string) {
    /* Parse bare dates as UTC. */
    const has_tz = /Z$|[+-]\d\d((:?)\d\d)?$/.test(date) // ISO 8601 TZ designation or offset
    const iso_date = has_tz ? date : `${date}Z`
    return new Date(iso_date).getTime()
  }

  let epoch: any
  if (value == null || isNumber(value)) {
    epoch = value
  } else if (isString(value)) {
    const num = Number(value)
    epoch = isNaN(num) ? parse(value) : num
  } else if (value instanceof Date) {
    epoch = value.valueOf()
  } else {
    epoch = Number(value)
  }

  const NaT = -9223372036854776.0
  if (Number.isNaN(epoch) || epoch == NaT) {
    return spec.nan_format
  } else if (value == null) {
    return spec.null_format
  }
  return datetime(epoch, date_format(spec.format))
}

export function cell_formatter(spec: CellFormatterSpec): CellFormatterFn | null {
  switch (spec.type) {
    case "StringFormatter":
      return (value, data) => string_format(spec, {value, data})
    case "ScientificFormatter":
      return (value, data) => string_format(spec, {value: scientific_value(spec, value), data})
    case "NumberFormatter": {
      const numeral = new NumeralTickFormatter({format: spec.format, language: spec.language, rounding: spec.rounding})
      return (value, data) => {
        if (!Number.isNaN(value) && value != null) {
          value = numeral.doFormat([value], {loc: 0})[0]
        }
        return string_format(spec, {value, data})
      }
    }
    case "DateFormatter":
      return (value, data) => string_format(spec, {value: date_value(spec, value), data})
    case "BooleanFormatter":
      return (value) => value ? i({class: spec.icon}).outerHTML : ""
    case "HTMLTemplateFormatter": {
      const template = _.template(spec.template)
      return (value, data) => value == null ? "" : template({...data, value})
    }
  }
  return null
}
