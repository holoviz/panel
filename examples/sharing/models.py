import pathlib
import shutil
import subprocess
import tempfile

from io import BytesIO
from typing import Dict, List

import config
import param

from utils import set_directory
import uuid

class Repository(param.Parameterized):
    name = param.String(config.REPOSITORY_NAME, constant=True)
    code = param.String(config.CODE)
    readme = param.String(config.README)
    thumbnail = param.String(config.THUMBNAIL)
    requirements = param.String(config.REQUIREMENTS)

    def items(self)-> Dict:
        return {
            "app.py": self.code,
            "readme.md" : self.readme,
            "thumbnail.png": self.thumbnail,
            "requirements.txt": self.requirements,
        }.items()

    def save(self, path: pathlib.Path):
        path.mkdir(parents=True, exist_ok=True)
        for file_path, text in self.items():
            pathlib.Path(path / file_path).write_text(text)

class Project(param.Parameterized):
    name = param.String(config.PROJECT_NAME)
    repository = param.ClassSelector(class_=Repository)
    
    def __init__(self, **params):
        if not "repository" in params:
            params["repository"]=Repository()

        super().__init__(**params)

        if not "name" in params:
            with param.edit_constant(self):
                self.name=config.PROJECT_NAME

    def __str__(self):
        return self.name

    def save(self, path: pathlib.Path):
        self.repository.save(path=path)

class User(param.Parameterized):
    name = param.String(config.USER_NAME, constant=True, regex=config.USER_NAME_REGEX)
    authenticated = param.Boolean(config.AUTHENTICATED, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        if not "name" in params:
            with param.edit_constant(self):
                self.name=config.USER_NAME

    def __str__(self):
        return self.name

class Storage(param.Parameterized):
    def __getitem__(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()
    
    def keys(self):
        raise NotImplementedError()


class FileStorage(Storage):
    def __init__(self, path: str):
        super().__init__()
        
        self._path = pathlib.Path(path).absolute()
    
    def __getitem__(self, key):
        raise NotImplementedError()

    def _get_source_path(self, key)->pathlib.Path:
        return self._path / "source" / key

    def _get_target_path(self, key)->pathlib.Path:
        return self._path / "target" / key

    def __setitem__(self, key: str, value: Project):
        source = self._get_source_path(key)
        value.save(source)
        target = self._get_target_path(key)
        target.mkdir(parents=True, exist_ok=True)
        
        with set_directory(source):
            command = f"panel convert app.py --requirements requirements.txt --to pyodide-worker --skip-embed --out {target.absolute()}"
            result = subprocess.run(command, shell=True)

    def __delitem__(self, key):
        raise NotImplementedError()
    
    def keys(self):
        raise NotImplementedError()
    
    def get_zipped_folder(self, key)->BytesIO:
        # Todo: This only includes the repository files. We should also include the converted files
        source = self._get_source_path(key).absolute()
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(pathlib.Path(tmpdir)):
                target_file = "saved"
                result = shutil.make_archive(target_file, 'zip', source)
                with open(result, "rb") as fh:
                    return BytesIO(fh.read())

class TmpFileStorage(FileStorage):
    pass

class AzureBlobStorage(Storage):
    pass

class Site(param.Parameterized):
    name = param.String(config.SITE, constant=True)
    title = param.String(config.TITLE, constant=True)
    faq = param.String(config.FAQ, constant=True)
    about = param.String(config.ABOUT, constant=True)
    thumbnail = param.String(config.THUMBNAIL, constant=True)

    development_storage = param.ClassSelector(class_=Storage, constant=True)
    examples_storage = param.ClassSelector(class_=Storage, constant=True)
    shared_storage = param.ClassSelector(class_=Storage, constant=True)

    auth_provider = param.Parameter(constant=True)

    def __init__(self, **params):
        if not "development_storage" in params:
            params["development_storage"]=TmpFileStorage(path="apps/development")
        if not "examples_storage" in params:
            params["examples_storage"]=FileStorage(path="apps/examples")
        if not "shared_storage" in params:
            params["shared_storage"]=FileStorage(path="apps/shared")

        super().__init__(**params)

        if not "name" in params:
            with param.edit_constant(self):
                self.name = config.SITE

    def get_shared_key(self, user: User, project: Project):
        return user.name + "/" + project.name

    def get_shared_src(self, key):
        return f"apps/{key}/app.html"

    def get_development_src(self, key):
        return f"tmp-apps/{key}/app.html"

class AppState(param.Parameterized):
    site = param.Parameter(constant=True)
    user = param.Parameter(constant=True)
    project = param.Parameter(constant=True)

    # Todo: make the below constant
    # could not do it as it raised an error!
    development_key = param.String()
    development_url = param.String()
    
    shared_key = param.String()
    shared_url = param.String()

    def __init__(self, **params):
        if not "site" in params:
            params["site"]=Site()
        if not "user" in params:
            params["user"]=User()
        if not "project" in params:
            params["project"]=Project()
        
        super().__init__(**params)

    def set_development(self, key: str):
        self.development_key = key
        self.development_url = self.site.get_development_src(key)

    def set_shared(self, key: str):
        self.shared_key = key
        self.shared_url = self.site.get_shared_src(key)

    @param.depends("user.name", "project.name", watch=True, on_init=True)
    def _update_shared(self):
        key = self.site.get_shared_key(user=self.user, project=self.project)
        self.set_shared(key)

    def _get_random_key(self):
        return str(uuid.uuid4())
    
    def convert(self):
        key = self._get_random_key()
        self.site.development_storage[key] = self.project
        self.set_development(key)


    