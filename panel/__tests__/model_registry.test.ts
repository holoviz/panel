import {describe, it, expect, vi, beforeEach} from "vitest"
import {ModelRegistry, Deferred} from "../models/anywidget_component"

describe("Deferred", () => {
  it("resolves with the given value", async () => {
    const d = new Deferred<number>()
    d.resolve(42)
    await expect(d.promise).resolves.toBe(42)
  })

  it("rejects with the given reason", async () => {
    const d = new Deferred<number>()
    d.reject(new Error("fail"))
    await expect(d.promise).rejects.toThrow("fail")
  })
})

describe("ModelRegistry", () => {
  let registry: ModelRegistry

  beforeEach(() => {
    registry = new ModelRegistry()
  })

  it("register then get resolves immediately", async () => {
    const adapter = {model_id: "m1"}
    registry.register("m1", adapter)
    const result = await registry.get("m1")
    expect(result).toBe(adapter)
  })

  it("get before register resolves when registered", async () => {
    const pending = registry.get("m2")
    const adapter = {model_id: "m2"}
    registry.register("m2", adapter)
    const result = await pending
    expect(result).toBe(adapter)
  })

  it("get_resolved returns null for unknown id", () => {
    expect(registry.get_resolved("unknown")).toBeNull()
  })

  it("get_resolved returns adapter for registered id", () => {
    const adapter = {model_id: "m3"}
    registry.register("m3", adapter)
    expect(registry.get_resolved("m3")).toBe(adapter)
  })

  it("delete removes registered adapter", () => {
    const adapter = {model_id: "m4"}
    registry.register("m4", adapter)
    registry.delete("m4")
    expect(registry.get_resolved("m4")).toBeNull()
  })

  it("delete also removes pending deferred", () => {
    // get creates a pending deferred
    registry.get("m5")
    registry.delete("m5")
    // Re-registering after delete should still work
    const adapter = {model_id: "m5"}
    registry.register("m5", adapter)
    expect(registry.get_resolved("m5")).toBe(adapter)
  })

  it("times out after 10s if never registered", async () => {
    vi.useFakeTimers()
    const pending = registry.get("m6")
    vi.advanceTimersByTime(10001)
    await expect(pending).rejects.toThrow("timed out after 10s")
    vi.useRealTimers()
  })

  it("does not time out if registered before 10s", async () => {
    vi.useFakeTimers()
    const pending = registry.get("m7")
    vi.advanceTimersByTime(5000)
    registry.register("m7", {model_id: "m7"})
    // Advance past timeout — should NOT reject since we already resolved
    vi.advanceTimersByTime(6000)
    const result = await pending
    expect(result).toEqual({model_id: "m7"})
    vi.useRealTimers()
  })
})
