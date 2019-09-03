import panel as pn

from .sinewave import SineWave

def app(doc):
    sw = SineWave()
    row = pn.Row(sw.param, sw.plot)
    row._get_root(doc)
