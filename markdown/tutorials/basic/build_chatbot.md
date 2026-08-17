# Build a Chat Bot

In this tutorial, we will build a streaming *chat bot*. We will first use the *high-level* `ChatInterface` to build a basic chat bot. Then we will add streaming.

## Build a Basic Chat Bot

Run the code below:

```python
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

## Add Streaming

We will now make the chat bot *stream* its response just like ChatGPT does.

Run the code below:

```python
import panel as pn
from time import sleep

pn.extension()

def get_response(contents, user, instance):
    if "turbine" in contents.lower():
        response = "A wind turbine converts wind energy into electricity."
    else:
        response = "Sorry, I don't know."
    for index in range(len(response)):
        yield response[0:index+1]
        sleep(0.03) # to simulate slowish response

chat_bot = pn.chat.ChatInterface(callback=get_response, max_height=500)
chat_bot.send("Ask me anything!", user="Assistant", respond=False)
chat_bot.servable()
```

Try entering `What is a wind turbine?` in the *text input* and click *Send*.

## Learn More

We can learn more about the `ChatInterface` via its [*reference guide*](../../reference/chat/ChatInterface.md). We find the *reference guide* in the [Chat Section](../../reference/index.rst#chat) of the [Component Gallery](../../reference/index.rst).

## Find Inspiration

We can find more inspiration and starter templates at [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/).

:height: 300px
:target: https://holoviz-topics.github.io/panel-chat-examples/
:::

## Recap

In this section, we have used the *easy to use*, *high-level* `ChatInterface` to build a streaming chat bot.

## Resources

- [Chat Component Gallery](../../reference/index.rst#chat)
- [Panel-Chat-Examples](https://holoviz-topics.github.io/panel-chat-examples/)
