# panel.io.profile module

panel.io.profile.profile(name: str, engine: ProfilingEngine = 'pyinstrument') → Callable\[\[Callable\[\_P, \_R\]\], Callable\[\_P, \_R\]\]
A decorator which may be added to any function to record profiling
output.

Parameters:
**name: str**
A unique name for the profiling session.

**engine: str**
The profiling engine, e.g. ‘pyinstrument’, ‘snakeviz’ or ‘memray’

panel.io.profile.profile_ctx(engine: ProfilingEngine \| None = 'pyinstrument') → Iterator\[list\[Profile \| bytes \| Session\]\]
A context manager which profiles the body of the with statement with the
supplied profiling engine and returns the profiling object in a list.

Parameters:
**engine: str**
The profiling engine, e.g. ‘pyinstrument’, ‘snakeviz’ or ‘memray’

Returns:
sessions: list
A list containing the profiling session.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
