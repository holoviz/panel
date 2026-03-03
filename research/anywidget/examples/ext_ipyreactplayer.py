"""
IPyReactPlayer Example — Interactive Video Player in Panel
==========================================================

This example demonstrates using IPyReactPlayer's VideoPlayer (an anywidget
video player built on react-player) with Panel's AnyWidget pane.

The VideoPlayer supports YouTube, Vimeo, SoundCloud, and direct video URLs.
It exposes traits for playback control (playing, volume, muted, loop, etc.)
and current playback time, allowing full bidirectional sync with Panel.

GitHub: https://github.com/seidlr/ipyreactplayer
Docs:   https://github.com/seidlr/ipyreactplayer#readme

Key traitlets:
    - url (Unicode): Video URL (YouTube, Vimeo, direct)
    - playing (Bool): Whether video is currently playing
    - volume (Float): Volume level 0.0-1.0
    - muted (Bool): Whether audio is muted
    - loop (Bool): Loop playback
    - playbackRate (Float): Playback speed multiplier
    - time (Float): Current playback position in seconds
    - controls (Bool): Show native player controls
    - width/height (Unicode): Player dimensions as CSS strings

NOTE: `width` and `height` traits are CSS strings (e.g., "640px") which collide
with Panel's Layoutable integer params. They are renamed to `w_width` and
`w_height` on the component.

Required package:
    pip install ipyreactplayer

Run with:
    panel serve research/anywidget/examples/ext_ipyreactplayer.py
"""

from ipyreactplayer import VideoPlayer

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the VideoPlayer and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

# Using a Big Buck Bunny trailer (public domain, reliable CDN)
widget = VideoPlayer(
    url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    controls=True,
    width="640px",
    height="360px",
)
anywidget_pane = pn.pane.AnyWidget(widget, height=400, width=660)

component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

# Video URL selector
url_select = pn.widgets.Select(
    name="Video URL",
    options={
        "Big Buck Bunny (YouTube)": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
        "Sintel (YouTube)": "https://www.youtube.com/watch?v=eRsGyueVLvQ",
        "Direct MP4 (sample)": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
    },
    width=400,
)

# Playback controls
playing_toggle = pn.widgets.Toggle(name="Playing", value=False, width=100)
muted_toggle = pn.widgets.Toggle(name="Muted", value=False, width=100)
loop_toggle = pn.widgets.Toggle(name="Loop", value=False, width=100)
controls_toggle = pn.widgets.Toggle(name="Show Controls", value=True, width=120)

volume_slider = pn.widgets.FloatSlider(
    name="Volume", start=0.0, end=1.0, step=0.05, value=1.0, width=250
)
rate_slider = pn.widgets.FloatSlider(
    name="Playback Rate", start=0.25, end=4.0, step=0.25, value=1.0, width=250
)

# Panel -> Widget sync
url_select.param.watch(lambda e: setattr(component, "url", e.new), "value")
playing_toggle.param.watch(lambda e: setattr(component, "playing", e.new), "value")
muted_toggle.param.watch(lambda e: setattr(component, "muted", e.new), "value")
loop_toggle.param.watch(lambda e: setattr(component, "loop", e.new), "value")
controls_toggle.param.watch(lambda e: setattr(component, "controls", e.new), "value")
volume_slider.param.watch(lambda e: setattr(component, "volume", e.new), "value")
rate_slider.param.watch(lambda e: setattr(component, "playbackRate", e.new), "value")

# Widget -> Panel sync
def on_component_change(*events):
    for event in events:
        if event.name == "playing":
            playing_toggle.value = event.new
        elif event.name == "muted":
            muted_toggle.value = event.new
        elif event.name == "loop":
            loop_toggle.value = event.new
        elif event.name == "controls":
            controls_toggle.value = event.new
        elif event.name == "volume":
            volume_slider.value = event.new
        elif event.name == "playbackRate":
            rate_slider.value = event.new

component.param.watch(
    on_component_change,
    ["playing", "muted", "loop", "controls", "volume", "playbackRate"],
)

# Live trait display
trait_display = pn.pane.Markdown(
    pn.bind(
        lambda playing, muted, loop, vol, rate, time, url: (
            f"**Trait Values:**\n\n"
            f"- `playing`: {playing}\n"
            f"- `muted`: {muted}\n"
            f"- `loop`: {loop}\n"
            f"- `volume`: {vol:.2f}\n"
            f"- `playbackRate`: {rate:.1f}\n"
            f"- `time`: {time:.1f}s\n"
            f"- `url`: {url}\n"
        ),
        component.param.playing,
        component.param.muted,
        component.param.loop,
        component.param.volume,
        component.param.playbackRate,
        component.param.time,
        component.param.url,
    ),
    width=350,
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Upstream ESM incompatibility.</strong> ipyreactplayer's ESM has two issues:
(1) It uses <code>import React from "react"</code> (bare specifier) which requires
React in the import map — Panel's AnyWidget pane does not provide React by default.
(2) It exports a React component (<code>export default App</code>) instead of an
anywidget <code>render({model, el})</code> function. The upstream package would need
to either bundle React or use <code>@anywidget/react</code> with a CDN import.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# IPyReactPlayer -- Interactive Video Player in Panel

**ipyreactplayer** wraps [react-player](https://github.com/cookpete/react-player)
as an anywidget, supporting YouTube, Vimeo, SoundCloud, and direct video URLs.

## How to Test

### Video Playback
1. Click **Playing** toggle -- video should start/stop
2. The `time` trait in the sidebar should update as the video plays

### Controls
3. Toggle **Muted** -- audio should mute/unmute
4. Toggle **Loop** -- video should loop when it ends
5. Drag **Volume** slider -- volume should change
6. Drag **Playback Rate** slider -- playback speed should change

### Video Selection
7. Change the **Video URL** dropdown -- the player should load a new video

### Bidirectional Sync
8. If you click play/pause on the VIDEO PLAYER controls, the **Playing**
   toggle in the sidebar should update to match

## Trait Name Collisions

`width` and `height` traits (CSS strings like "640px") collide with Panel's
Layoutable integer params. They are renamed to `w_width` and `w_height`.
""", sizing_mode="stretch_width")

controls_panel = pn.Column(
    pn.pane.Markdown("### Playback Controls"),
    pn.Row(playing_toggle, muted_toggle, loop_toggle, controls_toggle),
    volume_slider,
    rate_slider,
    pn.pane.Markdown("### Video Selection"),
    url_select,
    pn.pane.Markdown("### Live Trait Values"),
    trait_display,
    width=420,
)

pn.Column(
    status,
    header,
    pn.Row(
        anywidget_pane,
        controls_panel,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
