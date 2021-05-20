"""The site module contains definitions of models like User and Application."""
import uuid

import toml
import yaml

import param


def _get_nested_value(element, *keys):
    """Returns a nested value if it exists. Otherwise None

    If 'panel' is a key of element then we search from the value of 'panel'"""
    if not isinstance(element, dict):
        raise AttributeError("Expects dict as first argument.")
    if len(keys) == 0:
        raise AttributeError("Expects at least two arguments, one given.")

    if "panel" in element:
        element = element["panel"]

    if "config" in element:
        element = element["config"]

    for key in keys:
        try:
            element = element[key]
        except KeyError:
            return None
    return element


def _skip(item):
    """Returns True if the item is a dictionary with the key 'skip' and value True"""
    if not isinstance(item, dict):
        return False
    return item.get("skip", False)


class _BaseModel(param.Parameterized):
    """The BaseModel adds ordering by the name parameter to a Class"""

    uid = param.String(constant=True, doc="A unique id identifying the item.", precedence=1)
    name = param.String(default="New Model", doc="The name of the item", precedence=1)
    area = param.List(doc="The area can be used for navigation", precedence=1)
    tags = param.List(
        class_=str,
        precedence=3,
        doc="""A list of tags like 'machine-learning', 'panel', 'holoviews'.""",
    )
    resources = param.Dict(
        precedence=3,
        doc="""
        A dictionary of urls. For example 'github': 'https://panel.holoviz.org'""",
    )

    def __init__(self, **params):
        if "uid" not in params:
            params["uid"] = str(uuid.uuid4())
        if "resources" not in params:
            params["resources"] = {}

        super().__init__(**params)

    def __lt__(self, other):
        if hasattr(other, "name"):
            return self.name.casefold() < other.name.casefold()
        return True

    def __eq__(self, other):
        if hasattr(other, "uid"):
            return self.uid == other.uid
        return False

    def __str__(
        self,
    ):
        return self.name

    def __repr__(
        self,
    ):
        return f"{self.__class__.name}(name='{self.name}')"

    @classmethod
    def create_from_toml(cls, path, clean_func=None):
        """Returns a Dictionary of Models from the toml file specified by the path"""
        config = toml.load(path)
        if not clean_func:
            clean_func = lambda x: x
        return {key: cls(uid=key, **clean_func(value)) for key, value in config.items()}


class User(_BaseModel):
    """A Model of a User

    >>> from panel.site import User
    >>> User(
    ...     name = "Philipp Rudiger",
    ...     url = "https://github.com/philippjfr",
    ...     email = "na@hotmail.com",
    ...     avatar = "https://avatars.githubusercontent.com/u/1550771",
    ...     tags = ["pyviz", "developer"],
    ...     resources = {"twitter": "https://twitter.com/PhilippJFR"},
    ... )
    """

    name = param.String(default="New User", doc="The name of the user.", precedence=1)
    project = param.String(
        doc="""
    The name of associated project. Can be used for governance in a multi-project site""",
        precedence=1,
    )

    email = param.String(doc="The email of the user.", precedence=1)
    url = param.String(doc="An url pointing to a page about the user.", precedence=1)

    avatar = param.String(doc="The url of an avatar image of the user.", precedence=2)

    @staticmethod
    def _get_users(config):
        """Returns a list of Users from the specificed list of dicts"""
        if not config:
            return []

        users = _get_nested_value(config, "users")
        if not users:
            return []

        return [User(**user) for user in users if not _skip(user)]


class Application(_BaseModel):
    """A Model of an Application

    >>> from panel.site import User
    >>> philipp = User(
    ...     name = "Philipp Rudiger",
    ...     url = "https://github.com/philippjfr",
    ...     email = "na@hotmail.com",
    ...     avatar = "https://avatars.githubusercontent.com/u/1550771",
    ...     resources = {"twitter": "https://twitter.com/PhilippJFR"},
    ...     tags = ["pyviz", "developer"],
    ... )
    >>> Application(
    ...     name = "Panel",
    ...     description = "The analytics app framework to rule them all",
    ...     description_long = "Turns every dash into something lit",
    ...     author = philipp,
    ...     owner = philipp,
    ...     url = "https://panel.holoviz.org",
    ...     thumbnail = "https://panel.holoviz.org/_static/logo_stacked.png",
    ...     resources = {"github": "https://github.com/holoviz/panel"},
    ...     tags = ["awesome", "analytics", "apps"]
    ... )
    """

    name = param.String(
        default="New Application",
        precedence=1,
        doc="""
        The name of the application""",
    )

    author = param.ClassSelector(class_=User, constant=True, precedence=1)
    owner = param.ClassSelector(class_=User, constant=True, precedence=1)

    description = param.String(
        regex="^.{0,150}$",
        precedence=1,
        doc="""
        A short text introduction of max 150 characters.""",
    )
    description_long = param.String(
        precedence=1,
        doc="""
        A longer description. Can contain Markdown and HTML""",
    )

    servable = param.String(precedence=2, doc="The path to a servable Panel application")
    url = param.String(precedence=2, doc="The url of the application.")
    thumbnail = param.String(precedence=2, doc="The url of a thumbnail of the application.")

    def __init__(self, **params):
        for key in ["author", "owner"]:
            if key in params:
                user = params[key]
                if isinstance(user, str):
                    params[key] = User(uid=user, name=user)
            else:
                params[key] = User()

        super().__init__(**params)

    @staticmethod
    def _get_applications(config, users):
        """Returns a list of Applications from the specificed list of dicts.

        users is a list of existing Users
        """
        if not config:
            return []

        user_map = {user.uid: user for user in users}

        applications = _get_nested_value(config, "applications")
        if not applications:
            return []

        for application in applications:
            for key in ["author", "owner"]:
                if key in application:
                    user = application[key]
                    if user in user_map:
                        application[key] = user_map[user]

        return [
            Application(**application) for application in applications if not _skip(application)
        ]

    @classmethod
    def read(cls, file):
        """Returns a list of Applications from the specified file

        Currently only yaml is supported

        Args:
            path (str|pathlib.Path): The path to the file
        """
        with open(file, "r") as stream:
            config = yaml.safe_load(stream)
        users = User._get_users(config)
        return cls._get_applications(config, users)
