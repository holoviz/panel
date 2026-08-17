# Debugger
---
```python
import logging

import panel as pn

pn.extension('terminal', console_output='disable')
```

The `Debugger` is an uneditable Card layout which lets your front end show logs and errors that may fire whenever your dashboard is running.

When running a panel server with several end users, the debugger will let them know whenever one of their interactions did not run as planned. Information can also be logged for end users to know that everything went well in the back-end. If logger_names is not specified, events must be logged using the `panel` logger or a custom child logger, e.g. `panel.myapp`.

It is also usable in a live notebook and complements the `console_output` logs.

Note the debugger is based on the `terminal widget` and requires `pn.extension('terminal')` to be called.

####  Parameters:

* **``only_last``** (bool): when exceptions are logged, indicates whether only the last trace in the stack will be prompted. Note this does not change how logs are thrown to `stderr`, the logs on server side will be accessible as you programmed them. Default: `False`
* **``level``** (int): The log level you want to be prompt on the front end. Available values are the same as in [the standard levels of the `logging` package](https://docs.python.org/3/library/logging.html#levels). Default: `logging.ERROR`
* **``formatter_args``** (dict): arguments to pass to the [Formatter object](https://docs.python.org/3/library/logging.html#formatter-objects). You may modify the prompt format with `fmt` or date formats with `datefmt` as in the standard library. Default: `{'fmt':"%(asctime)s [%(name)s - %(levelname)s]: %(message)s"}`
* **``logger_names``** (list): [loggers called with `getLogger`](https://docs.python.org/3/library/logging.html#logging.getLogger) which will be prompted to the terminal. In a server context, note only the errors thrown  within the user session will be prompted, not all errors throughout the server. Default: `['panel']`

```python
debug = pn.widgets.Debugger(name='My Debugger')
debug
```

We are making a radio button attached to a callback that intentionally throws an error. Upon clicking on the error generating buttons, you will see the error number increasing in the debugger. Note the inline log was disabled with `pn.config.console_output = 'disable'` to avoid cluterring the notebook.

```python
btn = pn.widgets.RadioButtonGroup(label='Throw error', value='no error', options=['ZeroDivision', 'no error', 'Custom error'], color='danger')

def throw_error(event):
    if event == 'ZeroDivision':
        return pn.pane.Str(1/0)
    elif event == 'no error':
        return pn.pane.Str('Hello!')
    elif event == 'Custom error':
        raise Exception('custom error thrown')
    
pn.Column(btn, pn.bind(throw_error, btn))
```

We may also send information to the front end. Let's create a new debugger with a lower logging level

```python
logger = logging.getLogger('panel.myapp')

debug_info = pn.widgets.Debugger(
    name='Debugger info level', level=logging.INFO, sizing_mode='stretch_both',
    logger_names=['panel.myapp'], #comment this line out to get all panel errors
)
```

```python
btn_info = pn.widgets.RadioButtonGroup(label='show info', options=['debug', 'info', 'warning'])

def throw_error(event):
    msg = (event + ' sent from btn_info').capitalize()
    if event == 'info':
        logger.info(msg)
    elif event == 'debug':
        logger.debug(msg)
    elif event == 'warning':
        logger.warning(msg)
    return msg

c = pn.Column(btn_info, debug_info, pn.bind(throw_error, btn_info), sizing_mode='stretch_both')
c
```

The end user may save the logs by clicking on the floppy disk 💾 and clear the debugger by clicking on the check box button ☐.

```python
debug_info.btns
```

---
