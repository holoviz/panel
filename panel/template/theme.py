import param

from bokeh.themes import Theme


class Theme(param.Parameterized):
    """
    A Theme customizes the look and feel of a Template by providing
    custom CSS and bokeh Theme class.
   
    When adding a new theme a generic Theme class should be created,
    which is what users will important and set on the Template.theme
    parameter. Additionally a concrete implementation of the Theme
    should be created specific to the particular Template being used.

    For example when adding a DarkTheme there should be a
    corresponding MaterialDarkTheme which declares the Template class
    on its _template class variable. In this way a user can always use
    the generic Theme but the actual CSS and bokeh Theme will depend
    on the exact Template being used.
    """

    css = param.Filename()

    bokeh_theme = param.ClassSelector(class_=Theme)

    _template = None

    __abstract = True

    @classmethod
    def find_theme(cls, template_type):
        if cls._template is template_type:
            return cls
        for theme in param.concrete_descendents(cls).values():
            if theme._template is template_type:
                return theme


class DefaultTheme(Theme):
    """
    The DefaultTheme uses the standard Panel color palette.
    """
