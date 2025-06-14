# app.py
import os, pandas as pd
import dash, sqlite3
from dash import dcc, html, Input, Output, State
import plotly.express as px
from flask import Flask

# 1) Combine Flask + Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
API_PORT = 5050  # matches erp_salesdatagen.py

# 2) Layout, including upload
app.layout = html.Div([
    html.H1("ERP Sales Dashboard"),

    # File upload
    dcc.Upload(
      id='upload-csv',
      children=html.Button("Upload CSV"),
      multiple=False
    ),
    html.Div(id='upload-status'),

    # Filters
    dcc.Dropdown(id='state-dd', placeholder='State'),
    dcc.Dropdown(id='city-dd', placeholder='City'),
    dcc.Dropdown(id='cust-dd', placeholder='Customer'),
    dcc.DatePickerRange(id='date-picker',

        start_date_placeholder_text='From date',
        end_date_placeholder_text='To date'
    ),

    # Chart
    dcc.Graph(id='sales-graph')
])

# 3) Upload callback → POST to your erp_salesdatagen API
@app.callback(
  Output('upload-status','children'),
  Input('upload-csv','contents'),
  State('upload-csv','filename')
)
def upload(contents, filename):
    if not contents:
        return ""
    import requests, base64
    # Extract raw bytes
    b64 = contents.split(',')[1]
    data = base64.b64decode(b64)
    # Send to local API
    r = requests.post(f"http://localhost:{API_PORT}/upload", files={'file':(filename,data)})
    return f"Upload status: {r.json().get('status')}"

# 4) Whenever filters change, re‐gen CSV & reload the DF
def load_df(filters):
    # Build API call to gen_csv
    params = {k:v for k,v in filters.items() if v}
    import requests
    requests.get(f"http://localhost:{API_PORT}/gen_csv", params=params)
    return pd.read_csv('erp_sales_data.csv', parse_dates=['invoice_date'])

@app.callback(
  Output('state-dd','options'),
  Input('upload-status','children')
)
def init_states(_):
    df = pd.read_csv('erp_sales_data.csv')
    return [{'label':s,'value':s} for s in df['state_name'].unique()]

@app.callback(
  Output('city-dd','options'),
  Input('state-dd','value'),
  Input('upload-status','children')
)
def update_cities(state,_):
    df = pd.read_csv('erp_sales_data.csv')
    return [{'label':c,'value':c} for c in df[df['state_name']==state]['city_name'].unique()]

@app.callback(
  Output('cust-dd','options'),
  Input('state-dd','value'), Input('city-dd','value'),
  Input('upload-status','children')
)
def update_customers(s,c,_):
    df = pd.read_csv('erp_sales_data.csv')
    df = df[(df['state_name']==s)&(df['city_name']==c)]
    return [{'label':p,'value':p} for p in df['Party_Name'].unique()]

@app.callback(
  Output('sales-graph','figure'),
  Input('state-dd','value'),
  Input('city-dd','value'),
  Input('cust-dd','value'),
  Input('date-picker','start_date'),
  Input('date-picker','end_date')
)
def draw_graph(s,c,p,fd,td):
    df = load_df({
      't_code':None,       # you can add controls
      'location_code':None,
      'from_date':fd, 'to_date':td,
      'state_name':s, 'city_name':c, 'customer':p
    })
    if df.empty:
        return px.line(title="No data")
    return px.bar(df.groupby('item_name')['invoice_value'].sum().reset_index(),
                  x='item_name', y='invoice_value',
                  title="Sales by Item")

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))

