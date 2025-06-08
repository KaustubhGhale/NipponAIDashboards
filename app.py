import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load the data
df = pd.read_csv("erp_sales_data.csv")

# Convert Invoice_Date column to datetime
df['Invoice_Date'] = pd.to_datetime(df['Invoice_Date'], errors='coerce')

# Initialize the app
app = dash.Dash(__name__)
app.title = "ERP Sales Drill-Down Dashboard"

# App layout
app.layout = html.Div([
    html.H1("ERP Sales Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select State"),
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': s, 'value': s} for s in df['state_name'].dropna().unique()],
            placeholder="Select a state"
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select City"),
        dcc.Dropdown(id='city-dropdown'),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Customer"),
        dcc.Dropdown(id='customer-dropdown'),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Date Range"),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=df['Invoice_Date'].min(),
            max_date_allowed=df['Invoice_Date'].max(),
            start_date=df['Invoice_Date'].min(),
            end_date=df['Invoice_Date'].max()
        )
    ], style={'width': '35%', 'display': 'inline-block', 'marginLeft': '2%'}),

    html.Br(), html.Br(),

    dcc.Graph(id='sales-graph')
])

# Callback to update City based on State
@app.callback(
    Output('city-dropdown', 'options'),
    Input('state-dropdown', 'value')
)
def update_city_dropdown(selected_state):
    if selected_state:
        filtered_df = df[df['state_name'] == selected_state]
        return [{'label': c, 'value': c} for c in filtered_df['city_name'].dropna().unique()]
    return []

# Callback to update Customer based on City
@app.callback(
    Output('customer-dropdown', 'options'),
    Input('city-dropdown', 'value'),
    Input('state-dropdown', 'value')
)
def update_customer_dropdown(selected_city, selected_state):
    if selected_city and selected_state:
        filtered_df = df[(df['state_name'] == selected_state) & (df['city_name'] == selected_city)]
        return [{'label': c, 'value': c} for c in filtered_df['Party_Name'].dropna().unique()]
    return []

# Callback to update Graph
@app.callback(
    Output('sales-graph', 'figure'),
    Input('state-dropdown', 'value'),
    Input('city-dropdown', 'value'),
    Input('customer-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_graph(state, city, customer, start_date, end_date):
    filtered_df = df.copy()

    if state:
        filtered_df = filtered_df[filtered_df['state_name'] == state]
    if city:
        filtered_df = filtered_df[filtered_df['city_name'] == city]
    if customer:
        filtered_df = filtered_df[filtered_df['Party_Name'] == customer]

    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Invoice_Date'] >= start_date) & (filtered_df['Invoice_Date'] <= end_date)]

    # Group by date and sum invoice values
    grouped = filtered_df.groupby('Invoice_Date')['invoice_value'].sum().reset_index()

    fig = px.bar(
        grouped,
        x='Invoice_Date',
        y='invoice_value',
        title='Sales Over Time',
        labels={'invoice_value': 'Total Sales', 'Invoice_Date': 'Date'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
