"""
Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.

For now I've just experimented a bit.

There is a simple implementation of an app using PyDeck in the gallery at
[awesome-streamlit.org](https://awesome-streamlit.org).

See

- [pydeck implementation](https://github.com/MarcSkovMadsen/awesome-panel/blob/master/package/awesome_panel/express/pane/pydeck.py)
- [test_pydeck app](https://github.com/MarcSkovMadsen/awesome-panel/blob/master/src/pages/gallery/awesome_panel_express_tests/test_pydeck.py)
- [test_pydeck test](https://github.com/MarcSkovMadsen/awesome-panel/blob/master/package/tests/test_pydeck.py)

It's based on the following resources

- [PyDeck Github](https://github.com/uber/deck.gl/tree/master/bindings/pydeck)
- [PyDeck Docs](https://deckgl.readthedocs.io/en/latest/)
- [PyDeck Deck Implementation](https://github.com/uber/deck.gl/blob/master/bindings/pydeck/pydeck/bindings/deck.py)
- [PyDeck render_json_to_html Implementation](https://github.com/uber/deck.gl/blob/master/bindings/pydeck/pydeck/io/html.py)

When I move on I believe I can find inspiration in

- The Panel implementation of the Plotly Pane and Plotly Bokeh Model
- [Extending Bokeh](https://docs.bokeh.org/en/latest/docs/user_guide/extensions.html)
- [PyDeck Jupyter Implementation](https://github.com/uber/deck.gl/blob/master/bindings/pydeck/pydeck/widget/widget.py)

There is a feature request for this at [Github 957](https://github.com/holoviz/panel/issues/957)
"""