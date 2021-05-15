import param
import toml
import uuid

class _BaseModel(param.Parameterized):
    """The BaseModel adds ordering by the name parameter to a Class"""

    uid = param.String(doc="A unique id identifying the item.")
    name = param.String(default="New Model", doc="The name of the item")
    category = param.String(doc="The category of the item")
    tags = param.List(
        class_=str,
        doc="""A list of tags like 'machine-learning', 'panel', 'holoviews'.""",
    )
    resources = param.Dict(doc="""
        A dictionary of urls. For example 'github': 'https://panel.holoviz.org'""")

    def __init__(self, **params):
        if not "uid" in params:
            params["uid"] = str(uuid.uuid4())
        if not "resources" in params:
            params["resources"]={}

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
    def create_from_toml(cls, path, clean_func = None):
        """Returns a Dictionary of Models from the toml file specified by the path"""
        config = toml.load(path)
        if not clean_func:
            clean_func = lambda x: x
        return {key: cls(uid=key, **clean_func(value)) for key, value in config.items()}

class User(_BaseModel):
    """A Model of a User

    >>> from panel.application import User
    >>> User(
    ...     name = "Philipp Rudiger",
    ...     url = "https://github.com/philippjfr",
    ...     email = "na@hotmail.com",
    ...     avatar = "https://avatars.githubusercontent.com/u/1550771",
    ...     tags = ["pyviz", "developer"],
    ...     resources = {"twitter": "https://twitter.com/PhilippJFR"},
    ... )
    """

    name = param.String(default="New User", doc="The name of the user.")

    url = param.String(doc="An url pointing to a page about the user.")
    email = param.String(doc="The email of the user.")

    avatar = param.String(doc="The url of an avatar image of the user.")

class Application(_BaseModel):
    """A Model of an Application

>>> from panel.application import User
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

    name = param.String(default="New Application", doc="""
        The name of the application""")

    author = param.ClassSelector(class_=User)
    owner = param.ClassSelector(class_=User)

    description = param.String(regex="^.{0,150}$", doc="""
        A short text introduction of max 150 characters.""", )
    description_long = param.String(doc="""
        A longer description. Can contain Markdown and HTML""")

    url = param.String(doc="The url of the application.")

    thumbnail = param.String(doc="The url of a thumbnail of the application.")

    def __init__(self, **params):
        for key in ["author", "owner"]:
            if key in params:
                user = params[key]
                if isinstance(user, str):
                    params[key]=User(uid=user, name=user)
            else:
                params[key]=User()

        super().__init__(**params)
