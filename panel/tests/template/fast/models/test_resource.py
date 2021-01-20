# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
from panel.template.fast.models import Resource


def test_can_construct(resource):
    assert isinstance(resource, Resource)
    assert resource in Resource.all
    assert resource._repr_html_()
