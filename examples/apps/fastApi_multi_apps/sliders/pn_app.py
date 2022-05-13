import panel as pn

from .sinewave import SineWave

def createApp():
    sw = SineWave()
    return pn.Row(sw.param, sw.plot).servable()
