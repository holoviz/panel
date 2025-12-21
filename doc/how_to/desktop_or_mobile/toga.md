# Create Cross-Platform Apps with Toga

This guide demonstrates how to convert a Panel application into a cross-platform desktop and mobile application using [Toga](https://toga.readthedocs.io/) and [Briefcase](https://briefcase.readthedocs.io/).

---

## Overview

Toga is a Python native, OS native, cross-platform GUI toolkit. Combined with Briefcase, a tool for converting Python projects into standalone native applications, you can package your Panel application to run on Windows, macOS, Linux, iOS, and Android.

Unlike pywebview, Toga provides a native UI framework, allowing you to integrate native controls alongside your Panel web content.

**What you'll learn:**
- How to integrate Panel with Toga
- How to package applications with Briefcase
- How to create cross-platform distributions

## Prerequisites

- Python 3.8 or later
- Basic familiarity with Panel applications
- Understanding of your target platforms

## Installation

Install Briefcase, which will handle Toga and other dependencies:

```bash
pip install briefcase
```

:::{note}
Briefcase will automatically install Toga and other required dependencies when you create your project.
:::

## Creating a Cross-Platform Application

### Step 1: Initialize a Briefcase Project

Create a new directory for your project and initialize it with Briefcase:

```bash
mkdir my_panel_app
cd my_panel_app
briefcase new
```

Briefcase will prompt you for project details:
- **Formal Name**: "My Panel App"
- **App Name**: "mypanelapp"
- **Bundle Identifier**: "com.example.mypanelapp"
- **Project Name**: "My Panel App"
- **Description**: "A Panel app packaged with Toga"
- **Author**: Your name
- **Author's Email**: Your email
- **URL**: Your project URL
- **License**: Choose a license
- **GUI Framework**: Select "Toga"

### Step 2: Create Your Panel Application

Navigate to the source directory and modify the main application file. The structure will look like:

```
my_panel_app/
├── pyproject.toml
└── src/
    └── mypanelapp/
        ├── __init__.py
        ├── __main__.py
        └── app.py
```

Edit `src/mypanelapp/app.py` to integrate Panel with Toga:

```python
import asyncio
import pathlib

import toga
from toga.style import Pack

import panel as pn

pn.extension()


class MyPanelApp(toga.App):
    """A Toga application that hosts a Panel app."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = None
        self.port = 0
    
    def create_panel_app(self):
        """Create your Panel application."""
        slider = pn.widgets.IntSlider(
            name='Value', 
            start=0, 
            end=100, 
            value=50
        )
        
        def update_text(value):
            return f"## Slider Value: {value}"
        
        text = pn.bind(update_text, slider.param.value)
        
        app = pn.Column(
            "# Panel in Toga!",
            "This Panel app is running inside a Toga native application.",
            slider,
            text,
            pn.pane.Markdown(
                "You can deploy this to Windows, macOS, Linux, iOS, and Android!"
            ),
        )
        
        return app
    
    async def start_panel_server(self, widget, **kwargs):
        """Start the Panel server asynchronously."""
        app = self.create_panel_app()
        
        # Start Panel server on a random available port
        self.server = pn.serve(
            {'/': app},
            port=0,  # Use 0 to get a random available port
            show=False,
            start=True
        )
        
        # Get the actual port that was assigned
        self.port = self.server.port
        
        # Update the webview URL
        self.webview.url = f'http://localhost:{self.port}'
        self.status_label.text = f'Panel app running on port {self.port}'
    
    def startup(self):
        """Construct and show the Toga application."""
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # Create a status label
        self.status_label = toga.Label(
            'Starting Panel server...',
            style=Pack(padding=5)
        )
        
        # Create a webview to display the Panel app
        self.webview = toga.WebView(
            style=Pack(flex=1)
        )
        
        # Create a reload button
        reload_button = toga.Button(
            'Reload',
            on_press=self.reload_app,
            style=Pack(padding=5)
        )
        
        # Create the layout
        button_box = toga.Box(
            children=[reload_button, self.status_label],
            style=Pack(direction='row', padding=5)
        )
        
        main_box = toga.Box(
            children=[button_box, self.webview],
            style=Pack(direction='column', flex=1)
        )
        
        self.main_window.content = main_box
        
        # Start the Panel server in the background
        self.add_background_task(self.start_panel_server)
        
        # Show the main window
        self.main_window.show()
    
    def reload_app(self, widget):
        """Reload the Panel application."""
        if self.port:
            self.webview.url = f'http://localhost:{self.port}'
            self.status_label.text = 'App reloaded'


def main():
    """Entry point for the application."""
    return MyPanelApp('My Panel App', 'com.example.mypanelapp')


if __name__ == '__main__':
    main().main_loop()
```

### Step 3: Update Dependencies

Edit `pyproject.toml` to include Panel and its dependencies:

```toml
[tool.briefcase.app.mypanelapp]
requires = [
    "toga>=0.4.0",
    "panel>=1.0.0",
    "bokeh>=3.0.0",
]
```

### Step 4: Test in Development Mode

Test your application in development mode:

```bash
briefcase dev
```

This runs your application using your local Python environment, which is faster for testing and debugging.

## Building and Packaging

### Desktop Applications

#### Build for Your Platform

Build the application for your current platform:

```bash
briefcase build
```

This creates a native application bundle in the appropriate format for your OS.

#### Run the Built Application

Test the built application:

```bash
briefcase run
```

#### Package for Distribution

Create a distributable package:

```bash
briefcase package
```

This creates:
- **Windows**: An MSI installer
- **macOS**: A DMG file
- **Linux**: AppImage, DEB, or RPM packages

### Mobile Applications

#### iOS

Build for iOS (requires macOS):

```bash
briefcase create iOS
briefcase build iOS
briefcase run iOS
```

Package for App Store:

```bash
briefcase package iOS
```

:::{note}
Building for iOS requires Xcode and Apple Developer account for distribution.
:::

#### Android

Build for Android:

```bash
briefcase create android
briefcase build android
briefcase run android
```

Package for Google Play:

```bash
briefcase package android
```

:::{note}
Building for Android requires Android SDK. Briefcase will help you install it if needed.
:::

## Advanced Features

### Adding Native UI Controls

You can combine Toga's native controls with Panel's web-based UI:

```python
def startup(self):
    """Startup with mixed native and web UI."""
    self.main_window = toga.MainWindow(title=self.formal_name)
    
    # Native controls
    self.zoom_level = 1.0
    
    zoom_in_button = toga.Button(
        'Zoom In',
        on_press=self.zoom_in,
        style=Pack(padding=5)
    )
    
    zoom_out_button = toga.Button(
        'Zoom Out',
        on_press=self.zoom_out,
        style=Pack(padding=5)
    )
    
    # Status label
    self.status_label = toga.Label(
        'Starting Panel server...',
        style=Pack(padding=5, flex=1)
    )
    
    # WebView for Panel content
    self.webview = toga.WebView(style=Pack(flex=1))
    
    # Layout
    toolbar = toga.Box(
        children=[zoom_in_button, zoom_out_button, self.status_label],
        style=Pack(direction='row', padding=5)
    )
    
    main_box = toga.Box(
        children=[toolbar, self.webview],
        style=Pack(direction='column', flex=1)
    )
    
    self.main_window.content = main_box
    self.add_background_task(self.start_panel_server)
    self.main_window.show()

def zoom_in(self, widget):
    """Increase zoom level."""
    self.zoom_level += 0.1
    self.webview.evaluate_javascript(
        f"document.body.style.zoom = {self.zoom_level};"
    )

def zoom_out(self, widget):
    """Decrease zoom level."""
    self.zoom_level = max(0.5, self.zoom_level - 0.1)
    self.webview.evaluate_javascript(
        f"document.body.style.zoom = {self.zoom_level};"
    )
```

### Adding Menus

Create application menus using Toga:

```python
def startup(self):
    # ... existing code ...
    
    # Create menu commands
    self.commands.add(
        toga.Command(
            self.reload_app,
            text='Reload',
            tooltip='Reload the Panel app',
            group=toga.Group.VIEW
        )
    )
    
    self.commands.add(
        toga.Command(
            self.zoom_in,
            text='Zoom In',
            tooltip='Increase zoom level',
            group=toga.Group.VIEW
        )
    )
    
    self.commands.add(
        toga.Command(
            self.zoom_out,
            text='Zoom Out',
            tooltip='Decrease zoom level',
            group=toga.Group.VIEW
        )
    )
```

### Handling Application State

Save and restore application state:

```python
import json
from pathlib import Path

class MyPanelApp(toga.App):
    
    def startup(self):
        # ... existing code ...
        
        # Load saved state
        self.load_state()
    
    def load_state(self):
        """Load application state from file."""
        state_file = self.paths.data / 'app_state.json'
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.zoom_level = state.get('zoom_level', 1.0)
    
    def save_state(self):
        """Save application state to file."""
        state_file = self.paths.data / 'app_state.json'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'zoom_level': self.zoom_level,
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
    
    def on_exit(self):
        """Handle application exit."""
        self.save_state()
        if self.server:
            self.server.stop()
        return True
```

## Troubleshooting

### Server Doesn't Start

**Issue**: Panel server fails to start or the webview shows an error.

**Solutions**:
- Check that all Panel dependencies are listed in `pyproject.toml`
- Verify the port is available
- Increase the delay before setting the webview URL
- Check application logs with `briefcase run --log`

### Mobile Build Fails

**Issue**: Android or iOS build fails.

**Solutions**:
- Ensure you have the required SDKs installed
- Check Briefcase logs for specific errors
- Verify all dependencies are compatible with mobile platforms
- Some Panel features may not work on mobile; test thoroughly

### Large Application Size

**Issue**: The packaged application is very large.

**Solutions**:
- Remove unnecessary dependencies from `pyproject.toml`
- Use Briefcase's packaging options to optimize size
- Consider lazy-loading heavy dependencies

## Platform-Specific Considerations

### Windows

- Test on different Windows versions
- Consider code signing for distribution
- Use MSI installer for professional deployment

### macOS

- Test on both Intel and Apple Silicon
- Sign and notarize for Gatekeeper
- Use DMG for distribution

### Linux

- Test on multiple distributions
- Consider AppImage for universal compatibility
- Provide DEB/RPM packages for specific distributions

### iOS

- Requires Apple Developer account ($99/year)
- Must follow App Store guidelines
- Test on physical devices, not just simulators
- Some Python packages may not be available

### Android

- Google Play requires developer account ($25 one-time)
- Follow Google Play policies
- Test on multiple Android versions
- Some Python packages may not be available

## Distribution

### Code Signing

For professional distribution, sign your applications:

**macOS:**
```bash
briefcase package macOS --adhoc  # For testing
briefcase package macOS --identity "Developer ID"  # For distribution
```

**Windows:**
Use tools like SignTool to sign your MSI installer.

### App Store Submission

#### iOS App Store

1. Build the release package
2. Use Xcode to upload to App Store Connect
3. Follow Apple's review process

#### Google Play Store

1. Build the release APK/AAB
2. Upload to Google Play Console
3. Follow Google's review process

## Example: Complete Application

Here's a complete example combining multiple features:

```python
import asyncio
import json
from pathlib import Path

import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW

import panel as pn

pn.extension()


class PanelDesktopApp(toga.App):
    """A full-featured Panel desktop application."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = None
        self.port = 0
        self.zoom_level = 1.0
    
    def create_panel_app(self):
        """Create a feature-rich Panel application."""
        # Create widgets
        text_input = pn.widgets.TextInput(
            name='Enter text',
            placeholder='Type something...'
        )
        
        slider = pn.widgets.FloatSlider(
            name='Adjust value',
            start=0,
            end=10,
            value=5,
            step=0.1
        )
        
        select = pn.widgets.Select(
            name='Choose option',
            options=['Option 1', 'Option 2', 'Option 3']
        )
        
        # Create dynamic content
        @pn.depends(text_input.param.value, slider.param.value, select.param.value)
        def update_content(text, value, option):
            return pn.pane.Markdown(f"""
            ## Your Inputs
            
            - **Text**: {text or 'None'}
            - **Slider**: {value:.2f}
            - **Selection**: {option}
            
            This is a fully functional Panel app running in a native application!
            """)
        
        # Layout
        app = pn.Column(
            "# Panel Desktop Application",
            pn.pane.Markdown("""
            Welcome to your Panel desktop app! This application demonstrates:
            
            - ✅ Native window integration
            - ✅ Responsive Panel widgets  
            - ✅ Cross-platform compatibility
            - ✅ Professional packaging
            """),
            pn.layout.Divider(),
            text_input,
            slider,
            select,
            pn.layout.Divider(),
            update_content,
        )
        
        return app
    
    async def start_panel_server(self, widget=None, **kwargs):
        """Start Panel server."""
        app = self.create_panel_app()
        
        self.server = pn.serve(
            {'/': app},
            port=0,
            show=False,
            start=True
        )
        
        self.port = self.server.port
        self.webview.url = f'http://localhost:{self.port}'
        self.status_label.text = 'Ready'
    
    def startup(self):
        """Initialize the application."""
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # Create controls
        self.status_label = toga.Label(
            'Initializing...',
            style=Pack(padding=5, flex=1)
        )
        
        reload_button = toga.Button(
            'Reload',
            on_press=self.reload_app,
            style=Pack(padding=5)
        )
        
        zoom_in_button = toga.Button(
            'Zoom In',
            on_press=self.zoom_in,
            style=Pack(padding=5)
        )
        
        zoom_out_button = toga.Button(
            'Zoom Out',
            on_press=self.zoom_out,
            style=Pack(padding=5)
        )
        
        # Create webview
        self.webview = toga.WebView(style=Pack(flex=1))
        
        # Layout
        toolbar = toga.Box(
            children=[
                reload_button,
                zoom_in_button,
                zoom_out_button,
                self.status_label
            ],
            style=Pack(direction=ROW, padding=5)
        )
        
        main_box = toga.Box(
            children=[toolbar, self.webview],
            style=Pack(direction=COLUMN, flex=1)
        )
        
        self.main_window.content = main_box
        
        # Start Panel server
        self.add_background_task(self.start_panel_server)
        
        self.main_window.show()
    
    def reload_app(self, widget):
        """Reload the Panel app."""
        if self.port:
            self.webview.url = f'http://localhost:{self.port}'
    
    def zoom_in(self, widget):
        """Increase zoom."""
        self.zoom_level += 0.1
        self.webview.evaluate_javascript(
            f"document.body.style.zoom = {self.zoom_level};"
        )
    
    def zoom_out(self, widget):
        """Decrease zoom."""
        self.zoom_level = max(0.5, self.zoom_level - 0.1)
        self.webview.evaluate_javascript(
            f"document.body.style.zoom = {self.zoom_level};"
        )


def main():
    return PanelDesktopApp('Panel Desktop App', 'com.example.paneldesktop')


if __name__ == '__main__':
    main().main_loop()
```

## Related Resources

- [Toga Documentation](https://toga.readthedocs.io/)
- [Briefcase Documentation](https://briefcase.readthedocs.io/)
- [BeeWare Project](https://beeware.org/)
- [Panel Server Configuration](../server/index)
