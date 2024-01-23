# Build a Chat Bot

In this section you will learn to build a basic *chat bot*:

- Its simple to develop a *chat bot* with the *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.html).
- Learn more about Panels Chat Features in the [Chat Section](../../reference/index.md#layouts) of the [Component Gallery](../../reference/index.md).
- Find reference chat implementations at [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/).

:::{admonition} Note
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Build the ChatBot

Run the code below:

```{pyodide}
import panel as pn
from time import sleep

pn.extension()

def even_or_odd(contents, user, instance):
    sleep(1)
    return f"Your text contains **{len(contents)}** characters."

chat_bot = pn.chat.ChatInterface(callback=even_or_odd, max_height=500)
chat_bot.send("Ask me anything!", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering the text `How many characters are there in this text?` in the *text input* and click *Send*.

:::{pyodide}
You can learn how to use the many features of the `ChatInterface` via its [*reference guide*](../../reference/chat/ChatInterface.html)
:::

## Find Inspiration

:::{admonition} Note
[Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/) provides lots of reference chat examples with accessible source code.
:::

Click [this link](https://holoviz-topics.github.io/panel-chat-examples/) and spend a couple of minutes browsing through the examples of [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/) to get inspired.

[<img src="../../_static/images/panel-chat-examples.png" height="300"></img>](https://holoviz-topics.github.io/panel-chat-examples/)

## Recap

In this section you have learned:

- Its simple to develop a *chat bot* with the *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.html).
- Learn more about Panels Chat Features in the [Chat Section](../../reference/index.md#layouts) of the [Component Gallery](../../reference/index.md).
- Find reference chat implementations at [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/).

## Resources

- [Chat Component Gallery](https://panel.holoviz.org/reference/index.html#chat)
- [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/)
