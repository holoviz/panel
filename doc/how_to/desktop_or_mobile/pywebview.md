# Create Desktop Apps with pywebview

This guide demonstrates how to convert a Panel application into a standalone desktop application using [pywebview](https://pywebview.flowrl.com/) and [PyInstaller](https://pyinstaller.org/).

---

## Overview

pywebview is a lightweight cross-platform wrapper around a webview component that allows you to display HTML content in a native GUI window. Combined with PyInstaller, you can package your Panel application as a standalone executable that users can run without installing Python.

**What you'll learn:**
- How to wrap a Panel app with pywebview
- How to package the application with PyInstaller
- How to create a distributable executable

## Prerequisites

- Python 3.8 or later
- Basic familiarity with Panel applications
- Understanding of your target platform (Windows, macOS, or Linux)

## Installation

Install the required packages:

```bash
pip install panel pywebview pyinstaller
```

:::{note}
On Linux, you may need to install additional GTK dependencies. See the [pywebview documentation](https://pywebview.flowrl.com/guide/installation.html) for platform-specific requirements.
:::

## Creating a Desktop Application

### Step 1: Create Your Panel Application

First, create a Panel application that you want to convert. Here's a simple example:

```python
import panel as pn

pn.extension()

def create_app():
    """Create a simple Panel application."""
    slider = pn.widgets.IntSlider(name='Value', start=0, end=100, value=50)
    
    def update_text(value):
        return f"The slider value is: {value}"
    
    text = pn.bind(update_text, slider.param.value)
    
    button = pn.widgets.Button(name='Close Application', button_type='danger')
    
    app = pn.Column(
        "# Desktop Panel Application",
        "This is a Panel app running in a native window!",
        slider,
        text,
        button,
    )
    
    return app, button

if __name__ == "__main__":
    app, button = create_app()
    pn.serve(app, port=5000, show=True)
```

### Step 2: Wrap with pywebview

Create a file called `app.py` that wraps your Panel application with pywebview:

```python
import threading
import webview
import panel as pn

pn.extension()

def create_app():
    """Create your Panel application."""
    slider = pn.widgets.IntSlider(name='Value', start=0, end=100, value=50)
    
    def update_text(value):
        return f"The slider value is: {value}"
    
    text = pn.bind(update_text, slider.param.value)
    
    button = pn.widgets.Button(name='Close Application', button_type='danger')
    
    # Close the window when button is clicked
    def close_window(event):
        window.destroy()
    
    button.on_click(close_window)
    
    app = pn.Column(
        "# Desktop Panel Application",
        "This is a Panel app running in a native window!",
        slider,
        text,
        button,
    )
    
    return app

def start_server():
    """Start the Panel server in a background thread."""
    app = create_app()
    pn.serve(app, port=5000, show=False, threaded=True)

if __name__ == '__main__':
    # Start Panel server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    import time
    time.sleep(2)
    
    # Create and show the native window
    window = webview.create_window(
        'Panel Desktop App',
        'http://localhost:5000',
        width=800,
        height=600,
    )
    webview.start()
```

### Step 3: Test the Application

Run your application to ensure it works correctly:

```bash
python app.py
```

You should see a native window open with your Panel application running inside. Test all functionality before proceeding to packaging.

## Packaging with PyInstaller

### Step 1: Create a Spec File (Optional)

For more control over the packaging process, create a PyInstaller spec file:

```python
# app.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['panel', 'bokeh', 'tornado'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PanelApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for a GUI-only app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### Step 2: Build the Executable

Build your application using PyInstaller:

**Using the basic command:**
```bash
pyinstaller app.py --onefile --windowed
```

**Or using the spec file:**
```bash
pyinstaller app.spec
```

**Command options explained:**
- `--onefile`: Package everything into a single executable
- `--windowed`: Don't show a console window (Windows/macOS)
- `--name`: Specify the name of the executable

### Step 3: Test the Executable

Find your executable in the `dist` folder:

- **Windows**: `dist/app.exe` or `dist/PanelApp.exe`
- **macOS**: `dist/app` or `dist/PanelApp`
- **Linux**: `dist/app` or `dist/PanelApp`

Run the executable to verify it works correctly.

## Advanced Features

### Adding Application Icons

Add a custom icon to your application:

```bash
pyinstaller app.py --onefile --windowed --icon=app_icon.ico
```

Icon format requirements:
- **Windows**: `.ico` file
- **macOS**: `.icns` file  
- **Linux**: `.png` file

### Customizing the Window

You can customize the pywebview window with additional options:

```python
window = webview.create_window(
    'Panel Desktop App',
    'http://localhost:5000',
    width=1024,
    height=768,
    resizable=True,
    fullscreen=False,
    min_size=(800, 600),
    background_color='#FFFFFF',
    text_select=True,
)
```

### Handling Application Lifecycle

Properly handle application startup and shutdown:

```python
import atexit
import threading
import webview
import panel as pn

pn.extension()

# Store server reference globally
server = None

def start_server():
    """Start the Panel server."""
    global server
    app = create_app()
    server = pn.serve(app, port=5000, show=False, threaded=True)

def cleanup():
    """Clean up resources on exit."""
    global server
    if server is not None:
        server.stop()

# Register cleanup function
atexit.register(cleanup)

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    import time
    time.sleep(2)
    
    window = webview.create_window('Panel Desktop App', 'http://localhost:5000')
    webview.start()
```

## Troubleshooting

### Application Won't Start

**Issue**: The executable starts but shows a blank window or error.

**Solutions**:
- Verify all dependencies are included in the PyInstaller build
- Add hidden imports: `--hidden-import=panel --hidden-import=bokeh`
- Check the console output by removing the `--windowed` flag
- Increase the sleep time before creating the window

### Large Executable Size

**Issue**: The executable is very large (>100MB).

**Solutions**:
- Use `--exclude-module` to remove unnecessary packages
- Consider creating a directory-based distribution instead of `--onefile`
- Use UPX compression: `--upx-dir=/path/to/upx`

### Port Already in Use

**Issue**: Error message about port 5000 already in use.

**Solutions**:
- Use a different port or dynamically select an available port:

```python
import socket

def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

# Use in your code
port = find_free_port()
server = pn.serve(app, port=port, show=False, threaded=True)
window = webview.create_window('Panel Desktop App', f'http://localhost:{port}')
```

## Platform-Specific Considerations

### Windows

- Use `.ico` format for icons
- Consider code signing for distribution
- Test on target Windows versions

### macOS

- Use `.icns` format for icons
- May need to sign and notarize for distribution
- Test on both Intel and Apple Silicon if targeting both

### Linux

- Different distributions may require different dependencies
- GTK3 is commonly required for pywebview
- Consider using AppImage or Flatpak for broader distribution

## Distribution

### Windows

1. Test the `.exe` on a clean Windows machine
2. Consider creating an installer with tools like [NSIS](https://nsis.sourceforge.io/) or [Inno Setup](https://jrsoftware.org/isinfo.php)
3. Sign the executable for professional distribution

### macOS

1. Test the application on a clean macOS system
2. Create a `.dmg` installer
3. Sign and notarize for Gatekeeper compatibility

### Linux

1. Test on multiple distributions
2. Consider AppImage, Flatpak, or Snap for distribution
3. Provide installation instructions for dependencies

## Related Resources

- [pywebview Documentation](https://pywebview.flowrl.com/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Panel Server Configuration](../server/index)
