from panel.templates.app.app import AppTemplate

def test_bootstrap_dashboard_view():
    app = AppTemplate(title="App Template Title", theme_name="bootstrap_dashboard")
    return app

if __name__.startswith("bk"):
    test_bootstrap_dashboard_view().servable()
