import importlib.util

import param
import re

def _get_parameterized_classes(module_name, module_path):
    """Returns an iterator of the Parameterized classes of a module to be included in a stub file"""    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    for value in foo.__dict__.values():
        try:
            if  issubclass(value, param.Parameterized) and value.__module__==module_name:
                yield(value)
        except:
            pass

def _to_class_name(parameterized):
    return parameterized.__name__

def _to_bases(parameterized):
    return ", ".join(item.__name__ for item in  parameterized.__bases__)

MAP = {
    param.Boolean: 'bool',
    param.Color: 'str',
    param.Integer: 'int',
    param.Parameter: 'Any',
    param.String: 'str',
}

def _default_to_string(default):
    if default is None:
        return 'None'
    elif isinstance(default, str):
        return f'"{default}"'
    else:
        return str(default)

def _to_typehint(parameter: param.Parameter) -> str:
    """Returns the typehint as a string of a Parameter"""
    if isinstance(parameter, param.ClassSelector):
        class_ = parameter.class_
        if isinstance(class_, (list, tuple, set)):
            tpe = "Union[" + ",".join(sorted((item.__name__ for item in class_), key=str.casefold)) + "]"
        else:
            tpe = class_.__name__
    elif isinstance(parameter, param.ObjectSelector):
        types = set(type(item).__name__ for item in parameter.objects)
        if len(types)==0:
            tpe = "Any"
        elif len(types)==1:
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
    elif parameter.__class__ in MAP:
        tpe = MAP[parameter.__class__]
    else:
        raise NotImplementedError(parameter)
    
    if parameter.allow_None and not tpe=='Any':
        tpe = f"Optional[{tpe}]"

    default_str = _default_to_string(parameter.default)
    tpe +=f"={default_str}"

    return tpe

def _to_type_hints(parameterized) -> dict:
    """Returns a dictionary of parameter names and typehints"""
    typed_attributes = {}
    for parameter_name in parameterized.param:
        parameter=parameterized.param[parameter_name]
        if not parameter_name.startswith("_"):
            typehint = _to_typehint(parameter)
            typed_attributes[parameter]=typehint
    return typed_attributes

def _to_typed_attributes(parameterized):
    """Returns a string of typed attributes
    
    Example:

    value: int=0
    value_throttled: Optional[int]=None
    ...
"""
    typed_attributes = ""
    for parameter, typehint in _to_type_hints(parameterized).items():
        if not parameter.name=="name" and parameter.owner is parameterized:
            if typed_attributes:
                typed_attributes += "\n"
            typed_attributes += f"    {parameter.name}: {typehint}"
    return typed_attributes

def _sorted_parameter_names(parameterized):
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

def _to_init(parameterized):
    """Returns the __init__ signature with typed arguments"""
    typed_attributes = ""
    type_hints=_to_type_hints(parameterized)
    for parameter in _sorted_parameters(parameterized):
        if not parameter in type_hints:
            continue
        typehint=type_hints[parameter]
        if typed_attributes:
            typed_attributes += "\n"
        typed_attributes += f"        {parameter.name}: {typehint},"
    return f"""\
    def __init__(self,
{typed_attributes}
    ):"""

ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

def _get_original_docstring(parameterized):
    """Returns the original docstring of a Parameterized class"""
    doc=ansi_escape.sub('', parameterized.__doc__)
    doc2=doc[doc.find("\n")+1:]
    doc3=doc2[:doc2.find("\nParameters of \'")]
    return doc3

def _get_args(parameterized):
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
            doc = parameter.doc.lstrip('\n').lstrip()
            if "\n\n" in doc:
                doc = doc.split("\n\n")[0] # We simplify the docstring for now
            doc=doc.replace("\n", " ") # Move to one line
            doc=re.sub(' +', ' ', doc)
            args += f"        {name}: {doc}"
    return args

def to_stub(parameterized):
    """Returns the stub of a Parameterized class"""
    class_name = _to_class_name(parameterized)
    bases = _to_bases(parameterized)
    _typed_parameters = _to_typed_attributes(parameterized)
    _init = _to_init(parameterized)
    original_doc=_get_original_docstring(parameterized)
    args = _get_args(parameterized)
    return f'''class {class_name}({bases}):
{_typed_parameters}

{_init}
        """{original_doc}"""

        Args:
{args}
'''

    