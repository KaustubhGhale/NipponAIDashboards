# pages/config.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ctx
import config_store
import oracledb
import os
from sqlalchemy import create_engine, text

# Global variable to track if thick mode is initialized
_thick_mode_initialized = False

def ensure_thick_mode():
    """Ensure Oracle thick mode is properly initialized"""
    global _thick_mode_initialized
    
    if _thick_mode_initialized:
        return True
    
    # Common Oracle Instant Client installation paths
    ORACLE_CLIENT_PATHS = [
        "C:\\oracle\\instantclient_23_8",
        "C:\\oracle\\instantclient_21_3", 
        "C:\\oracle\\instantclient_19_3",
        "C:\\oracle\\instantclient_12_2",
        "C:\\instantclient_23_8",
        "C:\\instantclient_21_3",
        "C:\\instantclient_19_3",
        "C:\\instantclient_12_2",
        "/opt/oracle/instantclient_23_8",  # Linux paths
        "/opt/oracle/instantclient_21_3",
        "/usr/lib/oracle/23/client64/lib", # Ubuntu/Debian
        "/usr/lib/oracle/21/client64/lib",
        "/usr/lib/oracle/19.3/client64/lib"
    ]
    
    for client_path in ORACLE_CLIENT_PATHS:
        try:
            if os.path.exists(client_path):
                print(f"Attempting to initialize Oracle thick mode with: {client_path}")
                oracledb.init_oracle_client(lib_dir=client_path)
                print(f"✅ Oracle thick mode initialized successfully with: {client_path}")
                _thick_mode_initialized = True
                return True
        except Exception as e:
            print(f"Failed to initialize Oracle client at {client_path}: {e}")
            continue
    
    print("❌ Warning: Could not initialize Oracle thick mode. Thick mode requires Oracle Instant Client.")
    return False

# Try to initialize thick mode when module loads
thick_mode_available = ensure_thick_mode()

# Register this as the /config page
dash.register_page(__name__, path="/config", name="Database Configuration")

layout = html.Div([
    # Full screen background with gradient
    html.Div([
        html.Div([
            # Header Section
            html.Div([
                html.H1("ERP Database Configuration", 
                       className="text-white text-center mb-1",
                       style={'fontSize': '3rem', 'fontWeight': 'bold'}),
                html.P("Configure your Oracle database connection to get started",
                      className="text-white text-center mb-4",
                      style={'fontSize': '1.2rem', 'opacity': '0.9'})
            ], className="mb-5"),
            
            # Main Configuration Card
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Database Connection Setup", className="mb-0 text-center"),
                    html.Hr(),
                    # Oracle Thick Mode Status
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        "Oracle Connection Mode: " + ("✅ Thick Mode Enabled" if thick_mode_available else "⚠️ Thin Mode (Limited Compatibility)")
                    ], color="success" if thick_mode_available else "warning", className="mb-0")
                ]),
                
                dbc.CardBody([
                    dbc.Form([
                        # Server Configuration
                        dbc.Row([
                            dbc.Col([
                                html.Label("Database Server", className="form-label fw-bold"),
                                dcc.Input(
                                    id="server-input",
                                    type="text",
                                    placeholder="192.168.1.206",
                                    className="form-control form-control-lg",
                                    style={'borderRadius': '10px'}
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Port", className="form-label fw-bold"),
                                dcc.Input(
                                    id="port-input",
                                    type="text",
                                    placeholder="1521",
                                    className="form-control form-control-lg",
                                    style={'borderRadius': '10px'}
                                )
                            ], md=6)
                        ], className="mb-4"),
                        
                        # Service Name
                        dbc.Row([
                            dbc.Col([
                                html.Label("Service Name", className="form-label fw-bold"),
                                dcc.Input(
                                    id="service-input",
                                    type="text",
                                    placeholder="ORCL",
                                    className="form-control form-control-lg",
                                    style={'borderRadius': '10px'}
                                )
                            ], md=12)
                        ], className="mb-4"),
                        
                        # Credentials
                        dbc.Row([
                            dbc.Col([
                                html.Label("Username", className="form-label fw-bold"),
                                dcc.Input(
                                    id="username-input",
                                    type="text",
                                    placeholder="NEWTON_ERP",
                                    className="form-control form-control-lg",
                                    style={'borderRadius': '10px'}
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Password", className="form-label fw-bold"),
                                dcc.Input(
                                    id="password-input",
                                    type="password",
                                    placeholder="Enter password",
                                    className="form-control form-control-lg",
                                    style={'borderRadius': '10px'}
                                )
                            ], md=6)
                        ], className="mb-4"),
                        
                        # Action Buttons
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-plug me-2"), "Test Connection"],
                                id="test-connection-btn",
                                color="info",
                                size="lg",
                                className="me-3",
                                style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-arrow-right me-2"), "Submit & Proceed"],
                                id="submit-proceed-btn",
                                color="success",
                                size="lg",
                                disabled=True,
                                style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                            )
                        ], className="text-center mb-4"),
                        
                        # Status Messages
                        html.Div(id="connection-status", className="mt-3"),
                        
                        # Help Section Toggle
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-question-circle me-2"), "Need Help with Oracle Client?"],
                                id="help-toggle-btn",
                                color="link",
                                size="sm"
                            )
                        ], className="text-center mt-3")
                    ])
                ])
            ], style={'borderRadius': '15px', 'border': 'none', 'boxShadow': '0 10px 30px rgba(0,0,0,0.1)'}),
            
            # Help Section (Collapsible)
            dbc.Collapse([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-download me-2"), "Oracle Instant Client Setup"], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("For older Oracle databases (before 12.1), you need Oracle Instant Client:", className="mb-3"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Strong("Step 1: "),
                                "Download Oracle Instant Client from ",
                                html.A("Oracle Downloads", href="https://www.oracle.com/database/technologies/instant-client/downloads.html", target="_blank", className="text-decoration-none")
                            ]),
                            dbc.ListGroupItem([
                                html.Strong("Step 2: "),
                                "Extract to one of these paths:",
                                html.Ul([
                                    html.Li("Windows: C:\\oracle\\instantclient_23_8"),
                                    html.Li("Windows: C:\\instantclient_23_8"),
                                    html.Li("Linux: /opt/oracle/instantclient_23_8")
                                ], className="mt-2 mb-0")
                            ]),
                            dbc.ListGroupItem([
                                html.Strong("Step 3: "),
                                "Restart your Python application"
                            ]),
                            dbc.ListGroupItem([
                                html.Strong("Step 4: "),
                                "The connection mode above should show 'Thick Mode Enabled'"
                            ])
                        ], flush=True),
                        html.Hr(),
                        html.P("Alternative: Ask your DBA to upgrade Oracle Database to version 12.1 or later.", 
                              className="text-muted mb-0")
                    ])
                ], style={'borderRadius': '10px'})
            ], id="help-collapse", is_open=False, className="mt-4")
            
        ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})
    ], style={
        'minHeight': '100vh',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '50px 20px'
    })
])

@callback(
    Output("help-collapse", "is_open"),
    Input("help-toggle-btn", "n_clicks"),
    State("help-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_help_section(n_clicks, is_open):
    return not is_open

@callback(
    [Output("connection-status", "children"),
     Output("submit-proceed-btn", "disabled")],
    Input("test-connection-btn", "n_clicks"),
    Input("submit-proceed-btn", "n_clicks"),
    State("server-input", "value"),
    State("port-input", "value"),
    State("service-input", "value"),
    State("username-input", "value"),
    State("password-input", "value"),
    prevent_initial_call=True
)
def handle_connection_actions(test_clicks, submit_clicks, server, port, service, username, password):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Validate required fields
    if not all([server, port, service, username, password]):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all required fields"
        ], color="warning"), True
    
    # Create connection string
    conn_str = f'oracle+oracledb://{username}:{password}@{server}:{port}/{service}'
    
    if triggered_id == "test-connection-btn":
        try:
            # Create engine for testing
            engine = create_engine(conn_str, pool_pre_ping=True, pool_recycle=3600)
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()
            
            engine.dispose()  # Clean up test connection
            
            # Success message
            mode_info = "Thick Mode" if _thick_mode_initialized else "Thin Mode"
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Connection successful using {mode_info}! You can now proceed."
            ], color="success"), False
            
        except Exception as e:
            error_msg = str(e)
            if "DPY-3010" in error_msg:
                return dbc.Alert([
                    html.H5([html.I(className="fas fa-times-circle me-2"), "Oracle Version Not Supported"], className="mb-3"),
                    html.P("Your Oracle database version requires thick mode with Oracle Instant Client."),
                    html.Hr(),
                    html.P("Solutions:", className="mb-2 fw-bold"),
                    dbc.ListGroup([
                        dbc.ListGroupItem("Install Oracle Instant Client (see help section below)"),
                        dbc.ListGroupItem("Ask your DBA to upgrade Oracle Database to version 12.1+"),
                        dbc.ListGroupItem("Use a different connection method through your DBA")
                    ], flush=True),
                    html.Hr(),
                    html.Small(f"Technical details: {error_msg}", className="text-muted")
                ], color="danger"), True
            else:
                return dbc.Alert([
                    html.I(className="fas fa-times-circle me-2"),
                    f"Connection failed: {error_msg}"
                ], color="danger"), True
    
    elif triggered_id == "submit-proceed-btn":
        try:
            # Create and test engine
            engine = create_engine(conn_str, pool_pre_ping=True, pool_recycle=3600)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()
            
            # Store configuration
            config_store.db_config = {
                'server': server,
                'port': port,
                'service': service,
                'username': username,
                'password': password,
                'conn_str': conn_str,
                'engine': engine,
                'thick_mode': _thick_mode_initialized
            }
            
            # Redirect to data fetching page
            return dcc.Location(pathname="/data-fetching", id="redirect-to-data-fetching"), True
            
        except Exception as e:
            error_msg = str(e)
            return dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                f"Configuration failed: {error_msg}"
            ], color="danger"), True
    
    return "", True