from panel.pane import Ace

code = """
import math
x = 10
math.sin(x)**2 + math.cos(x)**2 == 1
"""


def test_ace_pane(document, comm):
    pane = Ace(code)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.code == code

    # Replace Pane.object
    pane.object = None
    assert pane._models[model.ref['id']][0] is model
    assert model.code == ''

    # Replace params
    pane.object = "test"
    pane.language = 'xml'
    pane.theme = 'monokai'

    assert pane._models[model.ref['id']][0] is model
    assert model.code == "test"
    assert model.language == "xml"
    assert model.theme == "monokai"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
