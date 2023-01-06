# Set up Manual Threading

Enabling threading in Panel like we saw in the [automatic threading guide](threading) is a simple way to achieve concurrency, however sometimes we need more control. Below we will demonstrate an example of a `Thread` which we start in the background to process items we put in a queue for processing. We simulate the processing with a `time.sleep` but it could be any long-running computation. The `threading.Condition` allows us to manipulate the global shared `queue`.

```python
import time
import threading

c = threading.Condition()

button = pn.widgets.Button(name='Click to launch')
text = pn.widgets.StaticText()

queue = []

def callback():
    global queue
    while True:
        c.acquire()
        for i, event in enumerate(queue):
            text.value = f'Processing item {i+1} of {len(queue)} items in queue.'
            ... # Do something with the event
            time.sleep(2)
        queue.clear()
        text.value = "Queue empty"
        c.release()
        time.sleep(1)

thread = threading.Thread(target=callback)
thread.start()
```

Now we will create a callback that puts new items for processing on the queue when a button is clicked:

```python
def on_click(event):
    queue.append(event)

button.on_click(on_click)

pn.Row(button, text).servable()
```

Since the processing happens on a separate thread the application itself can still remain responsive to further user input (such as putting new items on the queue).
