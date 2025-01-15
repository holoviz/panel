from panel.pane import LaTeX


def test_latex_pane(document, comm):
    # Renderer is needed as if we run test randomly we can get mathjax pane
    pane = LaTeX(r"$\frac{p^3}{q}$", renderer='katex')

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'KaTeX'
    assert model.text == r"$\frac{p^3}{q}$"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_latex_mathjax_pane(document, comm):
    pane = LaTeX(r"$\frac{p^3}{q}$", renderer='mathjax')

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'MathJax'
    # assert model.text == r"$\frac{p^3}{q}$"
    assert model.text == r"$$\frac{p^3}{q}$$"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
