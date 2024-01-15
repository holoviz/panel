import panel as pn

set_price = 88

alert = pn.pane.Alert(alert_type="warning", visible=False)
item_image = pn.pane.Image("https://panel.holoviz.org/_static/logo.png")
price_shown = pn.pane.Markdown(object=f"## Price: ${set_price}")
layout = pn.Column(alert, item_image, price_shown)

promo_code = pn.state.session_args.get('promo_code', [b""])[0].decode()
if promo_code and promo_code.endswith("OFF"):
    discount = float(promo_code.replace("OFF", "")) / 100
    new_price = set_price * discount
    price_shown.object = f"## Price: $~~{set_price}~~ <font color='red'>Now ${new_price}</font>"
elif promo_code:
    alert.visible = True
    alert.object = f"The promo code provided, {promo_code!r}, is invalid."

layout.servable()
