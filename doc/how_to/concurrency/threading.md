# Enable Automatic Threading

Using threading in Panel can either be enabled manually, e.g. by managing your own thread pool and dispatching concurrent tasks to it, or it can be managed by Panel itself by setting the `config.nthreads` parameter (or equivalently by setting it with `pn.extension(nthreads=...)`. This will start a `ThreadPoolExecutor` with the specified number of threads (or if set to `0` it will set the number of threads based on your system, i.e. `min(32, os.cpu_count() + 4)`).

Whenever an event is generated or a periodic callback fires Panel will then automatically dispatch the event to the executor. An event in this case refers to any action generated on the frontend such as the manipulation of a widget by a user or the interaction with a plot. If you are launching an application with `panel serve` you should enable this option configure this option on the CLI by setting `--num-threads`.

To demonstrate the effect of enabling threading take this example below:

```python
import panel as pn

pn.extension(nthreads=2)

def button_click(event):
    print(f'Button clicked for the {event.new}th time.')
    time.sleep(2) # Simulate long running operation
    print(f'Finished processing {event.new}th click.')

button = pn.widgets.Button(name='Click me!')

button.on_click(button_click)
```

When we click the button twice successively in a single-threaded context we will see the following output:

```
> Button clicked for the 1th time.
... 2 second wait
> Finished processing 1th click.
> Button clicked for the 2th time.
... 2 second wait
> Finished processing 2th click.
```

In a threaded context on the other hand the two clicks will be processed concurrently:

```
> Button clicked for the 1th time.
> Button clicked for the 2th time.
... 2 second wait
> Finished processing 1th click.
> Finished processing 2th click.
```

```{note}
Note that the global ThreadPool is used to dispatch events triggered by changes in parameters, events (such as click events), [`defer_load`](../callbacks/defer_load) callbacks and optionally [`onload` callbacks](../callbacks/load).
```
