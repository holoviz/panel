"""The `Modal` is an element that displays in front of and deactivates all other page content.

Use it to focus your users attention on a specific piece of information or a
specific action.
"""
import param

from ..reactive import ReactiveHTML
from .base import NamedListLike

# See https://a11y-dialog.netlify.app/
JS_FILE = "https://cdn.jsdelivr.net/npm/a11y-dialog@8/dist/a11y-dialog.min.js"

STYLE = """
.dialog-container,
.dialog-overlay {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
.dialog-container {
  z-index: 100002;
  display: flex;
}
.dialog-container[aria-hidden='true'] {
  display: none;
}
.dialog-overlay {
  z-index: 100001;
  background-color: rgb(43 46 56 / 0.9);
}
.dialog-content {
  margin: auto;
  z-index: 100002;
  position: relative;
  background-color: white;
  border-radius: 2px;
  padding: 10px;
  padding-bottom: 20px;
}
fast-design-system-provider .dialog-content {
  background-color: var(--background-color);
  border-radius:  calc(var(--corner-radius) * 1px);
}
@keyframes fade-in {
  from {
    opacity: 0;
  }
}
@keyframes slide-up {
  from {
    transform: translateY(10%);
  }
}
.dialog-overlay {
  animation: fade-in 200ms both;
}
.dialog-content {
  animation: fade-in 400ms 200ms both, slide-up 400ms 200ms both;
}
@media (prefers-reduced-motion: reduce) {
  .dialog-overlay,
  .dialog-content {
    animation: none;
  }
}
.pnx-dialog-close {
  position: absolute;
  top: 0.5em;
  right: 0.5em;
  border: 0;
  padding: 0.25em;
  background-color: transparent;
  font-size: 1.5em;
  width: 1.5em;
  height: 1.5em;
  text-align: center;
  cursor: pointer;
  transition: 0.15s;
  border-radius: 50%;
  z-index: 10003;
}
fast-design-system-provider .pnx-dialog-close {
  color:  var(--neutral-foreground-rest);
}
.pnx-dialog-close:hover {
  background-color: rgb(50 50 0 / 0.15);;
}
fast-design-system-provider .pnx-dialog-close:hover {
  background-color: var(--neutral-fill-hover);
}
.lm-Widget.p-Widget.lm-TabBar.p-TabBar.lm-DockPanel-tabBar.jp-Activity {
  z-index: -1;
}
"""

class Modal(ReactiveHTML, NamedListLike):  # pylint: disable=too-many-ancestors
    """The `Modal` layout is a *pop up*, element that displays in front of and deactivates
    all other page content.

    Use it to focus your users attention on a specific piece of information or a
    specific action.

    You will need to include the `Modal` in a layout or your template. It will not be
    shown before you trigger the `open` event or equivalently set `is_open=True`.

    Args:
        *objects: The objects to display in the modal.

    Reference: https://panel.holoviz.org/reference/layouts/Modal.html

    Example:

    >>> import panel as pn
    >>> from panel import Modal
    >>> pn.extension("modal")
    >>> modal = Modal(pn.panel("Hi. I am the Panel Modal!", width=200))
    >>> pn.Column(modal.param.open, modal).servable()
    """
    show_close_button = param.Boolean(True, doc="Whether to show a close button in the modal")

    is_open = param.Boolean(doc="""
        Whether or not the modal is open. Set to True to open. Set to False to close.""")
    open = param.Event(doc="Click here to open the modal")
    close = param.Event(doc="Click here to close the modal")

    def __init__(self, *objects, **params):  # pylint: disable=redefined-builtin
        params["sizing_mode"]="fixed"
        params["height"] = params["width"] = params["margin"] = 0
        NamedListLike.__init__(self, *objects, **params)
        ReactiveHTML.__init__(self, objects=self.objects, **params)

    @param.depends("open", watch=True)
    def _show(self):
        self.is_open = True

    @param.depends("close", watch=True)
    def _hide(self):
        self.is_open = False

    _extension_name = "modal"

    __javascript__ = [JS_FILE]


    _template = """
<style id="pnx_dialog_style">""" + STYLE + """</style>
<div id="pnx_dialog" class="dialog-container bk-root" aria-hidden="true">
<div id="pnx_overlay" class="dialog-overlay" data-a11y-dialog-hide></div>
  <div id="pnx_dialog_content" class="dialog-content" role="document">
    <button id="pnx_dialog_close" data-a11y-dialog-hide class="pnx-dialog-close" aria-label="Close this dialog window">
      <svg class="svg-icon" viewBox="0 0 20 20">
        <path
          fill="currentcolor"
          d="M15.898,4.045c-0.271-0.272-0.713-0.272-0.986,0l-4.71,4.711L5.493,4.045c-0.272-0.272-0.714-0.272-0.986,0s-0.272,0.714,0,0.986l4.709,4.711l-4.71,4.711c-0.272,0.271-0.272,0.713,0,0.986c0.136,0.136,0.314,0.203,0.492,0.203c0.179,0,0.357-0.067,0.493-0.203l4.711-4.711l4.71,4.711c0.137,0.136,0.314,0.203,0.494,0.203c0.178,0,0.355-0.067,0.492-0.203c0.273-0.273,0.273-0.715,0-0.986l-4.711-4.711l4.711-4.711C16.172,4.759,16.172,4.317,15.898,4.045z"
        ></path>
      </svg>
    </button>
    {% for object in objects %}
      <div id="pnx_modal_object">${object}</div>
    {% endfor %}
  </div>
</div>
"""

    _scripts = {
        "render": """
        fast_el = document.getElementById("body-design-provider")
        if (fast_el!==null){
          fast_el.appendChild(pnx_dialog_style)
          fast_el.appendChild(pnx_dialog)
        }
        self.show_close_button()
        self.init_modal()
        """,
        "init_modal": """
state.modal = new A11yDialog(pnx_dialog)
state.modal.on('show', function (element, event) {data.is_open=true})
state.modal.on('hide', function (element, event) {data.is_open=false})
if (data.is_open==true){state.modal.show()}
""",
        "is_open": """\
if (data.is_open==true){state.modal.show();view.invalidate_layout()} else {state.modal.hide()}""",
        "show_close_button": """
if (data.show_close_button){pnx_dialog_close.style.display = " block"}else{pnx_dialog_close.style.display = "none"}
""",
    }
