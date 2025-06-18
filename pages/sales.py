import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.io as pio

dash.register_page(__name__, path="/", name="Sales")

# ---------------------- Load Data ----------------------
def load_data():
    try:
        return pd.read_csv("data/erp_sales_data.csv", parse_dates=["invoice_date"])
    except:
        return pd.DataFrame()

# ---------------------- Layout ----------------------
layout = dbc.Container([
    html.H2("📊 Sales Dashboard", className="text-center mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("State"),
            dcc.Dropdown(id='state-dd', placeholder="Select State")
        ], md=4),

        dbc.Col([
            html.Label("City"),
            dcc.Dropdown(id='city-dd', placeholder="Select City")
        ], md=4),

        dbc.Col([
            html.Label("Customer"),
            dcc.Dropdown(id='cust-dd', placeholder="Select Customer")
        ], md=4),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            html.Label("T-code"),
            dcc.Dropdown(id='tcode-dd', placeholder="Select T-code")
        ], md=6),

        dbc.Col([
            html.Label("Location Code"),
            dcc.Dropdown(id='locn-dd', placeholder="Select Location Code")
        ], md=6),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Date Range"),
            dcc.DatePickerRange(id='date-picker')
        ], md=6),

        dbc.Col([
            html.Label("Metric"),
            dcc.Dropdown(
                id='metric-dd',
                options=[
                    {'label': 'Invoice Value', 'value': 'invoice_value'},
                    {'label': 'Quantity Sold', 'value': 'qty'},
                    {'label': 'Taxable Value', 'value': 'Taxable_Value'}
                ],
                value='invoice_value',
                clearable=False
            )
        ], md=6),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Chart Type"),
            dcc.RadioItems(
                id='chart-type',
                options=[
                    {'label': 'Bar', 'value': 'bar'},
                    {'label': 'Pie', 'value': 'pie'},
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Time Series', 'value': 'time'}
                ],
                value='bar',
                labelStyle={'display': 'inline-block', 'margin-right': '15px'}
            )
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Button("Export to Excel", id='export-excel-btn', className="btn btn-success me-3"),
            dcc.Download(id="download-excel"),
            html.Button("Export to PDF", id='export-pdf-btn', className="btn btn-danger"),
            dcc.Download(id="download-pdf")
        ])
    ], className="mb-4"),

    dcc.Graph(id='sales-graph', config={"displayModeBar": True}),
])

# ---------------------- Dropdown Callbacks ----------------------
@callback(Output('state-dd', 'options'), Input('sales-graph', 'id'))
def populate_states(_):
    df = load_data()
    return [{'label': i, 'value': i} for i in df['state_name'].dropna().unique()]

@callback(Output('city-dd', 'options'), Input('state-dd', 'value'))
def populate_cities(state):
    df = load_data()
    if state:
        return [{'label': i, 'value': i} for i in df[df['state_name'] == state]['city_name'].dropna().unique()]
    return []

@callback(Output('cust-dd', 'options'), Input('state-dd', 'value'), Input('city-dd', 'value'))
def populate_customers(state, city):
    df = load_data()
    if state and city:
        return [{'label': i, 'value': i} for i in df[(df['state_name'] == state) & (df['city_name'] == city)]['Party_Name'].dropna().unique()]
    return []

@callback(Output('tcode-dd', 'options'), Input('sales-graph', 'id'))
def populate_tcodes(_):
    df = load_data()
    return [{'label': i, 'value': i} for i in df['t_code'].dropna().unique()]

@callback(Output('locn-dd', 'options'), Input('sales-graph', 'id'))
def populate_locns(_):
    df = load_data()
    return [{'label': i, 'value': i} for i in df['location_code'].dropna().unique()]

# ---------------------- Filtering Function ----------------------
def filter_df(state, city, customer, tcode, locn, from_date, to_date):
    df = load_data()
    if state: df = df[df['state_name'] == state]
    if city: df = df[df['city_name'] == city]
    if customer: df = df[df['Party_Name'] == customer]
    if tcode: df = df[df['t_code'] == tcode]
    if locn: df = df[df['location_code'] == locn]
    if from_date and to_date:
        df = df[(df['invoice_date'] >= from_date) & (df['invoice_date'] <= to_date)]
    return df

# ---------------------- Chart Callback ----------------------
@callback(
    Output('sales-graph', 'figure'),
    Input('state-dd', 'value'),
    Input('city-dd', 'value'),
    Input('cust-dd', 'value'),
    Input('tcode-dd', 'value'),
    Input('locn-dd', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('chart-type', 'value'),
    Input('metric-dd', 'value')
)
def update_graph(state, city, customer, tcode, locn, from_date, to_date, chart_type, metric):
    df = filter_df(state, city, customer, tcode, locn, from_date, to_date)
    if df.empty:
        return px.bar(title="No data available")

    if chart_type == 'bar':
        summary = df.groupby("item_name")[metric].sum().reset_index()
        fig = px.bar(summary, x='item_name', y=metric, title=f"{metric} by Item")
    elif chart_type == 'pie':
        summary = df.groupby("item_name")[metric].sum().reset_index()
        fig = px.pie(summary, names='item_name', values=metric, title=f"{metric} Distribution")
    elif chart_type == 'line':
        summary = df.groupby("item_name")[metric].sum().reset_index()
        fig = px.line(summary, x='item_name', y=metric, title=f"{metric} by Item")
    else:
        fig = px.line(df, x='invoice_date', y=metric, color='item_name', title=f"{metric} Over Time")

    fig.update_layout(transition_duration=500)
    return fig

# ---------------------- Export Callbacks ----------------------
@callback(
    Output("download-excel", "data"),
    Input("export-excel-btn", "n_clicks"),
    State('state-dd', 'value'), State('city-dd', 'value'),
    State('cust-dd', 'value'), State('tcode-dd', 'value'),
    State('locn-dd', 'value'), State('date-picker', 'start_date'),
    State('date-picker', 'end_date'),
    prevent_initial_call=True
)
def export_excel(n_clicks, state, city, cust, tcode, locn, from_d, to_d):
    df = filter_df(state, city, cust, tcode, locn, from_d, to_d)
    filename = "Filtered_Sales_Data.xlsx"
    df.to_excel(filename, index=False)
    return dcc.send_file(filename)

@callback(
    Output("download-pdf", "data"),
    Input("export-pdf-btn", "n_clicks"),
    State('state-dd', 'value'), State('city-dd', 'value'),
    State('cust-dd', 'value'), State('tcode-dd', 'value'),
    State('locn-dd', 'value'), State('date-picker', 'start_date'),
    State('date-picker', 'end_date'), State('chart-type', 'value'),
    State('metric-dd', 'value'),
    prevent_initial_call=True
)
def export_pdf(n, s, c, p, t, l, fd, td, chart_type, metric):
    fig = update_graph(s, c, p, t, l, fd, td, chart_type, metric)
    filename = "chart_export.pdf"
    pio.write_image(fig, filename, format='pdf', width=1000, height=600)
    return dcc.send_file(filename)
