import importlib.util
from types import ModuleType
import inspect

import param
import re
from typing import Type

import logging

logger = logging.getLogger("param_stubgen")


def _get_parameterized_classes(mod: ModuleType):
    """Returns an iterator of the Parameterized classes of a module to be included in a stub file"""
    module_name = mod.__name__
    module_path = mod.__file__

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    for value in foo.__dict__.values():
        try:
            if issubclass(value, param.Parameterized) and value.__module__ == module_name:
                yield (value)
        except:
            pass


def _to_class_name(parameterized):
    return parameterized.__name__


def _to_class_str(object) -> str:
    return str(object.__name__)


def _to_bases(parameterized):
    return ", ".join(item.__name__ for item in parameterized.__bases__)


PARAMETER_TO_TYPE = {
    param.Boolean: "bool",
    param.Color: "str",
    param.Integer: "int",
    param.Parameter: "Any",
    param.String: "str",
    param.Number: "Number",
    param.Date: "Union[datetime,date,np.datetime64]",
    param.Tuple: "tuple",
    param.Range: "Tuple[Number,Number]",
}


def _default_to_string(default):
    if default is None:
        return "None"
    elif isinstance(default, str):
        return f'"{default}"'
    else:
        return str(default)


def _to_typehint(parameter: param.Parameter) -> str:
    """Returns the typehint as a string of a Parameter

    Example:

    Optional[int]=None
    """
    if isinstance(parameter, param.ClassSelector):
        class_ = parameter.class_
        if isinstance(class_, (list, tuple, set)):
            tpe = (
                "Union["
                + ",".join(sorted((item.__name__ for item in class_), key=str.casefold))
                + "]"
            )
        else:
            tpe = class_.__name__
    elif isinstance(parameter, param.ObjectSelector):
        types = set(type(item).__name__ for item in parameter.objects)
        if len(types) == 0:
            tpe = "Any"
        elif len(types) == 1:
            tpe = types.pop()
        else:
            tpe = "Union[" + ",".join(sorted(types, key=str.casefold)) + "]"
    elif isinstance(parameter, param.List):
        class_ = parameter.class_
        if isinstance(class_, (list, tuple, set)):
            tpe = "List[" + ",".join(item.__name__ for item in class_) + "]"
        elif class_:
            tpe = f"List[{class_.__name__}]"
        else:
            tpe = "list"
    elif parameter.__class__ in PARAMETER_TO_TYPE:
        tpe = PARAMETER_TO_TYPE[parameter.__class__]
    else:
        raise NotImplementedError(parameter)

    if parameter.allow_None and not tpe == "Any":
        tpe = f"Optional[{tpe}]"

    default_str = _default_to_string(parameter.default)
    tpe += f"={default_str}"

    return tpe


def _to_type_hints(parameterized: Type[param.Parameterized]) -> dict:
    """Returns a dictionary of parameter names and typehints with default values

    Example:

    {
        "value": "int=0",
        "value_throttled": "Optional[int]=None",
    }
    """
    typed_attributes = {}
    for parameter_name in parameterized.param:
        parameter = parameterized.param[parameter_name]
        if not parameter_name.startswith("_"):
            typehint = _to_typehint(parameter)
            typed_attributes[parameter] = typehint
    return typed_attributes


def _to_typed_attributes(parameterized: Type[param.Parameterized]) -> str:
    """Returns a string of typed attributes

    Example:

    value: int=0
    value_throttled: Optional[int]=None
    ..."""
    typed_attributes = ""
    for parameter, typehint in _to_type_hints(parameterized).items():
        if not parameter.name == "name" and parameter.owner is parameterized:
            if typed_attributes:
                typed_attributes += "\n"
            typed_attributes += f"    {parameter.name}: {typehint}"
    return typed_attributes


def _sorted_parameter_names(parameterized: Type[param.Parameterized]) -> str:
    "Returns a list of parameter names sorted by 'relevance'. Most relevant parameters first."
    parameters = []
    for class_ in reversed(parameterized.mro()):
        if issubclass(class_, param.Parameterized):
            for parameter in reversed(list(class_.param)):
                if not parameter in parameters:
                    parameters.append(parameter)
    return list(reversed(parameters))


def _sorted_parameters(parameterized):
    "Returns a list of parameter names sorted by 'relevance'. Most relevant parameters first."
    return [parameterized.param[name] for name in _sorted_parameter_names(parameterized)]


def _to_init(parameterized: Type[param.Parameterized]) -> str:
    """Returns the __init__ signature with typed arguments"""
    typed_attributes = ""
    type_hints = _to_type_hints(parameterized)
    for parameter in _sorted_parameters(parameterized):
        if not parameter in type_hints:
            continue
        typehint = type_hints[parameter]
        if typed_attributes:
            typed_attributes += "\n"
        typed_attributes += f"        {parameter.name}: {typehint},"
    return f"""\
    def __init__(self,
{typed_attributes}
    ):"""


ANSI_ESCAPE = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)

import ast
# fname = "panel/widgets/slider.py"
# with open(fname, 'r') as f:
#     tree = ast.parse(f.read())
 
# for t in tree.body:
#     print(t.__dict__)
#     try:
#         docstring = ast.get_docstring(t)
#         print(docstring)
#     except Exception:
#         pass

def _get_node(tree, parameterized: Type[param.Parameterized]):
    for t in tree.body:
        try:
            if t.name==parameterized.name:
                return t
        except:
            pass
    return None

def _get_original_docstring(parameterized: Type[param.Parameterized]) -> str:
    """Returns the original docstring of a Parameterized class"""
    tree = ast.parse(inspect.getsource(parameterized))
    node=_get_node(tree, parameterized)
    if node:
        doc=ast.get_docstring(node)
    else:
        raise NotImplementedError()
    if not doc:
        logger.warning(
            "%s has no doc string: %s:%s",
            parameterized.__name__,
            inspect.getfile(parameterized),
            inspect.findsource(parameterized)[1] + 1,
        )
    
    return doc


def _get_args(parameterized: Type[param.Parameterized]) -> str:
    """Returns a string of arguments with docstrings

    Example:

    value: The slider value. Updated when the slider is dragged
    value_throttled: The slider value. Updated on mouse up.
    """
    args = ""
    for name in sorted(parameterized.param):
        parameter = parameterized.param[name]
        if not name.startswith("_"):
            if args:
                args += "\n"
            if parameter.doc:
                doc = parameter.doc
            else:
                doc = ""
                logger.warning(
                    "%s.%s has no doc string: %s:%s",
                    parameterized.__name__,
                    parameter.name,
                    inspect.getfile(parameterized),
                    inspect.findsource(parameterized)[1] + 1,
                )
            doc = doc.lstrip("\n").lstrip()
            if "\n\n" in doc:
                doc = doc.split("\n\n")[0]  # We simplify the docstring for now
            doc = doc.replace("\n", " ")  # Move to one line
            doc = re.sub(" +", " ", doc)
            args += f"        {name}: {doc}"
    return args


def parameterized_to_stub(parameterized: Type[param.Parameterized]) -> str:
    """Returns the stub of a Parameterized class"""
    class_name = _to_class_name(parameterized)
    bases = _to_bases(parameterized)
    typed_parameters = _to_typed_attributes(parameterized)
    init = _to_init(parameterized)
    original_doc = _get_original_docstring(parameterized)
    args = _get_args(parameterized)

    return f'''class {class_name}({bases}):
{typed_parameters}

{init}
        """{original_doc}

        Args:
{args}
"""
'''


def module_to_stub(module: ModuleType) -> str:
    stub = ""
    for parameterized in _get_parameterized_classes(module):
        stub += "\n\n" + parameterized_to_stub(parameterized)
    return stub


