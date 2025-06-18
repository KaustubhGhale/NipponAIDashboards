# pages/inventory.py
import dash
from dash import html

dash.register_page(__name__, path="/inventory", name="Inventory")

layout = html.Div([
    html.H2("Inventory Dashboard"),
    html.P("This module will provide insights on stock levels, reorder alerts, inventory aging, etc."),
    html.P("Work in progress...")
])
