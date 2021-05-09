from panel import param
import panel as pn

def template_with_sidebar(Template=pn.template.FastListTemplate, sidebar=True):
    button = pn.widgets.Button(name="Click Me")
    select = pn.widgets.Select(name="Select", value=1, options=[1,2,3,4,5])

    template = Template(
        site="Home",
        title="Sidebar Width Test",
        main=["Hello"]
        )
    if sidebar:
        template.sidebar[:]=[button, select, pn.Param(select)]
    return template

def template_without_sidebar(Template=pn.template.FastListTemplate):
    return Template(
        title="No Sidebar Width Test",
        main=["Hello"]
        )

apps = {
    "vanilla-template": template_with_sidebar(Template=pn.template.VanillaTemplate),
    "vanilla-template-no-sidebar": template_with_sidebar(Template=pn.template.VanillaTemplate, sidebar=False),
    "material-template": template_with_sidebar(Template=pn.template.MaterialTemplate),
    "material-template-no-sidebar": template_with_sidebar(Template=pn.template.MaterialTemplate, sidebar=False),
    "bootstrap-template": template_with_sidebar(Template=pn.template.BootstrapTemplate),
    "bootstrap-template-no-sidebar": template_with_sidebar(Template=pn.template.BootstrapTemplate, sidebar=False),
    "fast-list-template": template_with_sidebar(Template=pn.template.FastListTemplate),
    "fast-list-template-no-sidebar": template_with_sidebar(Template=pn.template.FastListTemplate, sidebar=False),
}

if __name__.startswith("bokeh"):
    template = "material"
    apps[template + "-template"].servable()
if __name__=="__main__":
    pn.serve(apps)