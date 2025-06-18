# pages/home.py
import dash
from dash import html, dcc, callback, Output, Input
import config_store

dash.register_page(__name__, path="/", name="Home")

layout = html.Div(id="home-redirect")

@callback(Output("home-redirect", "children"), Input("home-redirect", "id"))
def redirect_logic(_):
    if not config_store.db_config:
        return dcc.Location(pathname="/config", id="redirect-to-config")
    return dcc.Location(pathname="/sales", id="redirect-to-sales")