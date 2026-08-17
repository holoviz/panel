# panel.io.datamodel module

class panel.io.datamodel.Parameterized(\*, default: T \| UndefinedType \| IntrinsicType = Intrinsic, help: str \| None = None)
Bases: `Property`

Accept a Parameterized object.

This property only exists to support type validation, e.g. for “accepts”
clauses. It is not serializable itself, and is not useful to add to
Bokeh models directly.

class panel.io.datamodel.ParameterizedList(\*, default: T \| UndefinedType \| IntrinsicType = Intrinsic, help: str \| None = None)
Bases: `Property`

Accept a list of Parameterized objects.

This property only exists to support type validation, e.g. for “accepts”
clauses. It is not serializable itself, and is not useful to add to
Bokeh models directly.

validate(value, detail=True)
Determine whether we can set this property from this value.

Validation happens before transform()

Args:
value (obj) : the value to validate against this property type detail
(bool, options) : whether to construct detailed exceptions

>
>
> Generating detailed type validation error messages can be expensive.
> When doing type checks internally that will not escape exceptions to
> users, these messages can be skipped by setting this value to False
> (default: True)
>
>

Returns:
None

Raises:
ValueError if the value is not valid for this property type

class panel.io.datamodel.PolarsDataFrame(\*, default: T \| UndefinedType \| IntrinsicType = Intrinsic, help: str \| None = None)
Bases: `Property`

Accept Polars DataFrame values.

This property only exists to support type validation, e.g. for “accepts”
clauses. It is not serializable itself, and is not useful to add to
Bokeh models directly.

validate(value: Any, detail: bool = True) → None
Determine whether we can set this property from this value.

Validation happens before transform()

Args:
value (obj) : the value to validate against this property type detail
(bool, options) : whether to construct detailed exceptions

>
>
> Generating detailed type validation error messages can be expensive.
> When doing type checks internally that will not escape exceptions to
> users, these messages can be skipped by setting this value to False
> (default: True)
>
>

Returns:
None

Raises:
ValueError if the value is not valid for this property type

panel.io.datamodel.construct_data_model(parameterized, name=None, ignore=\[\], types={}, extras={})
Dynamically creates a Bokeh DataModel class from a Parameterized object.

Parameters:
**parameterized: param.Parameterized \| type\[param.Parameterized\]**
The Parameterized class or instance from which to create the DataModel

**name: str or None**
Name of the dynamically created DataModel class

**ignore: list(str)**
List of parameters to ignore.

**types: dict**
A dictionary mapping from parameter name to a Parameter type, making it
possible to override the default parameter types.

**extras: dict**
Additional properties to define on the DataModel.

Returns:
DataModel

panel.io.datamodel.create_linked_datamodel(obj, root=None)
Creates a Bokeh DataModel from a Parameterized class or instance which
automatically links the parameters bi-directionally.

Parameters:
**obj: param.Parameterized**
The Parameterized class to create a linked DataModel for.

Returns:
DataModel instance linked to the Parameterized object.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
