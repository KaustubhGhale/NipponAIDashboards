# pages/sales.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

dash.register_page(__name__, path="/sales", name="Sales")

# Load CSV
def load_data():
    try:
        data_path = os.path.join("data", "erp_sales_data.csv")
        df = pd.read_csv(data_path)
        # Ensure required columns exist, fill with NaN if missing
        required_columns = ['state_name', 'city_name', 'party_name', 'invoice_date', 'item_name', 'invoice_value']
        for col in required_columns:
            if col not in df.columns:
                df[col] = pd.NA
        # Parse invoice_date if it exists and is not all NA
        if 'invoice_date' in df.columns and not df['invoice_date'].isna().all():
            df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['state_name', 'city_name', 'party_name', 'invoice_date', 'item_name', 'invoice_value'])

# Shared filter logic
def filter_df(state, city, customer, from_date, to_date):
    df = load_data()
    if df.empty:
        return df
    if state and 'state_name' in df.columns:
        df = df[df['state_name'] == state]
    if city and 'city_name' in df.columns:
        df = df[df['city_name'] == city]
    if customer and 'party_name' in df.columns:
        df = df[df['party_name'] == customer]
    if from_date and to_date and 'invoice_date' in df.columns:
        df = df[(df['invoice_date'] >= from_date) & (df['invoice_date'] <= to_date)]
    return df

# Page layout
layout = dbc.Container([
    html.H2("📊 Sales Dashboard", className="my-3"),

    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='state-dd', placeholder="Select State"), md=4),
                dbc.Col(dcc.Dropdown(id='city-dd', placeholder="Select City", disabled=True), md=4),
                dbc.Col(dcc.Dropdown(id='cust-dd', placeholder="Select Customer", disabled=True), md=4),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(dcc.DatePickerRange(
                    id='date-picker',
                    start_date_placeholder_text="Select Start Date",
                    end_date_placeholder_text="Select End Date"
                ), md=6),
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
                        inline=True
                    )
                ], md=3),
                dbc.Col([
                    dbc.Button("Export to Excel", id='export-excel-btn', color="primary", className="me-2"),
                    dbc.Button("Export to PDF", id='export-pdf-btn', color="secondary")
                ], md=3, className="text-end")
            ])
        ])
    ], className="mb-4"),

    dcc.Download(id="download-excel"),
    dcc.Download(id="download-pdf"),

    dcc.Graph(id='sales-graph')
], fluid=True)

# ----------------- Dropdown Callbacks --------------------

@callback(
    [Output('state-dd', 'options'), Output('state-dd', 'disabled')],
    Input('sales-graph', 'id')
)
def populate_states(_):
    df = load_data()
    if 'state_name' in df.columns:
        return [{'label': i, 'value': i} for i in df['state_name'].dropna().unique()], False
    return [], False

@callback(
    [Output('city-dd', 'options'), Output('city-dd', 'disabled')],
    Input('state-dd', 'value')
)
def populate_cities(state):
    df = load_data()
    if state and 'state_name' in df.columns and 'city_name' in df.columns:
        cities = [{'label': i, 'value': i} for i in df[df['state_name'] == state]['city_name'].dropna().unique()]
        return cities, False
    return [], True

@callback(
    [Output('cust-dd', 'options'), Output('cust-dd', 'disabled')],
    [Input('state-dd', 'value'), Input('city-dd', 'value')]
)
def populate_customers(state, city):
    df = load_data()
    if state and city and 'state_name' in df.columns and 'city_name' in df.columns and 'party_name' in df.columns:
        customers = [{'label': i, 'value': i} for i in df[(df['state_name'] == state) & (df['city_name'] == city)]['party_name'].dropna().unique()]
        return customers, False
    return [], True

# ----------------- Graph Callback --------------------

@callback(
    Output('sales-graph', 'figure'),
    Input('state-dd', 'value'),
    Input('city-dd', 'value'),
    Input('cust-dd', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('chart-type', 'value')
)
def update_graph(state, city, customer, from_date, to_date, chart_type):
    df = filter_df(state, city, customer, from_date, to_date)
    if df.empty or 'item_name' not in df.columns or 'invoice_value' not in df.columns:
        return {
            'data': [],
            'layout': {
                'title': {'text': 'No data available', 'x': 0.5, 'xanchor': 'center'},
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'No data to display',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }

    if chart_type == 'bar':
        summary = df.groupby("item_name")["invoice_value"].sum().reset_index()
        fig = px.bar(summary, x='item_name', y='invoice_value', title="Sales Amount by Item",
                     labels={'item_name': 'Item Name', 'invoice_value': 'Sales Amount'})
    elif chart_type == 'pie':
        summary = df.groupby("item_name")["invoice_value"].sum().reset_index()
        fig = px.pie(summary, names='item_name', values='invoice_value', title="Sales Amount by Item")
    elif chart_type == 'line':
        summary = df.groupby("item_name")["invoice_value"].sum().reset_index()
        fig = px.line(summary, x='item_name', y='invoice_value', title="Sales Amount by Item",
                      labels={'item_name': 'Item Name', 'invoice_value': 'Sales Amount'})
    else:
        if 'invoice_date' in df.columns and not df['invoice_date'].isna().all():
            fig = px.line(df, x='invoice_date', y='invoice_value', color='item_name', title="Sales Amount Over Time",
                         labels={'invoice_date': 'Date', 'invoice_value': 'Sales Amount', 'item_name': 'Item Name'})
        else:
            return {
                'data': [],
                'layout': {
                    'title': {'text': 'No date data available', 'x': 0.5, 'xanchor': 'center'},
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'annotations': [{
                        'text': 'No date data to display',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 16}
                    }]
                }
            }

    fig.update_layout(transition_duration=500)
    return fig

# ----------------- Export Callbacks --------------------

@callback(
    Output("download-excel", "data"),
    Input("export-excel-btn", "n_clicks"),
    State('state-dd', 'value'),
    State('city-dd', 'value'),
    State('cust-dd', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date'),
    prevent_initial_call=True
)
def export_excel(n_clicks, state, city, customer, from_d, to_d):
    df = filter_df(state, city, customer, from_d, to_d)
    if df.empty:
        return None
    filename = "Filtered_Sales_Data.xlsx"
    df.to_excel(filename, index=False)
    return dcc.send_file(filename)

@callback(
    Output("download-pdf", "data"),
    Input("export-pdf-btn", "n_clicks"),
    State('state-dd', 'value'),
    State('city-dd', 'value'),
    State('cust-dd', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date'),
    State('chart-type', 'value'),
    prevent_initial_call=True
)
def export_pdf(n, s, c, p, fd, td, chart_type):
    fig = update_graph(s, c, p, fd, td, chart_type)
    filename = "chart_export.pdf"
    pio.write_image(fig, filename, format='pdf', width=1000, height=600)
    return dcc.send_file(filename)