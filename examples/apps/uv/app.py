# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "panel",
# ]
# ///
import panel as pn

# Configure Panel with a modern design
pn.extension(design="material")

# Create interactive components
slider = pn.widgets.IntSlider(
    value=5,
    start=1,
    end=10,
    name="Rating"
)

def generate_stars(rating=5):
    """Convert numeric rating to star display."""
    return "⭐" * rating

# Build the application layout
app = pn.Column(
    "## ⭐ Star Rating Demo",
    "Adjust the slider to see your rating in stars:",
    slider,
    pn.bind(generate_stars, slider.param.value),
    sizing_mode="stretch_width",
    margin=(20, 40)
)

# Enable dual-mode execution
if pn.state.served:
    # Served mode: `panel serve script.py`
    app.servable(title="Star Rating App")
elif __name__ == "__main__":
    # Script mode: `python script.py`
    app.show(port=5007, autoreload=True)
