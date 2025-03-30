from panel.chat.icon import ChatReactionIcons


class TestChatReactionIcons:
    def test_init_default(self):
        icons = ChatReactionIcons(width=50, height=50)
        assert icons.options == {"favorite": "heart"}
        assert "favorite" in icons._rendered_icons
        assert icons._rendered_icons["favorite"].icon == "heart"
        assert icons._rendered_icons["favorite"].active_icon == ""
        assert len(icons._composite) == 1

    def test_options(self):
        icons = ChatReactionIcons(options={"like": "thumb-up", "dislike": "thumb-down"})
        assert icons.options == {"like": "thumb-up", "dislike": "thumb-down"}
        assert "like" in icons._rendered_icons
        assert icons._rendered_icons["like"].icon == "thumb-up"
        assert icons._rendered_icons["like"].active_icon == ""
        assert "dislike" in icons._rendered_icons
        assert icons._rendered_icons["dislike"].icon == "thumb-down"
        assert icons._rendered_icons["dislike"].active_icon == ""
        assert len(icons._composite) == 1
        assert len(icons._composite[0]) == 2

        icons.options = {"favorite": "heart"}
        assert icons.options == {"favorite": "heart"}
        assert "favorite" in icons._rendered_icons
        assert icons._rendered_icons["favorite"].icon == "heart"
        assert icons._rendered_icons["favorite"].active_icon == ""
        assert len(icons._composite) == 1
        assert len(icons._composite[0]) == 1

    def test_value(self):
        icons = ChatReactionIcons(
            options={"like": "thumb-up", "dislike": "thumb-down"}, value=["like"]
        )
        assert icons.value == ["like"]
        assert icons._rendered_icons["like"].value is True
        assert icons._rendered_icons["dislike"].value is False

        icons.value = ["dislike"]
        assert icons.value == ["dislike"]
        assert icons._rendered_icons["like"].value is False
        assert icons._rendered_icons["dislike"].value is True

    def test_active_icons(self):
        icons = ChatReactionIcons(
            options={"like": "thumb-up"},
            active_icons={"like": "thumb-down"},
            value=["like"],
        )
        assert icons.active_icons == {"like": "thumb-down"}
        assert icons._rendered_icons["like"].active_icon == "thumb-down"
        assert len(icons._composite) == 1

        icons.active_icons = {"like": "heart"}
        assert icons.active_icons == {"like": "heart"}
        assert icons._rendered_icons["like"].active_icon == "heart"
        assert len(icons._composite) == 1
