"""Functionality to speed up developing tests of Panel apps"""
from panel.layout import Column
from panel.pane import Markdown


class TestApp(Column):
    """Creates a Test App from the name and docstring of the test function"""

    __test__ = False  # We don't wan't pytest to collect this

    def __init__(self, test_func, *args, **kwargs):
        """## Creates a Test App from the name and docstring of the test function

        Displays
        - __name__
        - __doc__

        Has sizing_mode="stretch_width" unless otherwise specified

        Arguments:
            test_func {Callable} -- The function to create an app from.
        """
        text_str = test_func.__name__.replace("_", " ",).capitalize()
        text_str = "# " + text_str

        if test_func.__doc__:
            text_str += "\n\n" + test_func.__doc__
        text = Markdown(text_str)

        if "sizing_mode" not in kwargs and "width" not in kwargs and "height" not in kwargs:
            kwargs["sizing_mode"] = "stretch_width"

        super().__init__(text, *args, **kwargs)
