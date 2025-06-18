# pages/data_fetching.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import config_store
from sqlalchemy import text
import os
from datetime import datetime

dash.register_page(__name__, path="/data-fetching", name="Data Fetching")

layout = html.Div([
    # Full screen with modern background
    html.Div([
        html.Div([
            # Header Section
            html.Div([
                html.H1([
                    html.I(className="fas fa-database me-3"),
                    "SQL Query Interface"
                ], className="text-white text-center mb-1",
                   style={'fontSize': '3rem', 'fontWeight': 'bold'}),
                html.P("Execute SQL queries and export data to CSV format",
                      className="text-white text-center mb-4",
                      style={'fontSize': '1.2rem', 'opacity': '0.9'})
            ], className="mb-4"),
            
            # Connection Status Card
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-check-circle text-success me-2", style={'fontSize': '1.2rem'}),
                        html.Span("Connected to Oracle Database", className="fw-bold"),
                        html.Br(),
                        html.Small(id="connection-info", className="text-muted")
                    ], className="text-center")
                ])
            ], className="mb-4", style={'borderRadius': '10px', 'border': '2px solid #28a745'}),
            
            # Main Query Interface Card
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-code me-2"),
                        "SQL Query Editor"
                    ], className="mb-0")
                ]),
                
                dbc.CardBody([
                    # Query Input Section
                    html.Div([
                        html.Label("Enter SQL Query:", className="form-label fw-bold mb-3"),
                        dcc.Textarea(
                            id='sql-query-textarea',
                            placeholder='''Enter your SQL query here...

Example:
Select GRADE_CATG_CODE,
(Select SYSCDS_CODE_DESC from COR_SYSCODES 
 where syscds_code_value = HRD_CATG_PARA.GRADE_CATG_CODE 
 and SYSCDS_CODE_TYPE = 'EMP_CATEGORY' 
 and t_code = HRD_CATG_PARA.T_CODE) as GRADE_CATG_CODE_Desc,
GRADE_PARA_CODE,
(Select SYSCDS_CODE_DESC from COR_SYSCODES 
 where syscds_code_value = HRD_CATG_PARA.GRADE_PARA_CODE 
 and SYSCDS_CODE_TYPE = 'ASSMENT_PARA' 
 and t_code = HRD_CATG_PARA.T_CODE) as GRADE_PARA_CODE_Desc,
GRADE_ENTR_BY,
(Select empl_empl_name from HRD_EMPL_P 
 where HRD_EMPL_P.EMPL_EMPL_CODE = HRD_CATG_PARA.GRADE_ENTR_BY 
 and t_code = HRD_CATG_PARA.T_CODE) as GRADE_ENTR_BY_Desc,
to_char(GRADE_ENTR_DT,'dd/MM/yyyy') as GRADE_ENTR_DT
from HRD_CATG_PARA''',
                            style={
                                'width': '100%', 
                                'height': '300px', 
                                'fontFamily': 'Consolas, Monaco, monospace',
                                'fontSize': '14px',
                                'borderRadius': '10px',
                                'border': '2px solid #e9ecef',
                                'padding': '15px'
                            },
                            className='form-control'
                        )
                    ], className="mb-4"),
                    
                    # Action Buttons
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-play me-2"), "Execute Query"],
                            id="execute-sql-btn",
                            color="primary",
                            size="lg",
                            className="me-3",
                            style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-download me-2"), "Download CSV"],
                            id="download-results-btn",
                            color="success",
                            size="lg",
                            disabled=True,
                            className="me-3",
                            style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-eraser me-2"), "Clear"],
                            id="clear-sql-btn",
                            color="secondary",
                            size="lg",
                            outline=True,
                            style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                        )
                    ], className="text-center mb-4"),
                    
                    # Status and Results Section
                    html.Div(id="sql-execution-status"),
                    html.Div(id="query-results-preview", className="mt-4")
                ])
            ], style={'borderRadius': '15px', 'border': 'none', 'boxShadow': '0 10px 30px rgba(0,0,0,0.1)'}),
            
            # Navigation to Dashboard
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-tachometer-alt me-2"), "Go to Dashboard"],
                    id="go-to-dashboard-btn",
                    color="info",
                    size="lg",
                    outline=True,
                    href="/sales",
                    style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                )
            ], className="text-center mt-4")
            
        ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
    ], style={
        'minHeight': '100vh',
        'background': 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
        'padding': '50px 20px'
    }),
    
    # Hidden components
    dcc.Download(id="download-csv-file"),
    dcc.Store(id="executed-query-data")
])

@callback(
    Output("connection-info", "children"),
    Input("connection-info", "id")
)
def display_connection_info(_):
    if config_store.db_config:
        server = config_store.db_config.get('server', 'Unknown')
        service = config_store.db_config.get('service', 'Unknown')
        username = config_store.db_config.get('username', 'Unknown')
        mode = "Thick Mode" if config_store.db_config.get('thick_mode', False) else "Thin Mode"
        return f"Server: {server} | Service: {service} | User: {username} | Mode: {mode}"
    return "Connection information not available"

@callback(
    Output("sql-query-textarea", "value"),
    Input("clear-sql-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_sql_query(n_clicks):
    return ""

@callback(
    [Output("sql-execution-status", "children"),
     Output("query-results-preview", "children"),
     Output("executed-query-data", "data"),
     Output("download-results-btn", "disabled")],
    Input("execute-sql-btn", "n_clicks"),
    State("sql-query-textarea", "value"),
    prevent_initial_call=True
)
def execute_sql_query(n_clicks, query):
    if not query or not query.strip():
        return (
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Please enter a SQL query to execute"
            ], color="warning"),
            "",
            None,
            True
        )
    
    if not config_store.db_config:
        return (
            dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                "Database configuration not found. Please reconfigure the database connection."
            ], color="danger"),
            "",
            None,
            True
        )
    
    try:
        engine = config_store.db_config['engine']
        
        # Execute the query
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        
        if df.empty:
            return (
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Query executed successfully but returned no data"
                ], color="info"),
                "",
                None,
                True
            )
        
        # Save to data/erp_sales_data.csv
        os.makedirs("data", exist_ok=True)
        output_path = os.path.join("data", "erp_sales_data.csv")
        df.to_csv(output_path, index=False)
        
        # Create enhanced preview
        preview_card = dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="fas fa-table me-2"),
                    f"Query Results Preview"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                # Results summary
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(str(len(df)), className="text-primary mb-0"),
                                html.P("Total Rows", className="mb-0 text-muted")
                            ], className="text-center")
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(str(len(df.columns)), className="text-success mb-0"),
                                html.P("Columns", className="mb-0 text-muted")
                            ], className="text-center")
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{len(df.head(10))}", className="text-info mb-0"),
                                html.P("Preview Rows", className="mb-0 text-muted")
                            ], className="text-center")
                        ])
                    ], md=4)
                ], className="mb-4"),
                
                # Column information
                html.Div([
                    html.H6("Columns:", className="fw-bold"),
                    html.P(", ".join(df.columns.tolist()), className="text-muted small")
                ], className="mb-3"),
                
                # Data table preview
                html.Div([
                    dbc.Table.from_dataframe(
                        df.head(10), 
                        striped=True, 
                        bordered=True, 
                        hover=True,
                        size="sm",
                        responsive=True,
                        className="mb-0"
                    )
                ], style={'maxHeight': '400px', 'overflowY': 'auto'})
            ])
        ], style={'borderRadius': '10px'})
        
        # Success status
        success_status = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Query executed successfully! Retrieved {len(df)} rows with {len(df.columns)} columns. Saved to data/erp_sales_data.csv"
        ], color="success")
        
        return success_status, preview_card, df.to_dict('records'), False
        
    except Exception as e:
        error_msg = str(e)
        error_alert = dbc.Alert([
            html.H5([html.I(className="fas fa-times-circle me-2"), "Query Execution Failed"], className="mb-3"),
            html.P(f"Error: {error_msg}"),
            html.Hr(),
            html.P("Suggestions:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Check your SQL syntax"),
                html.Li("Verify table and column names exist"),
                html.Li("Ensure you have proper database permissions"),
                html.Li("Check if the database connection is still active")
            ]),
            html.Small("If the error persists, contact your database administrator.", className="text-muted")
        ], color="danger")
        
        return error_alert, "", None, True

@callback(
    Output("download-csv-file", "data"),
    Input("download-results-btn", "n_clicks"),
    State("executed-query-data", "data"),
    prevent_initial_call=True
)
def download_query_results(n_clicks, data):
    if not data:
        return None
    
    # Convert back to DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sql_query_results_{timestamp}.csv"
    
    # Save to temporary file for download
    df.to_csv(filename, index=False)
    
    return dcc.send_file(filename)