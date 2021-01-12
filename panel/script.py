import panel as pn
from panel.reactive import ReactiveHTML
import param
pn.extension()

JME = """20 19 C 6.61 -7.11 C 7.82 -7.81 O 6.61 -5.71 O 5.40 -7.81 N 7.82 -9.21 C 9.03 -7.11 C 10.25 -7.81 C 11.46 -7.11 N 12.67 -7.81 O 11.46 -5.71 C 13.88 -7.11 C 15.10 -7.81 O 15.10 -9.21 N 16.31 -7.11 C 17.52 -7.81 C 18.73 -7.11 C 13.88 -5.71 O 19.94 -7.81 O 18.73 -5.71 S 15.09 -5.01 1 2 1 1 3 2 1 4 1 2 5 -2 2 6 1 6 7 1 7 8 1 8 9 1 8 10 2 9 11 1 11 12 1 12 13 2 12 14 1 14 15 1 15 16 1 11 17 -1 16 18 1 16 19 2 17 20 1"""

HTML = ""

class JSMEEditor(ReactiveHTML):

    jme = param.String(JME)

    _html = '<div id="div-${id}"></div>'

    _dom_events = {}

editor = JSMEEditor()
editor_settings = pn.Param(editor, parameters=["jme"])
pn.Row(editor_settings, editor)