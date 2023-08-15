# ChatBox

[Open this notebook in Jupyterlite](https://panelite.holoviz.org?path=/reference/widgets/ChatBox.ipynb) | [Download this notebook from GitHub (right-click to download).](https://raw.githubusercontent.com/holoviz/panel/main/examples/reference/widgets/ChatBox.ipynb)

---
```{pyodide}
import panel as pn
pn.extension()
```

The ``ChatBox`` widget shows conversations between users.

For more information about listening to widget events and laying out widgets refer to the [widgets user guide](../../user_guide/Widgets.ipynb). Alternatively you can learn how to build GUIs by declaring parameters independently of any specific widgets in the [param user guide](../../user_guide/Param.ipynb). To express interactivity entirely using Javascript without the need for a Python server take a look at the [links user guide](../../user_guide/Param.ipynb).

#### Parameters:

For layout and styling related parameters see the [customization user guide](../../user_guide/Customization.ipynb).

##### Core

* **``value``** (List[Dict[str, Any]]): List of messages, mapping user to message, e.g. `[{'You': 'Welcome!'}]`. The message can be any Python object that can be rendered by Panel
* **``primary_name``** (str): Name of the primary input user; the first key found in value will be used if unspecified
* **``allow_input``** (boolean): Whether to allow the primary user to interactively enter messages
* **``allow_likes``** (boolean): Whether to allow the primary user to interactively like messages
* **``ascending``** (boolean): Whether to display messages in ascending time order. If true, the latest messages and message_input_widgets will be at the bottom of the chat box. Otherwise, they will be at the top.
* **``message_icons``** (Dict[str, str]): Dictionary mapping name of users to their icons, e.g. `[{'You': 'path/to/icon.png'}]`
* **``message_colors``** (Dict[str, str]): Dictionary mapping name of users to their colors, e.g. `[{'You': 'red'}]`
* **``message_hue``** (int): Base hue of the message bubbles if `message_colors` is not specified for a user.
* **``message_input_widgets``** (List[pn.widgets.Widget]): List of widgets to use for message input. Multiple widgets will be nested under tabs.
* **``default_message_callable``** (pn.pane.PaneBase | pn.widgets.Widget) The type of Panel object to use for items in value if they are not already rendered as a Panel object; if None, uses the pn.panel function to render a displayable Panel object. If the item is not serializable, will fall back to pn.panel.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``name``** (str): The name to display at the top center of the chat box

___

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"You": "Hello!"},
        {"Machine": "Greetings!"},
        {"You": "Question for you..."},
        {"You": "What is the meaning of life?"},
        {"Machine": "I don't know. Do you know?"},
    ],
)

chat_box
```

``ChatBox.value`` parameter returns a list of dictionaries that map a user to their message.

Each dictionary should only contain a single key--two or more keys will raise an error.

```{pyodide}
chat_box.value
```

The individual `ChatRow`s that make up the `ChatBox` can be accessed through the `rows` property, which exposes the `rows`' parameters

```{pyodide}
rows = chat_box.rows

row = rows[0]
print(row.value, row.icon, row.liked)
```

You may bind the row's liked parameter to a callback.

```{pyodide}
pn.bind(lambda liked: print(liked), row.param.liked, watch=True)

row.liked = True
```

`ChatBox` can support more than two users and the primary input user can be separate from the existing users and also allows setting a `message_hue` to distinguish multiple users:

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": "Morning!"},
        {"Machine 2": "Afternoon~"},
        {"Machine 3": "Night zzz..."},
    ],
    message_hue=220,
    primary_name="You",
)

chat_box
```

User interactive input can be disabled.

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": "It's just us machines!"},
        {"Machine 2": "Beep boop beep!"},
    ],
    allow_input=False
)

chat_box
```

Messages can be appended or extended after instantiating.

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": "I'm machine 1!"},
        {"Machine 2": "I'm machine 2!"},
    ],
)

chat_box.append({"Machine 3": "How do you do fellow machines?"})
chat_box.extend([{"Machine 1": "Oh hi!"}, {"Machine 2": "Welcome!"}])

chat_box
```

The logs from the `ChatBox` can also be cleared for a clean slate.

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": "It's over!"},
        {"Machine 2": "Good bye."},
    ],
)
chat_box.clear()

chat_box
```

The messages do *not* only have to be strings; they can be Panel objects as well.

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": pn.widgets.TextInput(value="This is editable!")},
        {"Machine 2": pn.pane.Image("https://panel.holoviz.org/_images/logo_horizontal_light_theme.png", height=100)},
    ]
)

chat_box
```

String messages can be rendered within `pn.widgets.TextInput`.

```{pyodide}
chat_box = pn.widgets.ChatBox(
    value=[
        {"Machine 1": pn.widgets.Button(name="I won't be affected")},
        {"Machine 2": "I will be used as the value for the text input below!"},
        {"Machine 3": "Me too!"},
    ],
    default_message_callable=pn.widgets.TextInput,
)

chat_box
```

Instead of using names to indicate user, icons can be used instead.

```
import panel as pn

pn.extension(sizing_mode="stretch_width")

pn.widgets.ChatBox(
    value=[
        {"You": "Hello!"},
        {"Machine": "Hi there!"},
        {"GPT3.5": "Hey all!"},
        {"GPT4": "Greetings!"},
    ],
    message_icons={
        "You": "https://user-images.githubusercontent.com/42288570/246667322-33a2a320-9ea3-4e79-8fb8-fcb5b6eac9c0.png",
        "Machine": "https://user-images.githubusercontent.com/42288570/246671017-d3a26763-f7f5-4e8d-8933-cb69670f90a8.svg",
        "GPT3.5": "https://user-images.githubusercontent.com/42288570/246667325-ad4e3434-d173-4463-bb98-5c5d4a892b25.png",
        "GPT4": "https://user-images.githubusercontent.com/42288570/246667324-5cf26789-765f-4f76-a8bf-49309d2ae84f.png",
    },
    allow_names=False,
)
```

---
[Open this notebook in Jupyterlite](https://panelite.holoviz.org?path=/reference/widgets/ChatBox.ipynb) | [Download this notebook from GitHub (right-click to download).](https://raw.githubusercontent.com/holoviz/panel/main/examples/reference/widgets/ChatBox.ipynb)
