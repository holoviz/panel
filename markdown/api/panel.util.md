# panel.util package

## Submodules

- [panel.util.checks module](panel.util.checks.md)
  - [isIn()](panel.util.checks.md#panel.util.checks.isIn)
  - [is_holoviews()](panel.util.checks.md#panel.util.checks.is_holoviews)
  - [is_parameterized()](panel.util.checks.md#panel.util.checks.is_parameterized)
  - [isdatetime()](panel.util.checks.md#panel.util.checks.isdatetime)
  - [isfile()](panel.util.checks.md#panel.util.checks.isfile)
- [panel.util.parameters module](panel.util.parameters.md)
  - [edit_readonly()](panel.util.parameters.md#panel.util.parameters.edit_readonly)
  - [extract_dependencies()](panel.util.parameters.md#panel.util.parameters.extract_dependencies)
  - [get_method_owner()](panel.util.parameters.md#panel.util.parameters.get_method_owner)
  - [recursive_parameterized()](panel.util.parameters.md#panel.util.parameters.recursive_parameterized)
- [panel.util.warnings module](panel.util.warnings.md)
  - [PanelDeprecationWarning](panel.util.warnings.md#panel.util.warnings.PanelDeprecationWarning)
  - [PanelUserWarning](panel.util.warnings.md#panel.util.warnings.PanelUserWarning)
  - [find_stack_level()](panel.util.warnings.md#panel.util.warnings.find_stack_level)

## Module contents

Various general utilities used in the panel codebase.

class panel.util.LazyHTMLSanitizer(**kwargs)
Bases: `object`

Wraps nh3.clean lazily importing it on the first call to clean.

Methods

|           |     |
|-----------|-----|
| **clean** |     |

panel.util.abbreviated_repr(value, max_length=25, natural_breaks=(',', ' '))
Returns an abbreviated repr for the supplied object. Attempts to find a
natural break point while adhering to the maximum length.

panel.util.base_version(version: str) → str
Extract the final release and if available pre-release (alpha, beta,
release candidate) segments of a PEP440 version, defined with three
components (major.minor.micro).

Useful to avoid nbsite/sphinx to display the documentation HTML title
with a not so informative and rather ugly long version (e.g.
`0.13.0a19.post4+g0695e214`). Use it in
`conf.py`:

version =
release =
base_version(package.\_\_version\_\_)

Return the version passed as input if no match is found with the
pattern.

panel.util.datetime_as_utctimestamp(value)
Converts a datetime to a UTC timestamp used by Bokeh internally.

panel.util.decode_token(token: str, signed: bool = True) → dict\[str, Any\]
Decodes a signed or unsigned JWT token.

panel.util.flatten(line)
Flatten an arbitrarily nested sequence.

Inspired by: pd.core.common.flatten

Parameters:
line : sequence
The sequence to flatten

Returns:
flattened : generator

Notes

This only flattens list, tuple, and dict sequences.

panel.util.full_groupby(l, key=\<function \<lambda\>\>)
Groupby implementation which does not require a prior sort

panel.util.fullpath(path: AnyStr \| PathLike) → str
Expanduser and then abspath for a given path.

panel.util.function_name(func) → str
Returns the name of a function (or its string repr)

panel.util.indexOf(obj, objs)
Returns the index of an object in a list of objects. Unlike the
list.index method this function only checks for identity not equality.

panel.util.param_name(name: str) → str
Removes the integer id from a Parameterized class name.

panel.util.param_reprs(parameterized, skip=None)
Returns a list of reprs for parameters on the parameterized object.
Skips default and empty values.

panel.util.parse_query(query: str) → dict\[str, Any\]
Parses a url query string, e.g. ?a=1&b=2.1&c=string, converting numeric
strings to int or float types.

panel.util.prefix_length(a: str, b: str) → int
Searches for the length of overlap in the starting characters of string
b in a. Uses binary search if b is not already a prefix of a.

panel.util.set_bokeh_validation(validate: bool)
Sets the bokeh validation mode for properties and callbacks.

Parameters:
**validate: bool**
Whether to enable validation.

panel.util.styler_update(styler, new_df)
Updates the todo items on a pandas Styler object to apply to a new
DataFrame.

Parameters:
**styler: pandas.io.formats.style.Styler**
Styler objects

**new_df: pd.DataFrame**
New DataFrame to update the styler to do items

Returns:
todos: list

panel.util.unique_iterator(seq)
Returns an iterator containing all non-duplicate elements in the input
sequence.

panel.util.url_path(url: str) → str
Strips the protocol and domain from a URL returning just the path.

panel.util.value_as_datetime(value)
Retrieve the value tuple as a tuple of datetime objects.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
