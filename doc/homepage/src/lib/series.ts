/**
 * The hero app's data.
 *
 * Deliberately deterministic: the page is prerendered and then hydrated, so the server
 * and the client must produce byte-identical paths from the same controls. Anything
 * seeded from Math.random or Date.now would tear on hydration.
 *
 * This mirrors what the Python beside it does (cumulative normal increments, then a
 * moving average) closely enough that the two read as the same program.
 */

const N = 400

/** mulberry32: small, fast, and identical across engines. */
function rng(seed: number) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function seedFrom(label: string) {
  let h = 2166136261
  for (let i = 0; i < label.length; i++) {
    h ^= label.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

/** Box-Muller, drawing pairs so the stream stays aligned for a given seed. */
function normals(seed: number, n: number, sigma: number) {
  const next = rng(seed)
  const out = new Float64Array(n)
  for (let i = 0; i < n; i += 2) {
    const u = Math.max(next(), 1e-12)
    const v = next()
    const r = Math.sqrt(-2 * Math.log(u))
    out[i] = r * Math.cos(2 * Math.PI * v) * sigma
    if (i + 1 < n) out[i + 1] = r * Math.sin(2 * Math.PI * v) * sigma
  }
  return out
}

function movingAverage(values: Float64Array, window: number) {
  const w = Math.max(1, Math.round(window))
  const half = Math.floor(w / 2)
  const out = new Float64Array(values.length)
  let sum = 0
  let count = 0
  // Prefix-sum walk so changing the window stays cheap enough to run on every drag.
  const prefix = new Float64Array(values.length + 1)
  for (let i = 0; i < values.length; i++) prefix[i + 1] = prefix[i] + values[i]
  for (let i = 0; i < values.length; i++) {
    const lo = Math.max(0, i - half)
    const hi = Math.min(values.length, i + w - half)
    sum = prefix[hi] - prefix[lo]
    count = hi - lo
    out[i] = sum / count
  }
  return out
}

export interface ChartGeometry {
  /** SVG path for the unsmoothed walk. */
  raw: string
  /** SVG path for the moving average. */
  smooth: string
  /** Baseline y for the zero line, in view units. */
  zero: number
  width: number
  height: number
}

const WIDTH = 760
const HEIGHT = 340
const PAD_X = 18
const PAD_Y = 26

export function chartGeometry(ticker: string, sigma: number, window: number): ChartGeometry {
  const steps = normals(seedFrom(ticker), N, sigma)
  const walk = new Float64Array(N)
  let acc = 0
  for (let i = 0; i < N; i++) {
    acc += steps[i]
    walk[i] = acc
  }
  const smooth = movingAverage(walk, window)

  let min = Infinity
  let max = -Infinity
  for (let i = 0; i < N; i++) {
    if (walk[i] < min) min = walk[i]
    if (walk[i] > max) max = walk[i]
  }
  // Keep zero in frame so the y axis means something as sigma changes.
  min = Math.min(min, 0)
  max = Math.max(max, 0)
  const span = max - min || 1

  const x = (i: number) => PAD_X + (i / (N - 1)) * (WIDTH - PAD_X * 2)
  const y = (v: number) => HEIGHT - PAD_Y - ((v - min) / span) * (HEIGHT - PAD_Y * 2)

  const toPath = (values: Float64Array) => {
    let d = `M${x(0).toFixed(1)} ${y(values[0]).toFixed(1)}`
    for (let i = 1; i < N; i++) d += ` L${x(i).toFixed(1)} ${y(values[i]).toFixed(1)}`
    return d
  }

  return {
    raw: toPath(walk),
    smooth: toPath(smooth),
    zero: y(0),
    width: WIDTH,
    height: HEIGHT,
  }
}
