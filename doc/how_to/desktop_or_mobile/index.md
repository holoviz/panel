# Convert to Desktop or Mobile App

Panel applications typically run in a web browser, backed by a Python server. However, you can also package Panel applications as standalone desktop or mobile applications using various frameworks. This allows you to distribute your application as a native executable that users can run without installing Python or managing dependencies.

This guide explores two popular approaches for creating desktop and mobile applications with Panel:

- **pywebview + PyInstaller**: A lightweight solution for creating desktop applications with a native window wrapper
- **Toga + Briefcase**: A comprehensive cross-platform solution for creating desktop and mobile applications

Both approaches embed a web server within the application and display your Panel app in a native window or webview.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1 sd-animate-grow50` pywebview + PyInstaller
:link: pywebview
:link-type: doc

Create lightweight desktop applications using pywebview and package them with PyInstaller.
:::

:::{grid-item-card} {octicon}`device-mobile;2.5em;sd-mr-1 sd-animate-grow50` Toga + Briefcase
:link: toga
:link-type: doc

Create cross-platform desktop and mobile applications using Toga and Briefcase.
:::

::::

## Choosing the Right Approach

### pywebview + PyInstaller

**Best for:**
- Desktop-only applications (Windows, macOS, Linux)
- Quick prototypes and simple applications
- Minimal dependencies and smaller application size
- Applications that need native window features

**Pros:**
- Lightweight and fast
- Simple to set up and use
- Native window controls and menus
- Good performance

**Cons:**
- Desktop only (no mobile support)
- Limited native UI components
- Manual packaging process with PyInstaller

### Toga + Briefcase

**Best for:**
- Cross-platform applications (desktop and mobile)
- Applications that need native UI components
- Professional distribution and packaging
- Long-term maintained applications

**Pros:**
- True cross-platform support (Windows, macOS, Linux, iOS, Android)
- Native UI integration
- Comprehensive packaging and distribution tools
- Active development and community

**Cons:**
- Larger application size
- More complex setup
- Additional dependencies

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

pywebview
toga
```
