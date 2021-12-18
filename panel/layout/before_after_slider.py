"""The BeforeAfterSlider layout enables you to quickly compare two panels"""
import panel as pn
import param

CSS = """
.before-after-container {
    position: relative;
    height:100%;
    width:100%
}
.before-after-container .outer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
.before-after-container .inner,
 {
    height: 100%
}
.pn-beforeafter-slider {
    position:absolute;
    height:100%;
    border-radius: 8px;
    cursor: move;
}
"""

class BeforeAfterSlider(pn.reactive.ReactiveHTML):
    """The BeforeAfterSlider layout enables you to quickly compare two panels layed out on top of
    each other with a part of the *before* panel shown on one side of a slider and a part of the
    *after* panel shown on the other side."""
    value = param.Integer(50, bounds=(0, 100), doc="""
        The percentage of the *after* panel to show.""")
    before = param.Parameter(allow_None=False, doc="""
        The before panel""")
    after = param.Parameter(allow_None=False, doc="""
        The after panel""")

    slider_width = param.Integer(default=12, bounds=(0, 100), doc="""
        The width of the slider in pixels""")
    slider_color = param.Color(default="silver", doc="""
        The color of the slider""")   

    _template = f"<style>{CSS}</style>""" + """
<style id="slider_style"></style>
<div id="container" class='before-after-container'>
    <div id="before" class='outer'>
        <div id="before_inner" class="inner" >${before}</div>
    </div>
    <div id="after" class='outer' style="overflow:hidden">
        <div id="after_inner" class="inner">${after}</div>
    </div>
    <div id="slider" class="pn-beforeafter-slider"></div>
</div>
"""

    _scripts = {
        "render": """
window.addEventListener("resize", self.layoutPanel);

function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
}
function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    
    current = e.clientX
    start = view.el.getBoundingClientRect().left
    end = start + view.el.clientWidth
    
    value = parseInt( (current-start)/view.el.clientWidth*100  )
    value = Math.max(0,Math.min(value,100))
    data.value = value
}
function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
}
slider.onmousedown = dragMouseDown   

""",
        "after_layout": """
self.layoutPanel()
self.value()
""",
        "handle_change": """
data.value=parseInt(event.target.value);
""",
        "value": """
adjustment = parseInt((100-data.value)/100*10)
after.style.width=`calc(${data.value}% - ${adjustment}px)`
slider.style.left = after.style.width
""",
        "slider_color": "self.slider_style()",
        "slider_width": "self.slider_style()",
        "slider_style": """
slider_style.innerHTML=`
.before-after-container .pn-beforeafter-slider {
    width: ${data.slider_width}px;
    background: ${data.slider_color};
}
.before-after-container .slider::-moz-range-thumb {
    width: ${data.slider_width}px;
    background: ${data.slider_color};
}`""",
    "layoutPanel": """
width=view.el.offsetWidth-12
height=view.el.offsetHeight-10
after.children[0].style.width=`${width}px`
before.children[0].style.width=`${width}px`
after.children[0].style.height=`${height}px`
before.children[0].style.height=`${height}px`
self.slider_style()
"""
}

if __name__.startswith("bokeh"):
    import hvplot.pandas
    import pandas as pd
    pn.extension(sizing_mode="stretch_width")

    ACCENT_COLOR = "#D2386C"

    data = pd.DataFrame({"y": range(10)})
    before = data.hvplot().opts(color="green", line_width=6, responsive=True, height=400)
    after = data.hvplot().opts(color="red", line_width=6, responsive=True, height=400)

    before = pn.Spacer(background="red", sizing_mode="stretch_both")
    after = pn.Spacer(background="green", sizing_mode="stretch_both")

    before_after = BeforeAfterSlider(value=20, before=before, after=after, height=400)
    controls = pn.Param(before_after, parameters=["value", "slider_width", "slider_color"])
    pn.template.FastListTemplate(
        site="Awesome Panel",
        title="Before After Slider",
        sidebar=[controls],
        main=[before_after],
        accent_base_color=ACCENT_COLOR,
        header_background=ACCENT_COLOR,
    ).servable()