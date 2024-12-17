# Schedule Global Tasks

This guide addresses how to schedule tasks that run independently of any user visiting an application.

---

The `pn.state.schedule_task` functionality allows scheduling global tasks at certain times or on a specific schedule. This is distinct from [periodic callbacks](./periodic), which are scheduled per user session. Global tasks are useful for performing periodic actions like updating cached data, performing cleanup actions or other housekeeping tasks, while periodic callbacks should be reserved for making periodic updates to an application.

The different contexts in which global tasks and periodic callbacks run also has implications on how they should be scheduled. Scheduled task **must not** be declared in the application code itself, i.e. if you are serving `panel serve app.py` the callback you are scheduling must not be declared in the `app.py`. It must be defined in an external module or in a separate script declared as part of the `panel serve` invocation using the `--setup` commandline argument.

Scheduling using `pn.state.schedule_task` is idempotent, i.e. if a callback has already been scheduled under the same name subsequent calls will have no effect. By default the starting time is immediate but may be overridden with the `at` keyword argument. The period may be declared using the `period` argument or a cron expression (which requires the `croniter` library). Note that the `at` time should be in local time but if a callable is provided it must return a UTC time. If `croniter` is installed a `cron` expression can be provided using the `cron` argument.

Here is a simple example of a task scheduled at a fixed interval:

```python
import panel as pn
import datetime as dt
import asyncio

async def task():
    print(f'Task executed at: {dt.datetime.now()}')

pn.state.schedule_task('task', task, period='1s')
await asyncio.sleep(3)

pn.state.cancel_task('task')
```

Note that while both `async` and regular callbacks are supported, asynchronous callbacks are preferred if you are performing any I/O operations to avoid interfering with any running applications.

If you have the `croniter` library installed you may also provide a cron expression, e.g. the following will schedule a task to be repeated at 4:02 am every Monday and Friday:

```python
pn.state.schedule_task('task', task, cron='2 4 * * mon,fri')
```

## Related Resources
- See [crontab.guru](https://crontab.guru/) and the [`croniter` README](https://github.com/kiorky/croniter#introduction) to learn the special syntax supported by `croniter` and about cron expressions generally.
