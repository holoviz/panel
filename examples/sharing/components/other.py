"""Provides an iframe component to embed another web page in your page"""

import panel as pn
import config
import param

def iframe_string(src: str)->str:
    """Returns an iframe string"""
    # pylint: disable=line-too-long
    return f"""<iframe frameborder="0" title="panel app" style="width: 100%;height:100%";flex-grow: 1" src="{src}" allow="accelerometer;autoplay;camera;document-domain;encrypted-media;fullscreen;gamepad;geolocation;gyroscope;layout-animations;legacy-image-formats;microphone;oversized-images;payment;publickey-credentials-get;speaker-selection;sync-xhr;unoptimized-images;unsized-media;screen-wake-lock;web-share;xr-spatial-tracking"></iframe>"""

def _iframe(src: str, sizing_mode="stretch_both", **params)->pn.pane.HTML:
    """Returns an iframe inside a HTML pane

    Use this to embed another web page inside your app.

    Args:
        src: The url of the web page to embed
        sizing_mode: Defaults to "stretch_both".

    Returns:
        An iframe inside a HTML pane
    """
    # pylint: disable=line-too-long
    return pn.pane.HTML(iframe_string(src=src), sizing_mode=sizing_mode, **params)

def iframe(src: param.String):
    pane = pn.bind(_iframe, src=src)
    # Todo: Figure out why all this wrapping is needed
    return pn.Column(pn.panel(pane, sizing_mode="stretch_both"), sizing_mode="stretch_both")

faq = pn.pane.Markdown(config.FAQ, name="FAQ", sizing_mode="stretch_both")
about= pn.pane.Markdown(config.ABOUT, name="ABOUT", sizing_mode="stretch_both")

