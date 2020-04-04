from panel.themes.theme_builder.theme import ThemeForeground, ThemeBackground, THEMES

def test_themes():
    for theme in THEMES.values():
        foreground, background = theme
        assert isinstance(foreground, ThemeForeground)
        assert isinstance(background, ThemeBackground)