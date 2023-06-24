# Use Asynchronous Processing

When using Python you can use async callbacks wherever you would ordinarily use a regular synchronous function. For instance you can use `pn.bind` on an async function:

```{pyodide}
import panel as pn

widget = pn.widgets.IntSlider(start=0, end=10)

async def get_img(index):
    url = f"https://picsum.photos/800/300?image={index}"
    if pn.state._is_pyodide:
        from pyodide.http import pyfetch
        return pn.pane.JPG(await (await pyfetch(url)).bytes())

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return pn.pane.JPG(await resp.read())

pn.Column(widget, pn.bind(get_img, widget))
```

In this example Panel will invoke the function and update the output when the function returns while leaving the process unblocked for the duration of the `aiohttp` request.

Similarly you can attach asynchronous callbacks using `.param.watch`:

```{pyodide}
widget = pn.widgets.IntSlider(start=0, end=10)

image = pn.pane.JPG()

async def update_img(event):
    url = f"https://picsum.photos/800/300?image={event.new}"
    if pn.state._is_pyodide:
        from pyodide.http import pyfetch
        image.object = await (await pyfetch(url)).bytes()
        return

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            image.object = await resp.read()

widget.param.watch(update_img, 'value')
widget.param.trigger('value')

pn.Column(widget, image)
```

In this example Param will await the asynchronous function and the image will be updated when the request completes.
