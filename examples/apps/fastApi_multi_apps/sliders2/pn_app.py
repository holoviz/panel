import panel as pn

from .sinewave import SineWave

def createApp2(doc):
    sw = SineWave()
    row = pn.Row(sw.param, sw.plot)
    row.server_doc(doc)