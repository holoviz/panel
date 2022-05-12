import panel as pn

from .sinewave import SineWave

def createApp2():
    sw = SineWave()
    return pn.Row(sw.param, sw.plot).servable()
