import {describe, it, expect, vi, beforeEach} from "vitest"
import {ChildModelAdapter, AnyWidgetModelAdapter} from "../models/anywidget_component"
import {ReactiveESM} from "./mocks/reactive_esm"

// Helper to create a parent adapter with mock model
function createParentAdapter(): AnyWidgetModelAdapter {
  const model = new ReactiveESM() as any
  model.data = {attributes: {esm_constants: {}}}
  model.attributes = {}
  model.trigger_event = vi.fn()
  return new AnyWidgetModelAdapter(model)
}

describe("ChildModelAdapter", () => {
  let parent: AnyWidgetModelAdapter
  let child: ChildModelAdapter

  beforeEach(() => {
    parent = createParentAdapter()
    child = new ChildModelAdapter("child-1", {color: "red", size: 10}, parent)
  })

  // --- get/set ---

  it("get returns initial state value", () => {
    expect(child.get("color")).toBe("red")
    expect(child.get("size")).toBe(10)
  })

  it("get returns undefined for unknown key", () => {
    expect(child.get("unknown")).toBeUndefined()
  })

  it("set updates internal state", () => {
    child.set("color", "blue")
    expect(child.get("color")).toBe("blue")
  })

  it("set marks field as dirty", () => {
    child.set("color", "blue")
    // Dirty tracking is internal, but save_changes should send the change
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    child.save_changes()
    expect(triggerSpy).toHaveBeenCalledTimes(1)
    const eventArg = triggerSpy.mock.calls[0][0]
    expect(eventArg.data._child_save_changes.changes).toEqual({color: "blue"})
  })

  // --- save_changes ---

  it("save_changes is no-op when nothing is dirty", () => {
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    child.save_changes()
    expect(triggerSpy).not.toHaveBeenCalled()
  })

  it("save_changes only sends dirty fields", () => {
    child.set("color", "green")
    child.set("size", 20)
    child.save_changes()

    // After save, changing only one field should send just that field
    child.set("size", 30)
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    triggerSpy.mockClear()
    child.save_changes()

    const eventArg = triggerSpy.mock.calls[0][0]
    expect(eventArg.data._child_save_changes.changes).toEqual({size: 30})
  })

  it("save_changes clears dirty set", () => {
    child.set("color", "blue")
    child.save_changes()
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    triggerSpy.mockClear()
    child.save_changes()
    expect(triggerSpy).not.toHaveBeenCalled()
  })

  it("save_changes includes model_id in event", () => {
    child.set("color", "blue")
    child.save_changes()
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    const eventArg = triggerSpy.mock.calls[0][0]
    expect(eventArg.data._child_save_changes.model_id).toBe("child-1")
  })

  // --- on/off ---

  it("on registers callback for change event", () => {
    const cb = vi.fn()
    child.on("change:color", cb)
    child._update_state("color", "blue")
    expect(cb).toHaveBeenCalledWith("blue")
  })

  it("on registers callback for generic change event", () => {
    const cb = vi.fn()
    child.on("change", cb)
    child._update_state("color", "blue")
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it("off removes specific callback", () => {
    const cb = vi.fn()
    child.on("change:color", cb)
    child.off("change:color", cb)
    child._update_state("color", "blue")
    expect(cb).not.toHaveBeenCalled()
  })

  it("off without callback removes all listeners for event", () => {
    const cb1 = vi.fn()
    const cb2 = vi.fn()
    child.on("change:color", cb1)
    child.on("change:color", cb2)
    child.off("change:color")
    child._update_state("color", "blue")
    expect(cb1).not.toHaveBeenCalled()
    expect(cb2).not.toHaveBeenCalled()
  })

  it("off with no args clears all listeners", () => {
    const cb1 = vi.fn()
    const cb2 = vi.fn()
    child.on("change:color", cb1)
    child.on("change", cb2)
    child.off()
    child._update_state("color", "blue")
    expect(cb1).not.toHaveBeenCalled()
    expect(cb2).not.toHaveBeenCalled()
  })

  // --- send ---

  it("send routes through parent DataEvent with child model ID", () => {
    child.send({type: "query", sql: "SELECT 1"})
    const triggerSpy = parent.model.trigger_event as ReturnType<typeof vi.fn>
    expect(triggerSpy).toHaveBeenCalledTimes(1)
    const eventArg = triggerSpy.mock.calls[0][0]
    expect(eventArg.data._child_model_id).toBe("child-1")
    expect(eventArg.data.type).toBe("query")
  })

  // --- _update_state ---

  it("_update_state fires change:key listeners with decoded value", () => {
    const cb = vi.fn()
    child.on("change:color", cb)
    child._update_state("color", "green")
    expect(cb).toHaveBeenCalledWith("green")
    expect(child.get("color")).toBe("green")
  })

  it("_update_state fires generic change listeners", () => {
    const cb = vi.fn()
    child.on("change", cb)
    child._update_state("size", 42)
    expect(cb).toHaveBeenCalledTimes(1)
  })

  // --- widget_manager ---

  it("widget_manager is a stable reference", () => {
    const wm1 = child.widget_manager
    const wm2 = child.widget_manager
    expect(wm1).toBe(wm2) // Object.is identity
  })

  it("widget_manager.get_model returns a promise", () => {
    const result = child.widget_manager.get_model("some-id")
    expect(result).toBeInstanceOf(Promise)
  })
})
