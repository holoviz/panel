"""Grid layout using Split.js with vertical splits."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent
from panel.layout.base import ListLike

CSS = """
.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}
.gutter.gutter-vertical {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAFAQMAAABo7865AAAABlBMVEVHcEzMzMzyAv2sAAAAAXRSTlMAQObYZgAAABBJREFUeF5jOAMEEAIEEFwAn3kMwcB6I2AAAAAASUVORK5CYII=');
    cursor: row-resize;
}
"""

class GridAnyWidget(ListLike, AnyWidgetComponent):
    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    function render({ model, el}) {
      const objects = model.get_child("objects")

      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';
      splitDiv.style.height = `calc(100% - ${(objects.length - 1) * 10}px)`;

      let splits = [];

      objects.forEach((object, index) => {
        const split = document.createElement('div');
        splits.push(split)

        splitDiv.appendChild(split);
        split.appendChild(object);
      })

      Split(splits, {direction: 'vertical'})

      el.appendChild(splitDiv);
    }
    export default {render}
    """

    _stylesheets = [CSS]

component = GridAnyWidget(
    pn.pane.Markdown("## Section 1\n\nTop content."),
    pn.pane.Markdown("## Section 2\n\nMiddle content."),
    pn.pane.Markdown("## Section 3\n\nBottom content."),
    styles={"border": "2px solid lightgray"},
    height=400,
    width=400,
    sizing_mode="fixed",
)
