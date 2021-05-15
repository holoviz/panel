from panel.application import Application, User
from panel.template import FastGalleryTemplate

def _get_applications():
    philipp = User(
        uid = "Philipp Rudiger",
        name = "Philipp Rudiger",
        url = "https://github.com/philippjfr",
        avatar = "https://avatars.githubusercontent.com/u/1550771",
        tags = ["holoviz", "developer"],
        resources = {"twitter": "https://twitter.com/PhilippJFR"},
    )
    marc = User(
        uid="Marc Skov Madsen",
        name="Marc Skov Madsen",
        url="https://datamodelsanalytics.com",
        tags = ["analytics", "apps", "enthusiast"],
        avatar="https://avatars0.githubusercontent.com/u/42288570",
    )

    return [
        Application(
            name="Async Tasks",
            description="We show case how to start a background thread that updates a progressbar while the rest of the application remains responsive.",
            url="https://awesome-panel.org",
            thumbnail="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/async_tasks.png",
            resources = {
                "code": "https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/async_tasks/async_tasks.py",
                "youtube": "https://www.youtube.com/watch?v=Ohr29FJjBi0&t=791s",
                "documentation": "https://awesome-panel.readthedocs.org",
            },
            author=philipp,
            owner=marc,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Application(
            name="Bootstrap Dashboard",
            description="",
            url="https://awesome-panel.org",
            thumbnail="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/bootstrap_dashboard.png",
            resources= {
                "code": "https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/bootstrap_dashboard/main.py",
            },
            author=marc,
            owner=philipp,
            tags=[
                "Code",
                "App In Gallery",
            ],
        )
    ]

def test_can_construct():
    FastGalleryTemplate(
        site_name="Awesome Panel Gallery",
        site_url="https://awesome-panel.org",
        description="ABCD",
        resources=_get_applications(),
        target="_blank",
    )

def test_get_manual_test_app():
    return FastGalleryTemplate(
        site="Awesome Panel",
        site_url="https://awesome-panel.org",
        title="Gallery",
        # background_image_url="https://ih1.redbubble.net/image.875683605.8623/ur,mug_lifestyle,tall_portrait,750x1000.jpg",
        resources=_get_applications(),
        target="_blank",
        accent_base_color="green",
        footer="Made with &#x1f40d;, &#10084;&#65039; and <fast-anchor href='https://panel.holoviz.org' appearance='hypertext' target='_blank'>Panel</fast-anchor>."
    )


if __name__.startswith("bokeh"):
    test_get_manual_test_app().servable()
