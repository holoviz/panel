# panel.io.admin module

class panel.io.admin.Data(\*, data, name)
Bases: `Parameterized`

**Parameter Definitions**

------------------------------------------------------------------------

`data`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'logging.LogRecord'>,`` ``label='Data')`

class panel.io.admin.LogDataHandler(data)
Bases: `StreamHandler`

emit(record: LogRecord)
Emit a record.

If a formatter is specified, it is used to format the record. The record
is then written to the stream with a trailing newline. If exception
information is present, it is formatted using traceback.print_exception
and appended to the stream. If the stream has an ‘encoding’ attribute,
it is used to determine how to do the output to the stream.

class panel.io.admin.LogFilter(name='')
Bases: `Filter`

filter(record)
Determine if the specified record is to be logged.

Returns True if the record should be logged, or False otherwise. If
deemed appropriate, the record may be modified in-place.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
