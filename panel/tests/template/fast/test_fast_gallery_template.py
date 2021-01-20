# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
# pylint: disable=line-too-long

from panel.template.fast.fast_gallery_template import (
    FastGalleryTemplate,
)
from panel.template.fast.models import Resource, Person


def get_applications():
    jochem_smit = Person(
        name="Jochem Smit",
        url="https://github.com/Jhsmit",
        avatar_url="https://avatars1.githubusercontent.com/u/7881506?s=400&u=bdf7b6635bf57e7022763ce3b002649fe80ef6a8&v=40",
    )
    marc_skov_madsen = Person(
        name="Marc Skov Madsen",
        url="https://datamodelsanalytics.com",
        avatar_url="https://avatars0.githubusercontent.com/u/42288570",
    )

    applications = [
        Resource(
            name="Async Tasks",
            description="We show case how to start a background thread that updates a progressbar while the rest of the application remains responsive.",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/async_tasks.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/async_tasks/async_tasks.py",
            youtube_url="https://www.youtube.com/watch?v=Ohr29FJjBi0&t=791s",
            documentation_url="https://awesome-panel.readthedocs.org",
            author=jochem_smit,
            owner=marc_skov_madsen,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Bootstrap Dashboard",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/bootstrap_dashboard.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/bootstrap_dashboard/main.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Custom Bokeh Model",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/custom_bokeh_model.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/custom_bokeh_model/custom.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Dashboard",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/dashboard.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/dashboard/dashboard.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="DataExplorer - Loading...",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/dataexplorer_loading.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/dataexplorer_loading/dataexplorer_loading.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="DE:TR: Object Detection",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/detr.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/detr/detr.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Image Classifier",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/image_classifier.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/image_classifier/image_classifier.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="JS Actions",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/js_actions.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/js_actions/js_actions.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Kickstarter Dashboard",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/kickstarter_dashboard.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/kickstarter_dashboard/main.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Owid Choropleth Map",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/owid_choropleth_map.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/owid_choropleth_map/main.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Pandas Profiling",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/pandas_profiling_app.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/pandas_profiling_app/pandas_profiling_app.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Param Reference Example",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/param_reference_example.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/param_reference_example/param_reference_example.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Yahoo Query",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/yahooquery_app.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/yahooquery_app/yahooquery_app.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Test Bootstrap Alerts",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_bootstrap_alerts.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_bootstrap_alerts.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Bootstrap Card",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_bootstrap_card.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_bootstrap_card.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Code",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_code.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_code.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test DataFrame",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_dataframe.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_dataframe.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Divider",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_divider.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_divider.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test ECharts",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_echarts.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_echarts.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test FontAwesome",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_fontawesome.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_fontawesome.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Headings",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_headings.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_headings.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Markdown",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_markdown.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_markdown.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Material Components",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_material_components.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_material.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Test Model Viewer",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_model_viewer.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_model_viewer.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Test Perspective Viewer",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_perspective.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_perspective.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
            ],
        ),
        Resource(
            name="Test Progress Extension",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_progress_ext.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_progress_ext.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Share Links",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_share_links.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_share_links.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Spinners",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_spinners.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_spinners.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
        Resource(
            name="Test Wired",
            description="",
            url="https://awesome-panel.org",
            thumbnail_url="https://github.com/MarcSkovMadsen/awesome-panel/raw/master/assets/images/thumbnails/test_wired.png",
            code_url="https://github.com/MarcSkovMadsen/awesome-panel/blob/master/application/pages/awesome_panel_express_tests/test_wired.py",
            author=marc_skov_madsen,
            owner=jochem_smit,
            tags=[
                "Code",
                "App In Gallery",
                "awesome_panel.express",
            ],
        ),
    ]
    return {app.name: app for app in applications}


def test_can_construct():
    FastGalleryTemplate(
        site="Awesome Panel Gallery",
        description="ABCD",
        items=get_applications(),
        target="_blank",
    )


def test_get_manual_test_app():
    return FastGalleryTemplate(
        site="Awesome Panel",
        name="Gallery",
        description="""The purpose of the Awesome Panel Gallery is to inspire and help you create awesome analytics apps in <fast-anchor href="https://panel.holoviz.org" target="_blank" appearance="hypertext">Panel</fast-anchor> using the tools you know and love.""",
        resources=list(get_applications().values()),
        target="_blank",
    )


if __name__.startswith("bokeh"):
    test_get_manual_test_app().servable()
