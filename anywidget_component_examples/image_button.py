"""Image button widget with click tracking."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class ImageButton(AnyWidgetComponent):
    clicks = param.Integer(default=0)
    image = param.String()

    _esm = """
function render({ model, el }) {
    const button = document.createElement('button');
    button.id = 'button';
    button.className = 'pn-container center-content';

    const img = document.createElement('img');
    img.id = 'image';
    img.className = 'image-size';
    img.src = model.get("image");

    button.appendChild(img);

    button.addEventListener('click', () => {
        model.set("clicks", model.get("clicks")+1);
        model.save_changes();
    });
    el.appendChild(button);
}
export default { render }
"""

    _stylesheets = ["""
.pn-container {
    height: 100%;
    width: 100%;
}
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1em;
}
.image-size {
    width: 100%;
    max-height: 100%;
    object-fit: contain;
}
"""]

component = ImageButton(
    image="https://panel.holoviz.org/_static/logo_stacked.png",
    styles={"border": "2px solid lightgray"},
    width=400, height=200,
)
