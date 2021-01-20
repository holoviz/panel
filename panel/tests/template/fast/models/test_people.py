# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
from panel.template.fast.models import Person, Resource

from panel.tests.template.fast.models.conftest import create_person


def test_can_construct(person):
    assert isinstance(person, Person)
    assert person in Person.all
    assert Resource.all is not Person.all
    assert person._repr_html_()


if __name__.startswith("bokeh"):
    import panel as pn
    author = create_person()
    pn.panel(author, sizing_mode="stretch_both").servable()
