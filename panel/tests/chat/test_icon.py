from panel.chat.icon import ChatReactionIcons
from panel.pane.image import SVG


class TestChatReactionIcons:
    def test_init(self):
        icons = ChatReactionIcons(width=50, height=50)
        assert icons.options == {"favorite": "heart"}

        svg = icons._svgs[0]
        assert isinstance(svg, SVG)
        assert svg.alt_text == "favorite"
        assert not svg.encode
        assert svg.margin == 0

        svg_text = svg.object
        assert 'width="50px"' in svg_text
        assert 'height="50px"' in svg_text
        assert 'alt="favorite"' in svg_text
        assert "icon-tabler-heart" in svg_text

        assert icons._reactions == ["favorite"]

    def test_options(self):
        icons = ChatReactionIcons(options={"favorite": "heart", "love": "heart"})
        assert icons.options == {"favorite": "heart", "love": "heart"}
        assert len(icons._svgs) == 2

        svg = icons._svgs[0]
        assert svg.alt_text == "favorite"

        svg = icons._svgs[1]
        assert svg.alt_text == "love"

    def test_value(self):
        icons = ChatReactionIcons(value=["favorite"])
        assert icons.value == ["favorite"]

        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-heart-filled" in svg_text

    def test_active_icons(self):
        icons = ChatReactionIcons(
            options={"like": "heart"},
            active_icons={"like": "help-square"},
            value=["like"],
        )
        assert icons.options == {"like": "heart"}

        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-help-square" in svg_text

        icons.value = []
        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-heart" in svg_text
