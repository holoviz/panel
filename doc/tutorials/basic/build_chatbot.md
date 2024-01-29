# Build a Chat Bot

In this tutorial we will build a streaming *chat bot*. We will first use the *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.ipynb) to build a basic chat bot. Then we will add streaming.

:::{admonition} Note
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Build a Basic Chat Bot

Run the code below:

```{pyodide}
import panel as pn
from time import sleep

pn.extension()

def get_response(contents, user, instance):
    if "turbine" in contents.lower():
        response = "A wind turbine converts wind energy into electricity."
    else:
        response = "Sorry, I don't know."
    sleep(1)
    return response

chat_bot = pn.chat.ChatInterface(callback=get_response, max_height=500)
chat_bot.send("Ask me what a wind turbine is", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering `What is a wind turbine?` in the *text input* and click *Send*.

:::{admonition}
The `callback` function `get_response` will receive `"What is a wind turbine?"` in the `contents` argument. Since `contents` contains the word *turbine*, the chat bot will return `WIND_TURBINE` as the `response`.
:::

## Add Streaming

We will now make the chat bot *stream* its response just like chatGPT does.

Run the code below:

```{pyodide}
import panel as pn
from time import sleep

pn.extension()

WIND_TURBINE = "A *wind turbine* is a device that converts the kinetic energy of wind into electrical energy."
DONT_KNOW = "Sorry. I don't know."

def get_response(contents, user, instance):
    if "turbine" in contents.lower():
        response = WIND_TURBINE
    else:
        response = DONT_KNOW
    message = ""
    for char in response:
        instance.stream(char, user="Assistant")
        sleep(0.10)

chat_bot = pn.chat.ChatInterface(callback=get_response, max_height=500)
chat_bot.send("Ask me anything!", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering `What is a wind turbine?` in the *text input* and click *Send*.

:::{admonition} Note
The chat app is now *streaming* because we `yield` the partial `response` instead of `return`ing the full `response`.
:::

:::{admonition} Note
To make the Streaming Chat Bot scale to many users you should use `async`. You will learn more about scaling applications and `async` in the [Intermediate Tutorials](../intermediate/index.md).
:::

## Learn More

:::{admonition} Note
You can learn more about the `ChatInterface` via its [*reference guide*](../../reference/chat/ChatInterface.html). You find the *reference guide* in the [Chat Section](/reference/index.html#chat) of the [Component Gallery](../../reference/index.md).
:::

[![Chat Section of Component Gallery](../../_static/images/build_chatbot_chat_section.png)](/reference/index.html#chat)

## Find Inspiration

:::{admonition} Note
If you want to build more advanced chat bots, [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/) for inspiration and starter templates.
:::

[<img src="../../_static/images/panel-chat-examples.png" height="300"></img>](https://holoviz-topics.github.io/panel-chat-examples/)

## Recap

In this section we have

- used the *easy to use*, *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.ipynb) to build a chat bot.

## Resources

- [Chat Component Gallery](/reference/index.html#chat)
- [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/)
