from panel.templates.app.app import AppTemplate

def test_angular_material_purple_green_view():
    app = AppTemplate(title="App Template Title", theme_name="angular_material_purple_green")
    return app


def test_bootstrap_dashboard_view():
    app = AppTemplate(title="App Template Title", theme_name="bootstrap_dashboard")
    return app

if __name__.startswith("bk"):
    # test_bootstrap_dashboard_view().servable()
    test_angular_material_purple_green_view().servable()
