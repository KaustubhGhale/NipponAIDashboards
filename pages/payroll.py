# pages/payroll.py
import dash
from dash import html

dash.register_page(__name__, path="/payroll", name="Payroll")

layout = html.Div([
    html.H2("Payroll Dashboard"),
    html.P("This module will include salary analysis, headcount tracking, leave trends, etc."),
    html.P("Work in progress...")
])
