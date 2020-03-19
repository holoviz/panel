from tranquilizer.handler import ScriptHandler, NotebookHandler
from tranquilizer.main import make_app


def build_single_handler_application(files, argv):
    functions = []
    for filename in files:
        extension = filename.split('.')[-1]
        if extension == 'py':
            source = ScriptHandler(filename)
        elif extension == 'ipynb':
            try:
                import nbconvert
            except ImportError as e: # pragma no cover
                raise ImportError("Please install nbconvert to serve Jupyter Notebooks.") from e

            source = NotebookHandler(args.filename)
        else:
            raise UnsupportedFileType('{} is not a script (.py) or notebook (.ipynb)'.format(filename))
        functions.extend(source.tranquilized_functions)
    return make_app(functions, 'Panel REST API')
