# app.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, callback
from flask import Flask
import os
import config_store

external_stylesheets = [dbc.themes.MINTY, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, use_pages=True, external_stylesheets=external_stylesheets)
app.title = "ERP Multi-Module Dashboard"

# Layout with navigation flow control
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    
    html.Div(id="navbar-container"),
    html.Div(id="page-content")
], fluid=True)

@callback(
    [Output("navbar-container", "children"), Output("page-content", "children")],
    Input("url", "pathname")
)
def display_page(pathname):
    # Step 1: If no config, always redirect to config page
    if not config_store.db_config and pathname not in ["/config", "/"]:
        return [], dcc.Location(pathname="/config", id="redirect-to-config")
    
    # Step 2: Home page logic - redirect to config page
    if pathname == "/":
        return [], dcc.Location(pathname="/config", id="redirect-to-config")
    
    # Step 3: For config and data-fetching pages, show only page content without navbar
    if pathname in ["/config", "/data-fetching"]:
        return [], dash.page_container
    
    # Step 4: Show navbar for dashboard pages (sales, inventory, payroll)
    navbar = [
        html.H1("ERP Multi-Module Dashboard", className="display-4 text-center my-4"),
        dbc.Nav([
            dbc.NavLink("Sales", href="/sales", active="exact"),
            dbc.NavLink("Inventory", href="/inventory", active="exact"),
            dbc.NavLink("Payroll", href="/payroll", active="exact")
        ], pills=True, justified=True, className="mb-4")
    ]
    
    return navbar, dash.page_container

app.config.suppress_callback_exceptions = True

# Run app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))