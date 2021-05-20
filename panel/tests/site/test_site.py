import pathlib

from panel.site import Application, User, _BaseModel

ROOT = pathlib.Path(__file__).parent
SITE_YAML = ROOT.parent.parent.parent/"examples"/"site.yaml"

def test_base_model():
    model = _BaseModel()
    # Then
    assert model.uid
    assert isinstance(model.tags, list)
    assert isinstance(model.resources, dict)

def test_base_model_with_arguments():
    # Given
    uid = "uid"
    name="model"
    area = ["Apps"]
    tags = ["holoviz", "panel"]
    resources = {
        "github": "https://panel.holoviz.org"
    }
    # When
    model = _BaseModel(uid=uid, name=name, area=area, tags=tags, resources=resources)

    # Then
    assert model.uid == uid
    assert model.name == name
    assert model.area == area
    assert model.tags == tags
    assert model.resources == resources

    assert str(model) == "model"
    assert repr(model) == "_BaseModel(name='model')"

def test_can_create_user():
    # When
    user = User()
    # Then
    assert isinstance(user, _BaseModel)


def test_can_create_user_with_arguments():
    User(
        name = "Philipp Rudiger",
        url = "https://github.com/philippjfr",
        email = "na@hotmail.com",
        avatar = "https://avatars.githubusercontent.com/u/1550771",
        tags = ["pyviz", "developer"],
        resources = {"twitter": "https://twitter.com/PhilippJFR"}
    )

def test_can_create_application():
    application = Application()

    assert isinstance(application, _BaseModel)
    assert isinstance(application.author, User)
    assert isinstance(application.owner, User)

def test_can_create_application_author_and_owner_from_string():
    application = Application(
        author="Marc Skov Madsen",
        owner="Philipp Rudiger",
    )
    assert application.author.uid == "Marc Skov Madsen"
    assert application.author.name == "Marc Skov Madsen"
    assert application.owner.uid == "Philipp Rudiger"
    assert application.owner.name == "Philipp Rudiger"

    assert isinstance(application.author, User)
    assert isinstance(application.owner, User)

def test_can_create_application_with_arguments():
    # Given
    philipp = User(
        name = "Philipp Rudiger",
        url = "https://github.com/philippjfr",
        email = "na@hotmail.com",
        avatar = "https://avatars.githubusercontent.com/u/1550771",
        tags = ["pyviz", "developer"],
        resources = {"twitter": "https://twitter.com/PhilippJFR"},
    )
    # Application
    Application(
        name = "Panel",
        description = "The analytics app framework to rule them all",
        description_long = "Turns every dash into something lit "*10,
        author = philipp,
        owner = philipp,
        url = "https://panel.holoviz.org",
        thumbnail = "https://panel.holoviz.org/_static/logo_stacked.png",
        resources = {"github": "https://github.com/holoviz/panel"},
        tags = ["awesome", "analytics", "apps"],
    )

def test_can_read_example_site_yaml():
    applications = Application.read(SITE_YAML)
    assert applications
