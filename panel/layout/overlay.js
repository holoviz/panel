const ANCHORS = {
  "top-left":      {top: 0, left: 0},
  "top-center":    {top: 0, left: "50%", transform: "translateX(-50%)"},
  "top-right":     {top: 0, right: 0},
  "center-left":   {top: "50%", left: 0, transform: "translateY(-50%)"},
  "center":        {top: "50%", left: "50%", transform: "translate(-50%,-50%)"},
  "center-right":  {top: "50%", right: 0, transform: "translateY(-50%)"},
  "bottom-left":   {bottom: 0, left: 0},
  "bottom-center": {bottom: 0, left: "50%", transform: "translateX(-50%)"},
  "bottom-right":  {bottom: 0, right: 0},
}

const coord = (v) => (typeof v === "number" ? `${v}px` : v)

// Overlay has a definite size if a stretch/scale_both mode or explicit
// dims are set; otherwise it hugs the natural size of `base`.
const isDefinite = (model) => {
  const sm = model.sizing_mode || ""
  return sm.includes("stretch") || sm === "scale_both" ||
         model.width != null || model.height != null
}

export function render({ model }) {
  const el = document.createElement("div")
  // NOTE: not "overlay" -- ReactiveESM already names the host container
  // after the component's class_name ("Overlay" -> ".overlay"), so
  // reusing it here would produce two nested `.overlay` elements.
  el.classList.add("overlay-container")
  Object.assign(el.style, {position: "relative"})

  // Bokeh already stretches its own wrapper around `el` to 100%/100%
  // whenever sizing_mode is definite, but that only gives `el` a
  // definite WIDTH for free -- a block-level element's height doesn't
  // inherit from its container the same way. Without this, `el` (and
  // anything inside it sized via height:100%, like a stretch_both
  // base) collapses to zero height even though the outer component
  // correctly fills the page. Mirrors the same isDefinite check used
  // for the base below.
  if (isDefinite(model)) {
    el.style.width = "100%"
    el.style.height = "100%"
  }

  let baseNode = null
  let panelBoxes = []

  const renderBase = () => {
    if (baseNode) { baseNode.remove(); baseNode = null }
    const base = model.get_child("base")
    if (base) {
      baseNode = base
      // Only force the base to fill the container when the Overlay's
      // own size is definite (stretch_* / scale_both / explicit
      // width+height) -- otherwise a content-sized base would be
      // forced to 100% of a container that hasn't sized itself yet
      // and collapse to zero.
      if (isDefinite(model) && baseNode.style) {
        baseNode.style.width = "100%"
        baseNode.style.height = "100%"
      }
      el.insertBefore(baseNode, el.firstChild)  // base sits beneath panels
    }
  }

  const renderPanels = () => {
    panelBoxes.forEach((b) => b.remove())
    panelBoxes = []
    const panels = model.get_child("objects")
    const anchors = model._anchors || []
    panels.forEach((child, i) => {
      const where = anchors[i]
      const box = document.createElement("div")
      box.style.position = "absolute"
      box.classList.add("overlay-panel")
      Object.assign(
        box.style,
        Array.isArray(where)
          ? {left: coord(where[0]), top: coord(where[1])}
          : (ANCHORS[where] || ANCHORS["top-left"])
      )
      // Not part of the reactivity contract -- purely a convenience
      // hook for styling/tests to select a panel by its anchor.
      if (typeof where === "string") {
        box.dataset.anchor = where
      } else if (Array.isArray(where)) {
        box.dataset.anchor = `${where[0]},${where[1]}`
      }
      box.appendChild(child)
      el.appendChild(box)
      panelBoxes.push(box)
    })
  }

  renderBase()
  renderPanels()
  model.on("base", renderBase)
  model.on("objects", renderPanels)
  model.on("_anchors", renderPanels)

  return el
}
