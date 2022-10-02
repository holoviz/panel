from models import Provider

DEFAULT_FAQ = """
# Frequently Asked Questions

## How do I add more files to a project?

You cannot do this as that would complicate this free and personal project.

What you can do is 

- Package your python code into a python package that you share on pypi and add it to the
`requirements`
- Store your other files somewhere public. For example on Github.

## What are the most useful resources for Panel data apps?

- [Panel](https://holoviz.panel.org) | [WebAssembly User Guide](https://pyviz-dev.github.io/panel/user_guide/Running_in_Webassembly.html) | [Community Forum](https://discourse.holoviz.org/) | [Github Code](https://github.com/holoviz/panel) | [Github Issues](https://github.com/holoviz/panel/issues) | [Twitter](https://mobile.twitter.com/panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)
- [Awesome Panel](https://awesome-panel.org) | [Github Code](https://github.com/marcskovmadsen/awesome-panel) | [Github Issues](https://github.com/MarcSkovMadsen/awesome-panel/issues)
- Marc Skov Madsen | [Twitter](https://twitter.com/MarcSkovMadsen) | [LinkedIn](https://www.linkedin.com/in/marcskovmadsen/)
- Sophia Yang | [Twitter](https://twitter.com/sophiamyang) | [Medium](https://sophiamyang.medium.com/)
- [Pyodide](https://pyodide.org) | [FAQ](https://pyodide.org/en/stable/usage/faq.html)
- [PyScript](https://pyscript.net/) | [FAQ](https://docs.pyscript.net/latest/reference/faq.html)

"""

DEFAULT_ABOUT = """
# About

The purpose of this project is to make it easy for you, me and the rest of the Panel community to
share Panel apps.

By using this project you consent to making your project publicly available and
[MIT licensed](https://opensource.org/licenses/MIT).

On the other hand I cannot guarentee the persisting of your project. Use at your own risk.

This project was made with Panel! Check out the code on
[Github](https://github.com/marcskovmadsen/awesome-panel).

If you are interested in getting your own version of Awesome Panel Sharing contact me via [LinkedIn](https://www.linkedin.com/in/marcskovmadsen).
"""

provider = Provider(
    site="Awesome Panel", title = "Sharing", faq=DEFAULT_FAQ, about=DEFAULT_ABOUT
)