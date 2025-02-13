import datetime
import os
import pathlib

from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from panel import Param, bind
from panel.chat.icon import ChatReactionIcons
from panel.chat.message import ChatMessage, _FileInputMessage
from panel.layout import Column, Row
from panel.pane.image import PNG, SVG, Image
from panel.pane.markup import HTML, DataFrame, Markdown
from panel.pane.media import Audio
from panel.tests.util import mpl_available, mpl_figure
from panel.widgets.button import Button
from panel.widgets.input import (
    FileInput, IntInput, TextAreaInput, TextInput,
)

ASSETS = pathlib.Path(__file__).parent.parent / 'pane' / 'assets'

PNG_FILE = 'https://assets.holoviz.org/panel/samples/png_sample.png'
SVG_FILE = 'https://assets.holoviz.org/panel/samples/svg_sample.svg'

class TestChatMessage:
    def test_layout(self):
        message = ChatMessage(object="ABC", header_objects=["Header Test", "Header 2"], footer_objects=["Footer Test", "Footer 2"])
        columns = message._composite.objects
        assert len(columns) == 2

        avatar_pane = columns[0][0]
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "🧑"

        meta_row = columns[1][0]
        user_pane = meta_row[0]
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "User"

        header_row = columns[1][1]
        assert isinstance(header_row[0], Markdown)
        assert header_row[0].object == "Header Test"
        assert isinstance(header_row[1], Markdown)
        assert header_row[1].object == "Header 2"

        center_row = columns[1][2]
        assert isinstance(center_row, Row)

        object_pane = center_row[0]
        assert isinstance(object_pane.object, Markdown)
        assert object_pane.object.object == "ABC"

        icons = columns[1][4][2]
        assert isinstance(icons, ChatReactionIcons)

        footer_col = columns[1][3]
        assert isinstance(footer_col, Column)

        assert isinstance(footer_col[0], Markdown)
        assert footer_col[0].object == "Footer Test"
        assert isinstance(footer_col[1], Markdown)
        assert footer_col[1].object == "Footer 2"

        timestamp_pane = columns[1][5][0]
        assert isinstance(timestamp_pane, HTML)

    def test_reactions_dynamic(self):
        message = ChatMessage("hi", reactions=["favorite"])
        assert message.reaction_icons.value == ["favorite"]

        message.reactions = ["thumbs-up"]
        assert message.reaction_icons.value == ["thumbs-up"]

    def test_reaction_icons_dynamic(self):
        message = ChatMessage("hi", reaction_icons={"favorite": "heart"})
        assert message.reaction_icons.options == {"favorite": "heart"}

        message.reaction_icons = ChatReactionIcons(options={"like": "thumb-up"})
        assert message._icons_row[-1] == message.reaction_icons

        message.reaction_icons = ChatReactionIcons(options={})

        message = ChatMessage("hi", reaction_icons={})

    def test_reactions_link(self):
        # on init
        message = ChatMessage(reactions=["favorite"])
        assert message.reaction_icons.value == ["favorite"]

        # on change in message
        message.reactions = []
        assert message.reaction_icons.value == []

        # on change in reaction_icons
        message.reactions = ["favorite"]
        assert message.reaction_icons.value == ["favorite"]

    def test_reaction_icons_input_dict(self):
        message = ChatMessage(reaction_icons={"favorite": "heart"})
        assert isinstance(message.reaction_icons, ChatReactionIcons)
        assert message.reaction_icons.options == {"favorite": "heart"}

    def test_update_avatar(self):
        message = ChatMessage(avatar="A")
        columns = message._composite.objects
        avatar_pane = columns[0][0]
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "A"

        message.avatar = "B"
        avatar_pane = columns[0][0]
        assert avatar_pane.object == "B"

        message.avatar = "❤️"
        avatar_pane = columns[0][0]
        assert avatar_pane.object == "❤️"

        message.avatar = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        avatar_pane = columns[0][0]
        assert isinstance(avatar_pane, Image)
        assert (
            avatar_pane.object
            == "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        )

        message.show_avatar = False
        avatar_layout = columns[0]
        assert not avatar_layout.visible

        message.avatar = SVG(
            "https://tabler-icons.io/static/tabler-icons/icons/user.svg"
        )
        avatar_pane = columns[0][0]
        assert isinstance(avatar_pane, SVG)

    def test_update_user(self):
        message = ChatMessage(user="Andrew")
        columns = message._composite.objects
        user_pane = columns[1][0][0]
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "Andrew"

        message.user = "August"
        user_pane = columns[1][0][0]
        assert user_pane.object == "August"

        message.show_user = False
        user_pane = columns[1][0][0]
        assert not user_pane.visible

    def test_update_object(self):
        message = ChatMessage(object="Test")
        columns = message._composite.objects
        object_pane = columns[1][2][0].object
        assert isinstance(object_pane, Markdown)
        assert object_pane.object == "Test"

        message.object = TextInput(value="Also testing...")
        object_pane = columns[1][2][0].object
        assert isinstance(object_pane, TextInput)
        assert object_pane.value == "Also testing..."

        message.object = _FileInputMessage(
            contents=b"I am a file", file_name="test.txt", mime_type="text/plain"
        )
        object_pane = columns[1][2][0].object
        assert isinstance(object_pane, Markdown)
        assert object_pane.object == "I am a file"

    @pytest.mark.flaky(reruns=3, reason="Minute can change during test run")
    def test_update_timestamp(self):
        message = ChatMessage()
        columns = message._composite.objects
        timestamp_pane = columns[1][5][0]
        assert isinstance(timestamp_pane, HTML)
        dt_str = datetime.datetime.now().strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        message = ChatMessage(timestamp_tz="UTC")
        columns = message._composite.objects
        timestamp_pane = columns[1][5][0]
        assert isinstance(timestamp_pane, HTML)
        dt_str = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        message = ChatMessage(timestamp_tz="US/Pacific")
        columns = message._composite.objects
        timestamp_pane = columns[1][5][0]
        assert isinstance(timestamp_pane, HTML)
        dt_str = datetime.datetime.now(tz=ZoneInfo("US/Pacific")).strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        special_dt = datetime.datetime(2023, 6, 24, 15)
        message.timestamp = special_dt
        timestamp_pane = columns[1][5][0]
        dt_str = special_dt.strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        mm_dd_yyyy = "%b %d, %Y"
        message.timestamp_format = mm_dd_yyyy
        timestamp_pane = columns[1][5][0]
        dt_str = special_dt.strftime(mm_dd_yyyy)
        assert timestamp_pane.object == dt_str

        message.show_timestamp = False
        timestamp_pane = columns[1][5][0]
        assert not timestamp_pane.visible

    def test_does_not_turn_widget_into_str(self):
        button = Button()
        message = ChatMessage(object=button)
        assert message.object == button

    def test_include_stylesheets_inplace_on_layouts(self):
        message = ChatMessage(
            Row(Markdown("Hello", css_classes=["message"]), stylesheets=["row.css"]),
            stylesheets=["chat.css"]
        )
        assert message.stylesheets == ["chat.css"]
        assert message.object.stylesheets == message._stylesheets + ["chat.css", "row.css"]

        # # nested
        message = ChatMessage(
            Row(
                Row(Markdown("Hello", css_classes=["message"]), stylesheets=["row2.css"]),
                stylesheets=["row.css"]
            ),
            stylesheets=["chat.css"]
        )
        assert message.object.stylesheets == ChatMessage._stylesheets + ["chat.css", "row.css"]
        assert message.object.objects[0].stylesheets == ChatMessage._stylesheets + ["chat.css", "row2.css"]

    def test_include_message_css_class_inplace(self):
        # markdown
        message = ChatMessage(object=Markdown("hello"))
        assert message.object.css_classes == ["message"]

        # custom css class; no message appended
        message = ChatMessage(object=Markdown("hello", css_classes=["custom"]))
        assert message.object.css_classes == ["custom"]

        # nested in layout; message appended
        message = ChatMessage(object=Row(Markdown("hello")))
        assert message.object.objects[0].css_classes == ["message"]

        # nested in layout as a string; message appended
        message = ChatMessage(object=Row("hello"))
        assert message.object.objects[0].css_classes == ["message"]

        # nested in layout with custom css; no message appended
        message = ChatMessage(object=Row(Markdown("hello", css_classes=["custom"])))
        assert message.object.objects[0].css_classes == ["custom"]

    @mpl_available
    async def test_can_display_any_python_object_that_panel_can_display(self):
        # For example matplotlib figures
        ChatMessage(object=mpl_figure())

        # For example async functions
        async def async_func():
            return "hello"

        ChatMessage(object=async_func)

        # For example async generators
        async def async_generator():
            yield "hello"
            yield "world"

        ChatMessage(object=async_generator)

    def test_can_use_pn_param_without_raising_exceptions(self):
        message = ChatMessage()
        Param(message)

    def test_bind_reactions(self):
        def callback(reactions):
            message.object = " ".join(reactions)

        message = ChatMessage(object="Hello")
        bind(callback, message.param.reactions, watch=True)
        message.reactions = ["favorite"]
        assert message.object == "favorite"

    def test_show_reaction_icons(self):
        message = ChatMessage()
        assert message.reaction_icons.visible
        message.show_reaction_icons = False
        assert not message.reaction_icons.visible

    def test_default_avatars(self):
        assert isinstance(ChatMessage.default_avatars, dict)
        assert (
            ChatMessage(user="Assistant").avatar == ChatMessage(user="assistant").avatar
        )
        assert ChatMessage(object="Hello", user="NoDefaultUserAvatar").avatar == ""

    def test_default_avatars_depends_on_user(self):
        ChatMessage.default_avatars["test1"] = "1"
        ChatMessage.default_avatars["test2"] = "2"

        message = ChatMessage(object="Hello", user="test1")
        assert message.avatar == "1"

        message.user = "test2"
        assert message.avatar == "2"

    def test_default_avatars_can_be_updated_but_the_original_stays(self):
        assert ChatMessage(user="Assistant").avatar == "🤖"
        ChatMessage.default_avatars["assistant"] = "👨"
        assert ChatMessage(user="Assistant").avatar == "👨"

        assert ChatMessage(user="System").avatar == "⚙️"

    def test_chat_copy_icon(self):
        message = ChatMessage(object="testing")
        assert message.chat_copy_icon.visible
        assert message.chat_copy_icon.value == "testing"

    @pytest.mark.parametrize("widget", [TextInput, TextAreaInput])
    def test_chat_copy_icon_text_widget(self, widget):
        message = ChatMessage(object=widget(value="testing"))
        assert message.chat_copy_icon.visible
        assert message.chat_copy_icon.value == "testing"

    def test_chat_copy_icon_disabled(self):
        message = ChatMessage(object="testing", show_copy_icon=False)
        assert not message.chat_copy_icon.visible
        assert not message.chat_copy_icon.value

    @pytest.mark.parametrize("component", [Column, FileInput])
    def test_chat_copy_icon_not_string(self, component):
        message = ChatMessage(object=component())
        assert not message.chat_copy_icon.visible
        assert not message.chat_copy_icon.value

    def test_serialize_text_prefix_with_viewable_type(self):
        message = ChatMessage(Markdown("string"))
        assert message.serialize() == "Markdown='string'"

    def test_serialize_text_prefix_with_viewable_name(self):
        message = ChatMessage(Markdown("string", name="Important Name"))
        assert message.serialize() == "Important Name='string'"

    def test_serialize_text_prefix_with_viewable_and_container_type(self):
        message = ChatMessage(Column(Markdown("string")))
        assert message.serialize() == "Column(Markdown='string')"

    def test_serialize_text_prefix_with_viewable_and_container_name(self):
        message = ChatMessage(
            Column(Markdown("string", name="Important Name"), name="Test Col")
        )
        assert message.serialize() == "Test Col(Important Name='string')"

    def test_serialize_multiple_objects_in_container(self):
        message = ChatMessage(
            Column(Markdown("markdown"), HTML("html"))
        )
        assert message.serialize() == "Column(\n    Markdown='markdown',\n    HTML='html'\n)"

    def test_serialize_nested_objects_in_container(self):
        message = ChatMessage(
            Row(
                Column(IntInput(name='int val')),
                Column(Markdown("markdown"), HTML("html"))
            )
        )
        assert message.serialize() == "Row(\n    Column(int val=0),\n    Column(\n        Markdown='markdown',\n        HTML='html'\n    )\n)"  # noqa

    def test_serialize_png_url(self):
        message = ChatMessage(PNG(PNG_FILE))
        assert message.serialize() == "PNG='https://assets.holoviz.org/panel/samples/png_sample.png'"

    @pytest.mark.internet
    def test_serialize_svg_embed(self):
        svg = SVG(SVG_FILE, embed=True, alt_text="abc")
        with BytesIO(svg._data(SVG_FILE)) as buf:
            message = ChatMessage(SVG(buf))
        assert message.serialize() == "SVG"

    @pytest.mark.skipif(os.name == 'nt', reason="Wrong Windows path")
    def test_serialize_audio(self):
        message = ChatMessage(Audio(str(ASSETS / 'mp3.mp3')))
        assert message.serialize() == f"Audio='{ASSETS / 'mp3.mp3'}'"

    def test_serialize_dataframe(self):
        message = ChatMessage(DataFrame(pd.DataFrame({'a': [1, 2, 3]})))
        assert message.serialize() == "DataFrame=   a\n0  1\n1  2\n2  3"

    def test_repr(self):
        message = ChatMessage(object="Hello", user="User", avatar="A", reactions=["favorite"])
        assert repr(message) == "ChatMessage(object='Hello', user='User', reactions=['favorite'])"

    def test_repr_dataframe(self):
        message = ChatMessage(pd.DataFrame({'a': [1, 2, 3]}), avatar="D")
        assert repr(message) == "ChatMessage(object=   a\n0  1\n1  2\n2  3, user='User', reactions=[])"
