import panel as pn

pn.extension(sizing_mode="stretch_width")


def show(page):
    main.objects = [pages[page]]


# Create contents
pages = {
    "Page 1": pn.Column("# Page 1", "...bla bla bla"),
    "Page 2": pn.Column("# Page 2", "...more bla"),
}
page = pn.widgets.Select(options=list(pages.keys()), name="Page")

# Layout widgets
sidebar = pn.Column(page)
main = pn.Column()
template = pn.template.FastListTemplate(
    title="As Single Page App",
    sidebar=[sidebar],
    main=[main],
)

# Add interactivity
pn.bind(show, page, watch=True)
page.param.trigger("value")
pn.state.location.sync(page, {"value": "page"})

# Serve app
template.servable()
