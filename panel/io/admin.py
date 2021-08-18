from ..models import terminal # noqa

from ..layout import Tabs
from ..template import FastListTemplate
from ..widgets import Terminal
from .server import set_curdoc
from .state import state


def admin_panel(doc):
    from pyinstrument.session import Session
    from pyinstrument.renderers import ConsoleRenderer
    r = ConsoleRenderer(color=True, unicode=True)
    session = state._sessions[0]
    for s in state._sessions[1:]:
        session = Session.combine(session, s)
    text = r.render(session)
    tabs = Tabs(
        ('Launch', Terminal(
            text,
            sizing_mode='stretch_both',
            margin=0,
            min_height=800
        )),
        margin=0,
        sizing_mode='stretch_both'
    )
    template = FastListTemplate(title='Panel Profiler', theme='dark')
    template.main.append(tabs)
    with set_curdoc(doc):
        template.server_doc(doc)
    return doc
