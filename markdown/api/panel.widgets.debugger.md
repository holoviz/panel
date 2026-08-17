# panel.widgets.debugger module

The Debugger Widget is an uneditable Card that gives you feedback on
errors thrown by your Panel callbacks.

class panel.widgets.debugger.CheckFilter(name='')
Bases: `Filter`

add_debugger(debugger)
Add a debugger to this logging filter.

Parameters:
widg : panel.widgets.Debugger
The widget displaying the logs.

Returns:
None.

filter(record)
Will filter out messages coming from a different bokeh document than the
document where the debugger is embedded in server mode. Returns True if
no debugger was added.

class panel.widgets.debugger.Debugger(\*, \_number_of_errors, \_number_of_infos, \_number_of_warnings, formatter_args, level, logger_names, only_last, active_header_background, button_css_classes, collapsed, collapsible, header, header_background, header_color, header_css_classes, hide_header, title, title_css_classes, auto_scroll_limit, scroll_button_threshold, scroll_position, view_latest, scroll, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Card](panel.layout.card.md#panel.layout.card.Card)

A uneditable Card layout holding a terminal printing out logs from your
callbacks. By default, it will only print exceptions. If you want to add
your own log, use the panel.callbacks logger within your callbacks:
logger = logging.getLogger(‘panel.callbacks’)

Methods

|                        |     |
|------------------------|-----|
| **acknowledge_errors** |     |
| **update_log_counts**  |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
> [class="reference internal" title="panel.layout.card.Card"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.card.Card](panel.layout.card.md#panel.layout.card.Card):
> css_classes, active_header_background, button_css_classes,
> collapsible, collapsed, header, header_background, header_color,
> header_css_classes, hide_header, title_css_classes, title
>
>

`_number_of_errors`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``errors')`
Number of logged errors since last acknowledged.

`_number_of_warnings`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``warnings')`
Number of logged warnings since last acknowledged.

`_number_of_infos`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``infos')`
Number of logged information since last acknowledged.

`only_last`` ``=`` ``Boolean(default=True,`` ``label='Only`` ``last')`
Whether only the last stack is printed or the full.

`level`` ``=`` ``Integer(default=40,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Level')`
Logging level to print in the debugger terminal.

`formatter_args`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'fmt':`` ``'%(asctime)s`` ``[%(name)s`` ``-`` ``%(levelname)s]:`` ``%(message)s'},`` ``label='Formatter`` ``args')`
Arguments to pass to the logging formatter. See the standard python
logging libraries.

`logger_names`` ``=`` ``List(bounds=(1,`` ``None),`` ``default=['panel'],`` ``item_type=<class`` ``'str'>,`` ``label='Logger`` ``names')`
Loggers which will be prompted in the debugger terminal.

class panel.widgets.debugger.DebuggerButtons(\*, clears, debug_name, terminal_output, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`terminal_output`` ``=`` ``String(default='',`` ``label='Terminal`` ``output')`
The output of the terminal, which is updated by the debugger widget.

`debug_name`` ``=`` ``String(default='',`` ``label='Debug`` ``name')`
The name of the debugger, used to save the terminal output to a file.

`clears`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Clears')`
The number of times the terminal has been cleared.

class panel.widgets.debugger.TermFormatter(\*args, only_last=True, **kwargs)
Bases: `Formatter`

format(record)
Format the specified record as text.

The record’s attribute dictionary is used as the operand to a string
formatting operation which yields the returned string. Before formatting
the dictionary, a couple of preparatory steps are carried out. The
message attribute of the record is computed using
LogRecord.getMessage(). If the formatting string uses the time (as
determined by a call to usesTime(), formatTime() is called to format the
event time. If there is exception information, it is formatted using
formatException() and appended to the message.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
