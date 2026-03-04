// Minimal stubs for Bokeh types used by anywidget_component.ts imports.
// These are never called — they just satisfy TypeScript/Vitest import resolution.
export class ModelEvent {
  origin: any
  constructor() {}
  protected get event_values(): any { return {} }
}
export function server_event(_name: string) {
  return (_target: any) => {}
}
export function div() { return document.createElement("div") }
export class ImportedStyleSheet {}
export class Enum {}
export class LayoutDOMView {}
export function isArray(x: any): x is any[] { return Array.isArray(x) }
export function serializeEvent() { return {} }
export class DOMEvent {}
export class HTMLBox {}
export class HTMLBoxView {}
export function set_size() {}
export function convertUndefined(x: any) { return x }
export function formatError(e: any) { return String(e) }
export function transform(code: string) { return {code} }
