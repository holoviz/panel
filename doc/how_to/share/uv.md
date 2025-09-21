# How to Share Panel Scripts with uv

**Transform your Panel applications into portable, shareable scripts that anyone can run** with a single command using [uv](https://docs.astral.sh/uv/guides/scripts/).

This approach eliminates dependency management headaches and makes your Panel apps accessible to colleagues, collaborators, and the broader community.

## What You'll Accomplish

By the end of this guide, you'll have:
- Created a self-contained Panel script with embedded dependencies
- Configured the script for both local development and sharing
- Published your script for others to run directly from GitHub
- Learned best practices for portable Panel application distribution

## Prerequisites

- **uv installed**: Install from [astral.sh/uv](https://docs.astral.sh/uv/)
- **Basic Panel knowledge**: Familiarity with creating Panel applications
- **Git/GitHub account**: For sharing your scripts publicly

## Step 1: Create a Self-Contained Panel Script

Create a new file called `script.py` with a complete Panel application:

```python
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
    app.show(port=5007)
```

**Why this structure works:**

- The dual-mode execution allows flexible running with either `python script.py` or `panel serve script.py`
- Clear component organization makes the code maintainable
- Descriptive names and comments aid understanding

## Step 2: Add Dependency Metadata

Configure your script's Python version and dependencies using uv's [inline metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata) feature:

```bash
uv add --script script.py --python ">=3.9" panel
```

This command automatically adds a metadata block to your script:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "panel",
# ]
# ///
```

**Pro tip:** Add additional dependencies as needed:

```bash
uv add --script script.py pandas matplotlib numpy
```

## Step 3: Test Locally

Verify your script works in an isolated environment:

```bash
# Run as a standalone application
uv run script.py

# Or serve with Panel's development server
uv run --with panel -- panel serve script.py --dev --show
```

The `--dev` flag enables auto-reload during development, and `--show` automatically opens your browser.

## Step 4: Publish to GitHub

Make your script accessible to others by publishing it:

1. **Create a repository** or use an existing one
2. **Commit your script**:
   ```bash
   git add script.py
   git commit -m "Add shareable Panel star rating app"
   git push origin main
   ```
3. **Get the raw file URL** from GitHub (click "Raw" button on the file page)

## Step 5: Share and Run from Anywhere

Others can now run your script directly from GitHub:

```bash
# Run the script directly from GitHub
uv run https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/script.py

# Or serve it with Panel
uv run --with panel -- panel serve https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/script.py --show
```

For example try:

```bash
# Run the script directly from GitHub
uv run https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/script.py

# Or serve it with Panel
uv run --with panel -- panel serve https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/script.py --show
```

## Advanced Sharing Patterns

### GitHub Gists

For quick sharing without a full repository create a [gist](https://gist.github.com/) and run it directly:

```bash
uv run https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/script.py
```

Your Panel applications are now portable, shareable, and ready for collaboration!

For more tips and tricks, check out the [uv | Running Scripts](https://docs.astral.sh/uv/guides/scripts/) guide.
