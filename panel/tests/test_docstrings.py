import pytest

from panel.viewable import Viewable


## Find child classes of MaterialComponent
def find_child_classes(cls):
    """
    Recursively find all child classes of MaterialComponent.
    """
    child_classes = []
    for subclass in cls.__subclasses__():
        child_classes.append(subclass)
        child_classes.extend(find_child_classes(subclass))
    return child_classes

def find_topmost_defining_class(cls, param_name):
    """
    Find the topmost parent class in the MRO that defines the parameter.
    Parameters
    ----------
    cls : type
        The class to start searching from.
    param_name : str
        The name of the parameter to search for.
    Returns
    -------
    type
        The topmost parent class that defines the parameter.
    """
    for base in reversed(cls.mro()):
        if hasattr(base, 'param') and param_name in getattr(base, 'param', {}):
            return base
    return cls

child_classes = find_child_classes(Viewable)

@pytest.mark.parametrize("child_class", child_classes)
def test_component_parameters_have_doc_attributes_set(child_class):
    """Test to ensure all parameters in component subclasses have docstrings set.
    Prints the topmost parent class that defines the parameter if missing docstring.
    """

    for name in child_class.param:
        if name.startswith('_'):
            continue
        parameter = child_class.param[name]
        if not parameter.doc:
            topmost_class = find_topmost_defining_class(child_class, name)
            message = (
                f"Parameter '{name}' in class '{topmost_class.__module__}.{topmost_class.__name__}' "
                "has no `doc` string."
            )
            raise AssertionError(message)
