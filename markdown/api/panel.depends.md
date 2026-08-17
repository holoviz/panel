# panel.depends module

panel.depends.bind(function: Callable\[\[...\], Any\], \*args: Any, watch: bool = False, **kwargs: Any) → Callable\[\[...\], Any\]
Bind constant values, parameters, bound functions or reactive
expressions to a function.

This function creates a wrapper around the given
`function`, binding some or all of its
arguments to constant values, `Parameter`
objects, or reactive expressions. The resulting function automatically
reflects updates to any bound parameters or reactive expressions,
ensuring that its output remains up-to-date.

Similar to `functools.partial()`, arguments can
also be bound to constants, leaving a simple callable object. When
`watch=True`, the function is automatically
evaluated whenever any bound parameter or reactive expression changes.

Parameters:
function : callable, generator, async generator, or coroutine
The function or coroutine to bind constant, dynamic, or reactive
arguments to. It can be:

- A standard callable (e.g., a regular function).

- A generator function (producing iterables).

- An async generator function (producing asynchronous iterables).

- A coroutine function (producing awaitables).

\*args : object, Parameter, bound function or reactive expression rx
Positional arguments to bind to the function. These can be constants,
param.Parameter objects, bound functions or reactive expressions.

watch : bool, optional
If True, the function is automatically evaluated whenever a bound
parameter or reactive expression changes. Defaults to False.

**kwargs : object, Parameter, bound function or reactive expression rx
Keyword arguments to bind to the function. These can also be constants,
param.Parameter objects, bound functions or reactive expressions.

Returns:
callable, generator, async generator, or coroutine
A new function with the bound arguments, annotated with all
dependencies. The function reflects changes to bound parameters or
reactive expressions.

Examples

Bind parameters to a function:

\>\>\>
import
param \>\>\>
class
Example(param.Parameterized):
...  a
=
param.Number(1)
...  b
=
param.Number(2)
\>\>\> example
=
Example()
\>\>\>
def
add(a,
b): ...
 return a
+ b
\>\>\> bound_add
=
param.bind(add,
example.param.a,
example.param.b)
\>\>\>
bound_add()
3

Update a parameter and observe the updated result:

\>\>\>
example.a
= 5
\>\>\>
bound_add()
7

Automatically evaluate the function when bound arguments change:

\>\>\> bound_watch
=
param.bind(print,
example.param.a,
example.param.b,
watch=True)
\>\>\>
example.a
= 1 \#
Triggers automatic evaluation 1 2

panel.depends.depends(\*dependencies: Dependency \| Callable\[t.Concatenate\[\_S, \_P\], \_R\], watch: bool = False, on_init: bool = False, **kw: Dependency) → DependsFunc\[\_P, \_R\] \| Callable\[\[Callable\[t.Concatenate\[\_S, \_P\], \_R\]\], DependsFunc\[\_P, \_R\]\]
Annotates a function or `Parameterized` method
to express its dependencies.

The specified dependencies can be either be
`Parameter` instances or if a method is
supplied they can be defined as strings referring to Parameters of the
class, or Parameters of subobjects (Parameterized objects that are
values of this object’s parameters). Dependencies can either be on
Parameter values, or on other metadata about the Parameter.

Parameters:
watch : bool, optional
Whether to invoke the function/method when the dependency is updated, by
default `False`.

on_init : bool, optional
Whether to invoke the function/method when the instance is created, by
default `False`.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
