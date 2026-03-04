import {describe, it, expect, beforeEach} from "vitest"
import {AnyWidgetModelAdapter} from "../models/anywidget_component"
import {ReactiveESM} from "./mocks/reactive_esm"

// Helper to create an adapter with a mock model
function createAdapter(attrs: Record<string, any> = {}): AnyWidgetModelAdapter {
  const model = new ReactiveESM() as any
  model.data = {attributes: {esm_constants: {}, ...attrs}}
  model.attributes = {}
  return new AnyWidgetModelAdapter(model)
}

describe("AnyWidgetModelAdapter._decode_binary", () => {
  let adapter: AnyWidgetModelAdapter

  beforeEach(() => {
    adapter = createAdapter()
  })

  it("returns null unchanged", () => {
    expect(adapter._decode_binary(null)).toBeNull()
  })

  it("returns undefined unchanged", () => {
    expect(adapter._decode_binary(undefined)).toBeUndefined()
  })

  it("returns primitives unchanged", () => {
    expect(adapter._decode_binary(42)).toBe(42)
    expect(adapter._decode_binary("hello")).toBe("hello")
    expect(adapter._decode_binary(true)).toBe(true)
  })

  it("decodes _pnl_bytes to DataView", () => {
    // btoa("AB") = "QUI=" (bytes 0x41, 0x42)
    const encoded = {_pnl_bytes: btoa("AB")}
    const result = adapter._decode_binary(encoded)
    expect(result).toBeInstanceOf(DataView)
    expect(result.byteLength).toBe(2)
    expect(result.getUint8(0)).toBe(0x41) // 'A'
    expect(result.getUint8(1)).toBe(0x42) // 'B'
  })

  it("preserves array reference when no binary data (React #185 fix)", () => {
    const arr = [1, 2, 3]
    const result = adapter._decode_binary(arr)
    expect(result).toBe(arr) // same reference — Object.is must be true
  })

  it("preserves object reference when no binary data", () => {
    const obj = {a: 1, b: "hello"}
    const result = adapter._decode_binary(obj)
    expect(result).toBe(obj) // same reference
  })

  it("returns new array when binary data is decoded in array", () => {
    const arr = [1, {_pnl_bytes: btoa("A")}, 3]
    const result = adapter._decode_binary(arr)
    expect(result).not.toBe(arr) // different reference — array was modified
    expect(result[0]).toBe(1)
    expect(result[1]).toBeInstanceOf(DataView)
    expect(result[2]).toBe(3)
  })

  it("returns new object when binary data is decoded in nested object", () => {
    const obj = {a: 1, b: {_pnl_bytes: btoa("X")}}
    const result = adapter._decode_binary(obj)
    expect(result).not.toBe(obj)
    expect(result.a).toBe(1)
    expect(result.b).toBeInstanceOf(DataView)
  })

  it("preserves DataView instances (does not recurse into them)", () => {
    const dv = new DataView(new ArrayBuffer(4))
    const result = adapter._decode_binary(dv)
    expect(result).toBe(dv) // same reference
  })

  it("preserves ArrayBuffer instances", () => {
    const ab = new ArrayBuffer(4)
    const result = adapter._decode_binary(ab)
    expect(result).toBe(ab)
  })

  it("handles deeply nested binary data", () => {
    const nested = {
      level1: {
        level2: [
          {_pnl_bytes: btoa("deep")},
          "keep",
        ],
      },
    }
    const result = adapter._decode_binary(nested)
    expect(result).not.toBe(nested)
    expect(result.level1.level2[0]).toBeInstanceOf(DataView)
    expect(result.level1.level2[1]).toBe("keep")
  })
})
