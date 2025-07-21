# Configuring WebSocket Communication Settings

This guide provides comprehensive instructions for configuring bidirectional WebSocket communication in Panel/Bokeh/Tornado/Jupyter/Kubernetes environments to handle larger data transfers effectively.

Out of the box, you can reliably handle communication up to approximately 10 MB. This covers common use cases including visualizing tabular data and plots and uploading smaller files. But for example for audio and video use cases you may quickly run into issues.

## Overview

When building applications that handle significant data transfers (file uploads/ downloads, large visualizations, audio and video), the default WebSocket communication settings may become a bottleneck. Understanding and configuring these settings is crucial for production deployments.

## Understanding WebSocket Communication Flow

**The journey of data from client to server:**

1. **Browser processing** - Data is loaded into browser memory
2. **Message packaging** - The data is packaged into JSON messages. This might sometimes increase or decrease the size depending on the serialization method applied.
3. **WebSocket transmission** - Data travels through [WebSocket](https://en.wikipedia.org/wiki/WebSocket) connections via [Tornado](https://www.tornadoweb.org/en/stable/).
4. **Backend processing** - Your Python application receives and unpacks the JSON Messages.

## Technical Constraints and Default Limits

Understanding the various layers that impose size limitations helps you configure your environment appropriately:

| Component | Default Limit | Description |
|-----------|---------------|-------------|
| Browser | Several GB | Rarely the bottleneck |
| WebSocket Message Size | 20 MB | Tornado/Bokeh default setting |
| Buffer Size | 100 MB | Tornado default setting |
| Network/Infrastructure | Varies | Kubernetes, load balancers, proxies may impose additional limits |

## Configuration Guidelines

### Panel/Bokeh Server Deployments

For production applications using **`panel serve`**, configure larger limits at application startup:

...

For production applications using **`panel.serve()`**, configure larger limits at application startup:

```python
# production_app.py
import panel as pn

# Your application code here
app = ...

# Configure for larger uploads (150 MB example)
MAX_SIZE_MB = 150

pn.serve(
    app,
    websocket_max_message_size=MAX_SIZE_MB * 1024 * 1024,
    http_server_kwargs={'max_buffer_size': MAX_SIZE_MB * 1024 * 1024}
)
```

### Jupyter Environments

#### Jupyter Notebook Classic

1. Generate configuration file:
```bash
jupyter notebook --generate-config
```

2. Add to `jupyter_notebook_config.py`:
```python
# Configure WebSocket and buffer sizes (150 MB example)
MAX_SIZE_BYTES = 150 * 1024 * 1024

c.NotebookApp.tornado_settings = {
    "websocket_max_message_size": MAX_SIZE_BYTES
}
c.NotebookApp.max_buffer_size = MAX_SIZE_BYTES
```

#### JupyterLab

1. Generate configuration file:
```bash
jupyter lab --generate-config
```

2. Add to `jupyter_lab_config.py`:
```python
# Configure WebSocket and buffer sizes (150 MB example)
MAX_SIZE_BYTES = 150 * 1024 * 1024

c.ServerApp.tornado_settings = {
    'websocket_max_message_size': MAX_SIZE_BYTES
}
c.ServerApp.max_buffer_size = MAX_SIZE_BYTES
```

#### Best Practices & Considerations

**🎯 User Experience Tips:**

- Provide clear feedback about file upload and download size restrictions.

**⚠️ What happens when limits are exceeded:**

- Browser tabs may crash or become unresponsive
- WebSocket connections may close with error messages like `[bokeh] Lost websocket 0 connection, 1009 (message too big)`
- Applications require page refresh to restore functionality

**💡 Alternative approaches for large transfers:**

- Use file input components with chunked messaging like the [`FileDropper`](https://panel.holoviz.org/reference/widgets/FileDropper.html) to enable uploading large files
- Consider cloud storage integration for enterprise applications

## Conclusion

Proper WebSocket configuration is essential for applications handling significant data transfers. Start with conservative settings, monitor your application's behavior, and scale configuration as needed. Always consider security implications and user experience when increasing transfer limits.

For specific use cases or troubleshooting, consult the relevant documentation:
- [Panel Documentation](https://panel.holoviz.org/)
- [Bokeh Server Documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server.html)
- [Tornado Documentation](https://www.tornadoweb.org/en/stable/)
- [Jupyter Configuration](https://jupyter.readthedocs.io/en/latest/use/config.html)
- [Kubernetes](https://kubernetes.io/docs/home/)
