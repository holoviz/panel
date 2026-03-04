import {describe, it, expect, vi, beforeEach} from "vitest"
import {AnyWidgetModelAdapter} from "../models/anywidget_component"
import {ReactiveESM} from "./mocks/reactive_esm"

// Helper to create an adapter with configurable model attributes
function createAdapter(opts: {
  dataAttrs?: Record<string, any>
  modelAttrs?: Record<string, any>
  constants?: Record<string, any>
} = {}): AnyWidgetModelAdapter {
  const model = new ReactiveESM() as any
  const constants = opts.constants || {}
  model.data = {
    attributes: {
      esm_constants: constants,
      ...opts.dataAttrs,
    },
  }
  model.attributes = opts.modelAttrs || {}
  model.trigger_event = vi.fn()
  model.setv = vi.fn()
  return new AnyWidgetModelAdapter(model)
}

describe("AnyWidgetModelAdapter — name translation", () => {
  it("_to_param_name returns mapped name when trait collides", () => {
    const adapter = createAdapter({
      constants: {_trait_name_map: {height: "w_height", width: "w_width"}},
    })
    expect(adapter._to_param_name("height")).toBe("w_height")
    expect(adapter._to_param_name("width")).toBe("w_width")
  })

  it("_to_param_name passes through unmapped names", () => {
    const adapter = createAdapter({
      constants: {_trait_name_map: {height: "w_height"}},
    })
    expect(adapter._to_param_name("value")).toBe("value")
  })

  it("_to_trait_name reverses the mapping", () => {
    const adapter = createAdapter({
      constants: {_trait_name_map: {height: "w_height"}},
    })
    expect(adapter._to_trait_name("w_height")).toBe("height")
  })

  it("_to_trait_name passes through unmapped param names", () => {
    const adapter = createAdapter()
    expect(adapter._to_trait_name("value")).toBe("value")
  })

  it("name maps are cached after first access", () => {
    const adapter = createAdapter({
      constants: {_trait_name_map: {height: "w_height"}},
    })
    // First access builds cache
    expect(adapter._to_param_name("height")).toBe("w_height")
    // Mutate constants (shouldn't affect cached result)
    adapter.model.data.attributes.esm_constants._trait_name_map = {}
    expect(adapter._to_param_name("height")).toBe("w_height")
  })
})

describe("AnyWidgetModelAdapter — get", () => {
  it("gets value from data.attributes", () => {
    const adapter = createAdapter({dataAttrs: {value: 42}})
    expect(adapter.get("value")).toBe(42)
  })

  it("falls back to model.attributes", () => {
    const adapter = createAdapter({modelAttrs: {label: "hello"}})
    expect(adapter.get("label")).toBe("hello")
  })

  it("translates trait name for get", () => {
    const adapter = createAdapter({
      dataAttrs: {w_height: 500},
      constants: {_trait_name_map: {height: "w_height"}},
    })
    expect(adapter.get("height")).toBe(500)
  })

  it("returns cached widget_serialization values", () => {
    const adapter = createAdapter({
      constants: {
        _widget_serialization_values: {
          layers: ["IPY_MODEL_abc", "IPY_MODEL_def"],
        },
      },
    })
    const result1 = adapter.get("layers")
    const result2 = adapter.get("layers")
    expect(result1).toEqual(["IPY_MODEL_abc", "IPY_MODEL_def"])
    // CRITICAL: Same reference on repeated calls (React useSyncExternalStore)
    expect(result1).toBe(result2)
  })

  it("converts ArrayBuffer to DataView", () => {
    const buf = new ArrayBuffer(4)
    const adapter = createAdapter({dataAttrs: {binary: buf}})
    const result = adapter.get("binary")
    expect(result).toBeInstanceOf(DataView)
  })

  it("decodes _pnl_bytes in get result", () => {
    const adapter = createAdapter({
      dataAttrs: {data: {_pnl_bytes: btoa("test")}},
    })
    const result = adapter.get("data")
    expect(result).toBeInstanceOf(DataView)
    expect(result.byteLength).toBe(4)
  })
})

describe("AnyWidgetModelAdapter — set", () => {
  it("accumulates data changes for known data attributes", () => {
    const adapter = createAdapter({dataAttrs: {value: 0}})
    adapter.set("value", 42)
    expect(adapter.data_changes).toEqual({value: 42})
  })

  it("accumulates model changes for known model attributes", () => {
    const adapter = createAdapter({modelAttrs: {label: "old"}})
    adapter.set("label", "new")
    expect(adapter.model_changes).toEqual({label: "new"})
  })

  it("translates trait name for set", () => {
    const adapter = createAdapter({
      dataAttrs: {w_height: 0},
      constants: {_trait_name_map: {height: "w_height"}},
    })
    adapter.set("height", 600)
    expect(adapter.data_changes).toEqual({w_height: 600})
  })

  it("skips undefined values", () => {
    const adapter = createAdapter({dataAttrs: {value: 0}})
    adapter.set("value", undefined)
    expect(adapter.data_changes).toEqual({})
  })

  it("converts DataView to ArrayBuffer", () => {
    const adapter = createAdapter({dataAttrs: {binary: new ArrayBuffer(0)}})
    const dv = new DataView(new ArrayBuffer(4))
    adapter.set("binary", dv)
    expect(adapter.data_changes.binary).toBeInstanceOf(ArrayBuffer)
  })
})

describe("AnyWidgetModelAdapter — save_changes", () => {
  it("flushes model changes via setv", () => {
    const adapter = createAdapter({modelAttrs: {label: "old"}})
    adapter.set("label", "new")
    adapter.save_changes()
    expect(adapter.model.setv).toHaveBeenCalledWith({label: "new"})
    expect(adapter.model_changes).toEqual({})
  })

  it("flushes data changes via data model setv", () => {
    const adapter = createAdapter({dataAttrs: {value: 0}})
    // Make data model have setv
    adapter.model.data.setv = vi.fn()
    adapter.set("value", 42)
    adapter.save_changes()
    expect(adapter.model.data.setv).toHaveBeenCalledWith({value: 42})
    expect(adapter.data_changes).toEqual({})
  })
})

describe("AnyWidgetModelAdapter — send", () => {
  it("triggers DataEvent with data", () => {
    const adapter = createAdapter()
    adapter.send({type: "query"})
    const triggerSpy = adapter.model.trigger_event as ReturnType<typeof vi.fn>
    expect(triggerSpy).toHaveBeenCalledTimes(1)
    const event = triggerSpy.mock.calls[0][0]
    expect(event.data.type).toBe("query")
  })

  it("base64-encodes binary buffers", () => {
    const adapter = createAdapter()
    const buf = new Uint8Array([65, 66, 67]).buffer // "ABC"
    adapter.send({type: "data"}, undefined, [buf])
    const triggerSpy = adapter.model.trigger_event as ReturnType<typeof vi.fn>
    const event = triggerSpy.mock.calls[0][0]
    expect(event.data._b64_buffers).toHaveLength(1)
    expect(event.data._b64_buffers[0]).toBe(btoa("ABC"))
  })

  it("supports legacy calling convention with buffers in options", () => {
    const adapter = createAdapter()
    const buf = new Uint8Array([1, 2]).buffer
    adapter.send({type: "data"}, {buffers: [buf]})
    const triggerSpy = adapter.model.trigger_event as ReturnType<typeof vi.fn>
    const event = triggerSpy.mock.calls[0][0]
    expect(event.data._b64_buffers).toHaveLength(1)
  })
})

describe("AnyWidgetModelAdapter — on/off", () => {
  it("on('change:x') registers wrapped callback via model.watch", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb = vi.fn()
    adapter.on("change:value", cb)
    // The watch method should have been called
    expect(adapter.model._watchers.get("value")?.size).toBe(1)
  })

  it("on('change:x') wraps callback to pass new value", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb = vi.fn()
    adapter.on("change:value", cb)
    // Simulate Bokeh signal firing by calling the wrapped callback
    const wrapped = Array.from(adapter.model._watchers.get("value")!)[0] as Function
    wrapped()
    expect(cb).toHaveBeenCalledWith(10)
  })

  it("on('change') registers generic change callback and watchers on all data attrs", () => {
    const adapter = createAdapter({dataAttrs: {value: 10, label: "hi"}})
    const cb = vi.fn()
    adapter.on("change", cb)
    // Generic callbacks are stored internally
    expect(adapter._generic_change_cbs.has(cb)).toBe(true)
    // Watchers should be registered on each data attr (except esm_constants)
    expect(adapter._generic_change_watchers.has(cb)).toBe(true)
    const watchers = adapter._generic_change_watchers.get(cb)!
    expect(watchers.length).toBe(2) // value and label
  })

  it("on('change') fires callback when any property watcher triggers", () => {
    const adapter = createAdapter({dataAttrs: {value: 10, label: "hi"}})
    const cb = vi.fn()
    adapter.on("change", cb)
    // Simulate a property change by triggering the watcher for "value"
    const valueWatchers = adapter.model._watchers.get("value")
    expect(valueWatchers).toBeDefined()
    for (const w of valueWatchers!) {
      w()
    }
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it("off('change:x', cb) unregisters the wrapped callback", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb = vi.fn()
    adapter.on("change:value", cb)
    adapter.off("change:value", cb)
    // The specific change:value watcher should be removed, but generic watchers
    // (if any) may remain. Only the change:value wrapped cb is removed.
    const watchers = adapter.model._watchers.get("value")
    // Check that the specific watcher was removed (size 0 means no specific watchers)
    expect(watchers?.size ?? 0).toBe(0)
  })

  it("off('change', cb) removes specific generic callback and its watchers", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb = vi.fn()
    adapter.on("change", cb)
    adapter.off("change", cb)
    expect(adapter._generic_change_cbs.has(cb)).toBe(false)
    expect(adapter._generic_change_watchers.has(cb)).toBe(false)
  })

  it("off('change') clears all generic callbacks and their watchers", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb1 = vi.fn()
    const cb2 = vi.fn()
    adapter.on("change", cb1)
    adapter.on("change", cb2)
    adapter.off("change")
    expect(adapter._generic_change_cbs.size).toBe(0)
    expect(adapter._generic_change_watchers.size).toBe(0)
  })

  it("off() with no args clears everything including generic watchers", () => {
    const adapter = createAdapter({dataAttrs: {value: 10}})
    const cb1 = vi.fn()
    const cb2 = vi.fn()
    adapter.on("change:value", cb1)
    adapter.on("change", cb2)
    adapter.off()
    expect(adapter._generic_change_cbs.size).toBe(0)
    expect(adapter._generic_change_watchers.size).toBe(0)
    expect(adapter._cb_map.size).toBe(0)
  })
})

describe("AnyWidgetModelAdapter — widget_manager", () => {
  it("is a stable reference (same object on repeated access)", () => {
    const adapter = createAdapter()
    const wm1 = adapter.widget_manager
    const wm2 = adapter.widget_manager
    expect(wm1).toBe(wm2)
  })

  it("get_model returns a promise", () => {
    const adapter = createAdapter()
    const result = adapter.widget_manager.get_model("some-id")
    expect(result).toBeInstanceOf(Promise)
  })
})

describe("AnyWidgetModelAdapter — _cached_ws_values", () => {
  it("returns same reference on repeated get() for widget_serialization values", () => {
    const adapter = createAdapter({
      constants: {
        _widget_serialization_values: {
          layers: ["IPY_MODEL_a", "IPY_MODEL_b"],
          controls: {zoom: "IPY_MODEL_c"},
        },
      },
    })

    const layers1 = adapter.get("layers")
    const layers2 = adapter.get("layers")
    expect(layers1).toBe(layers2) // same reference

    const controls1 = adapter.get("controls")
    const controls2 = adapter.get("controls")
    expect(controls1).toBe(controls2) // same reference
  })
})
