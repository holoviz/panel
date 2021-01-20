# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
import pytest

from panel.template.fast.models import Resource, Person


def create_person():
    return Person(
        name="Marc Skov Madsen",
        url="https://datamodelsanalytics.com",
        avatar_url="https://avatars0.githubusercontent.com/u/42288570",
        twitter_url="https://twitter.com/MarcSkovMadsen",
        linkedin_url="https://www.linkedin.com/in/marcskovmadsen/",
        github_url="https://github.com/MarcSkovMadsen",
    )


def create_resource(person=None):
    if not person:
        person = create_person()
    return Resource(
        name="Awesome Panel",
        description="""A site about Panel. The purpose is to inspire and make it easier to create
        awesome analytics apps in Python and Panel.""",
        url="https://awesome-panel.org",
        thumbnail_url="",
        documentation_url="d",
        code_url="a",
        youtube_url="b",
        gif_url="c",
        author=person,
        owner=person,
        tags=["Site"],
        binder_url=(
            "https://mybinder.org/v2/gh/MarcSkovMadsen/awesome-panel-extensions/master"
            "?filepath=examples%2Freference%2Fmodels%2FIcon.ipynb"
        ),
    )


@pytest.fixture
def person():
    return create_person()


@pytest.fixture
def resource(person):
    return create_resource(person)
