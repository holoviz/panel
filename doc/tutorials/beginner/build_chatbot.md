# Build a Chat Bot

In this section we will build two basic *chat bots*. We will

- use the *easy to use*, *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.ipynb) to build a basic chat bot.
- use `async` to build a streaming and scalable chat bot.

:::{admonition} Note
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Build a Basic Chat Bot

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

def even_or_odd(contents, user, instance):
    return f"Your text contains **{len(contents)}** characters."

chat_bot = pn.chat.ChatInterface(callback=even_or_odd, max_height=500)
chat_bot.send("Ask me anything!", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering `How many characters are there in this text?` in the *text input* and click *Send*.

## Build a Streaming Chat Bot

Run the code below:

```{pyodide}
import panel as pn
from asyncio import sleep

pn.extension()


async def even_or_odd(contents, user, instance):
    response = f"Sure. You asked '{contents}'. Your text contains **{len(contents)}** characters."
    for index in range(len(response)):
        yield response[:index]
        await sleep(0.05)


chat_bot = pn.chat.ChatInterface(callback=even_or_odd, max_height=500)
chat_bot.send("Ask me anything!", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering `Can you please stream your response to this question?` in the *text input* and click *Send*.

:::{adminition} Note
If your chat app will have many users I recommend you to use `async` to make it fast and responsive. Most *Large Language Models* like chatGPT support this *out of the box*.

We won't be using `async` a lot in the basic tutorials. I just want you to know that Panels support for `async` can enable you to build high performing, scalable applications including chat bots.
:::

## Learn More

:::{admonition} Note

:::{admonition} Note
You can learn how to use the many features of the `ChatInterface` via its [*reference guide*](../../reference/chat/ChatInterface.html) which you can find in the [Chat Section](/reference/index.html#chat) of the [Component Gallery](../../reference/index.md).
:::

## Find Inspiration

:::{admonition} Note
I recommend you to check out [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/) one day. It provides lots of reference chat examples with accessible source code.
:::

[<img src="../../_static/images/panel-chat-examples.png" height="300"></img>](https://holoviz-topics.github.io/panel-chat-examples/)

## Recap

In this section we have

- used the *easy to use*, *high-level* [`ChatInterface`](../../reference/chat/ChatInterface.ipynb) to build a basic chat bot.
- used `async` to build a streaming and scalable chat bot.

## Resources

- [Chat Component Gallery](/reference/index.html#chat)
- [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/)
