"""Split layout using Split.js CDN library."""
import panel as pn
from panel.custom import Child, AnyWidgetComponent

CSS = """
.split {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
}

.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}

.gutter.gutter-horizontal {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAeCAYAAADkftS9AAAAIklEQVQoU2M4c+bMfxAGAgYYmwGrIIiDjrELjpo5aiZeMwF+yNnOs5KSvgAAAABJRU5ErkJggg==');
    cursor: col-resize;
}
"""

class SplitAnyWidget(AnyWidgetComponent):
    left = Child()
    right = Child()

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    function render({ model, el }) {
      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';

      const split0 = document.createElement('div');
      splitDiv.appendChild(split0);

      const split1 = document.createElement('div');
      splitDiv.appendChild(split1);

      const split = Split([split0, split1])

      model.on('remove', () => split.destroy())

      split0.append(model.get_child("left"))
      split1.append(model.get_child("right"))

      el.appendChild(splitDiv)
    }

    export default {render}
    """

    _stylesheets = [CSS]

component = SplitAnyWidget(
    left=pn.pane.Markdown("## Left Panel\n\nContent here."),
    right=pn.pane.Markdown("## Right Panel\n\nContent here."),
    height=300,
    sizing_mode="stretch_width",
)
