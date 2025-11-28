"""
Pure Blind Region Planner - Sovereignty Upgrade Planning Dashboard
===================================================================

Interactive Dash web application for planning sovereignty upgrades across
the Pure Blind region.

Usage:
    python sovereignty_planner_app.py

Then open http://127.0.0.1:8050 in your browser
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
from upgrade_calculator import UpgradeCalculator
from graph_visualizer import GraphVisualizer
import json

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Initialize our calculators
calc = UpgradeCalculator()
calc.load_data()
calc.load_system_upgrades("system_upgrades.json")

viz = GraphVisualizer()
viz.load_data()
viz.build_graph()
viz.assign_constellation_colors()
viz.calculate_layout(scale=60, positions_file="positions_kamada_kawai.json")

# Get list of systems for dropdown
all_systems = sorted(viz.systems_df['system_name'].tolist())

# Get upgrade categories and upgrades
upgrade_categories = calc.upgrades_df['category'].unique().tolist()
all_upgrades = sorted(calc.upgrades_df['upgrade_name'].tolist())

# Define the app layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Pure Blind Sovereignty Upgrade Planner",
                style={'textAlign': 'center', 'color': '#00D9FF', 'margin': '10px'}),
    ], style={'backgroundColor': '#1a1a1a', 'padding': '10px'}),

    # Main content area - split screen
    html.Div([
        # Left panel - Controls (30%)
        html.Div([
            # System Selector
            html.Div([
                html.H3("System Selection", style={'color': '#00D9FF'}),
                dcc.Dropdown(
                    id='system-selector',
                    options=[{'label': sys, 'value': sys} for sys in all_systems],
                    value=all_systems[0],
                    style={'backgroundColor': '#2a2a2a', 'color': '#000'}
                ),
            ], style={'marginBottom': '20px'}),

            # System Info Display
            html.Div(id='system-info', style={'marginBottom': '20px'}),

            # Capacity Gauges
            html.Div([
                html.H4("Capacity Usage", style={'color': '#00D9FF'}),
                dcc.Graph(id='power-gauge', config={'displayModeBar': False},
                         style={'height': '200px'}),
                dcc.Graph(id='workforce-gauge', config={'displayModeBar': False},
                         style={'height': '200px'}),
            ], style={'marginBottom': '20px'}),

            # Preset Buttons
            html.Div([
                html.H4("Preset Configurations", style={'color': '#00D9FF'}),
                html.Div([
                    html.Button('Max Mining', id='preset-max-mining', n_clicks=0,
                               style={'margin': '5px', 'padding': '10px', 'backgroundColor': '#4CAF50',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
                    html.Button('Max Ratting', id='preset-max-ratting', n_clicks=0,
                               style={'margin': '5px', 'padding': '10px', 'backgroundColor': '#f44336',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
                    html.Button('Balanced', id='preset-balanced', n_clicks=0,
                               style={'margin': '5px', 'padding': '10px', 'backgroundColor': '#2196F3',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
                    html.Button('Clear All', id='preset-empty', n_clicks=0,
                               style={'margin': '5px', 'padding': '10px', 'backgroundColor': '#757575',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
                ], style={'display': 'flex', 'flexWrap': 'wrap'}),
            ], style={'marginBottom': '20px'}),

            # Installed Upgrades
            html.Div([
                html.H4("Installed Upgrades", style={'color': '#00D9FF'}),
                html.Div(id='installed-upgrades-list'),
            ], style={'marginBottom': '20px'}),

            # Add Upgrade Controls
            html.Div([
                html.H4("Add Upgrade", style={'color': '#00D9FF'}),
                dcc.Dropdown(
                    id='upgrade-selector',
                    options=[{'label': upg, 'value': upg} for upg in all_upgrades if upg != 'Empty'],
                    placeholder="Select upgrade to add...",
                    style={'backgroundColor': '#2a2a2a', 'color': '#000', 'marginBottom': '10px'}
                ),
                html.Button('Add Upgrade', id='add-upgrade-btn', n_clicks=0,
                           style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50',
                                  'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
                html.Div(id='add-upgrade-message', style={'marginTop': '10px'}),
            ], style={'marginBottom': '20px'}),

            # Save/Export
            html.Div([
                html.Button('Save Configuration', id='save-config-btn', n_clicks=0,
                           style={'width': '100%', 'padding': '10px', 'backgroundColor': '#00D9FF',
                                  'color': 'black', 'border': 'none', 'cursor': 'pointer', 'fontWeight': 'bold'}),
                html.Div(id='save-message', style={'marginTop': '10px'}),
            ]),

        ], style={
            'width': '30%',
            'float': 'left',
            'padding': '20px',
            'backgroundColor': '#1a1a1a',
            'color': '#ffffff',
            'height': 'calc(100vh - 100px)',
            'overflowY': 'auto'
        }),

        # Right panel - Visualization (70%)
        html.Div([
            html.H3("Region Map", style={'color': '#00D9FF', 'textAlign': 'center'}),
            dcc.Graph(
                id='region-map',
                config={'displayModeBar': True, 'scrollZoom': True},
                style={'height': 'calc(100vh - 150px)'}
            ),
        ], style={
            'width': '70%',
            'float': 'right',
            'backgroundColor': '#0a0a0a',
            'padding': '20px',
            'height': 'calc(100vh - 100px)'
        }),

    ], style={'display': 'flex'}),

    # Hidden div to store state
    html.Div(id='state-store', style={'display': 'none'}),

], style={'backgroundColor': '#0a0a0a', 'minHeight': '100vh'})


# Callback for updating system info display
@app.callback(
    Output('system-info', 'children'),
    Input('system-selector', 'value')
)
def update_system_info(system_name):
    if not system_name:
        return "No system selected"

    # Get system info from graph
    info = viz.get_system_info(system_name)

    return html.Div([
        html.P([html.Strong("Constellation: "), info['constellation']]),
        html.P([html.Strong("Security: "), f"{info['security']:.2f}"]),
        html.P([html.Strong("Moons: "), str(info['moons'])]),
        html.P([html.Strong("Ice Belt: "), "Yes" if info['has_ice'] else "No"]),
        html.P([html.Strong("Base Power: "), f"{info['power_capacity']:,}"]),
        html.P([html.Strong("Base Workforce: "), f"{info['workforce_capacity']:,}"]),
    ], style={'fontSize': '14px', 'color': '#cccccc'})


# Callback for updating capacity gauges
@app.callback(
    [Output('power-gauge', 'figure'),
     Output('workforce-gauge', 'figure')],
    Input('system-selector', 'value')
)
def update_capacity_gauges(system_name):
    if not system_name:
        # Return empty gauges
        empty_fig = go.Figure()
        return empty_fig, empty_fig

    # Calculate usage
    usage = calc.calculate_capacity_usage(system_name)

    # Power gauge
    power_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=usage['power_used'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Power", 'font': {'color': '#ffffff'}},
        delta={'reference': usage['total_power_capacity'], 'decreasing': {'color': '#4CAF50'}},
        gauge={
            'axis': {'range': [None, usage['total_power_capacity']], 'tickcolor': '#ffffff'},
            'bar': {'color': "#00D9FF"},
            'bgcolor': "#2a2a2a",
            'borderwidth': 2,
            'bordercolor': "#ffffff",
            'steps': [
                {'range': [0, usage['total_power_capacity'] * 0.7], 'color': '#1a4d1a'},
                {'range': [usage['total_power_capacity'] * 0.7, usage['total_power_capacity'] * 0.9], 'color': '#4d4d1a'},
                {'range': [usage['total_power_capacity'] * 0.9, usage['total_power_capacity']], 'color': '#4d1a1a'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': usage['total_power_capacity']
            }
        }
    ))
    power_fig.update_layout(
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#ffffff'},
        margin=dict(l=20, r=20, t=40, b=20),
        height=200
    )

    # Workforce gauge
    workforce_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=usage['workforce_used'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Workforce", 'font': {'color': '#ffffff'}},
        delta={'reference': usage['total_workforce_capacity'], 'decreasing': {'color': '#4CAF50'}},
        gauge={
            'axis': {'range': [None, usage['total_workforce_capacity']], 'tickcolor': '#ffffff'},
            'bar': {'color': "#00D9FF"},
            'bgcolor': "#2a2a2a",
            'borderwidth': 2,
            'bordercolor': "#ffffff",
            'steps': [
                {'range': [0, usage['total_workforce_capacity'] * 0.7], 'color': '#1a4d1a'},
                {'range': [usage['total_workforce_capacity'] * 0.7, usage['total_workforce_capacity'] * 0.9], 'color': '#4d4d1a'},
                {'range': [usage['total_workforce_capacity'] * 0.9, usage['total_workforce_capacity']], 'color': '#4d1a1a'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': usage['total_workforce_capacity']
            }
        }
    ))
    workforce_fig.update_layout(
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#ffffff'},
        margin=dict(l=20, r=20, t=40, b=20),
        height=200
    )

    return power_fig, workforce_fig


# Callback for displaying installed upgrades
@app.callback(
    Output('installed-upgrades-list', 'children'),
    Input('system-selector', 'value')
)
def update_installed_upgrades_list(system_name):
    if not system_name:
        return "No system selected"

    upgrades = calc.system_upgrades.get(system_name, [])

    if not upgrades:
        return html.P("No upgrades installed", style={'color': '#888888', 'fontStyle': 'italic'})

    upgrade_items = []
    for upgrade_name in upgrades:
        upgrade_info = calc.get_upgrade_info(upgrade_name)
        upgrade_items.append(
            html.Div([
                html.Div([
                    html.Strong(upgrade_name, style={'color': '#00D9FF'}),
                    html.Br(),
                    html.Small(f"Power: {upgrade_info['power']:+,} | Workforce: {upgrade_info['workforce']:+,}",
                              style={'color': '#888888'}),
                ], style={'flex': '1'}),
                html.Button('Remove',
                           id={'type': 'remove-upgrade-btn', 'index': upgrade_name},
                           n_clicks=0,
                           style={'padding': '5px 10px', 'backgroundColor': '#f44336',
                                  'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '10px',
                'margin': '5px 0',
                'backgroundColor': '#2a2a2a',
                'borderRadius': '5px'
            })
        )

    return html.Div(upgrade_items)


# Callback for handling preset buttons
@app.callback(
    [Output('add-upgrade-message', 'children'),
     Output('system-selector', 'value', allow_duplicate=True)],
    [Input('preset-max-mining', 'n_clicks'),
     Input('preset-max-ratting', 'n_clicks'),
     Input('preset-balanced', 'n_clicks'),
     Input('preset-empty', 'n_clicks')],
    State('system-selector', 'value'),
    prevent_initial_call=True
)
def handle_preset_buttons(max_mining_clicks, max_ratting_clicks, balanced_clicks, empty_clicks, system_name):
    if not system_name:
        return "No system selected", system_name

    ctx = callback_context
    if not ctx.triggered:
        return "", system_name

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    preset_map = {
        'preset-max-mining': 'max_mining',
        'preset-max-ratting': 'max_ratting',
        'preset-balanced': 'balanced',
        'preset-empty': 'empty'
    }

    preset = preset_map.get(button_id)
    if preset:
        try:
            added = calc.apply_preset(system_name, preset)
            # Force update by returning same value (triggers dependent callbacks)
            return html.Div([
                html.P(f"✓ Applied preset '{preset}' to {system_name}", style={'color': '#4CAF50'}),
                html.P(f"Added {len(added)} upgrades" if added else "Cleared all upgrades",
                      style={'color': '#888888', 'fontSize': '12px'})
            ]), system_name
        except Exception as e:
            return html.P(f"❌ Error: {str(e)}", style={'color': '#f44336'}), system_name

    return "", system_name


# Callback for adding upgrades
@app.callback(
    [Output('add-upgrade-message', 'children', allow_duplicate=True),
     Output('upgrade-selector', 'value')],
    Input('add-upgrade-btn', 'n_clicks'),
    [State('system-selector', 'value'),
     State('upgrade-selector', 'value')],
    prevent_initial_call=True
)
def add_upgrade(n_clicks, system_name, upgrade_name):
    if not system_name or not upgrade_name:
        return "Please select both system and upgrade", None

    try:
        # Check if can add
        can_add, reason = calc.can_add_upgrade(system_name, upgrade_name)

        if can_add:
            calc.add_upgrade(system_name, upgrade_name)
            return html.P(f"✓ Added '{upgrade_name}' to {system_name}",
                         style={'color': '#4CAF50'}), None
        else:
            return html.P(f"❌ {reason}", style={'color': '#f44336'}), None

    except Exception as e:
        return html.P(f"❌ Error: {str(e)}", style={'color': '#f44336'}), None


# Callback for removing upgrades
@app.callback(
    Output('add-upgrade-message', 'children', allow_duplicate=True),
    Input({'type': 'remove-upgrade-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('system-selector', 'value'),
    prevent_initial_call=True
)
def remove_upgrade(n_clicks_list, system_name):
    ctx = callback_context
    if not ctx.triggered or not system_name:
        return ""

    # Get which button was clicked
    button_id = ctx.triggered[0]['prop_id']
    if 'remove-upgrade-btn' in button_id:
        # Extract upgrade name from button id
        import json as json_lib
        upgrade_name = json_lib.loads(button_id.split('.')[0])['index']

        try:
            calc.remove_upgrade(system_name, upgrade_name)
            return html.P(f"✓ Removed '{upgrade_name}' from {system_name}",
                         style={'color': '#4CAF50'})
        except Exception as e:
            return html.P(f"❌ Error: {str(e)}", style={'color': '#f44336'})

    return ""


# Callback for saving configuration
@app.callback(
    Output('save-message', 'children'),
    Input('save-config-btn', 'n_clicks'),
    prevent_initial_call=True
)
def save_configuration(n_clicks):
    try:
        calc.save_system_upgrades("system_upgrades.json")
        return html.P("✓ Configuration saved successfully!", style={'color': '#4CAF50'})
    except Exception as e:
        return html.P(f"❌ Error saving: {str(e)}", style={'color': '#f44336'})


# Callback for updating the map visualization
@app.callback(
    Output('region-map', 'figure'),
    Input('system-selector', 'value')
)
def update_map(selected_system):
    # Find all systems with upgrades
    systems_with_upgrades = [sys for sys, upgs in calc.system_upgrades.items() if upgs]

    # Highlight both selected system and systems with upgrades
    highlight_systems = list(set([selected_system] + systems_with_upgrades)) if selected_system else systems_with_upgrades

    # Create the figure
    fig = viz.create_plotly_figure(
        highlight_systems=highlight_systems,
        show_labels=True,
        title=f"Pure Blind Region - Selected: {selected_system}" if selected_system else "Pure Blind Region",
        editable=False
    )

    return fig


if __name__ == '__main__':
    print("="*70)
    print("Pure Blind Sovereignty Upgrade Planner - Web Dashboard")
    print("="*70)
    print()
    print("Starting Dash application...")
    print("Open your browser to: http://127.0.0.1:8050")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)

    app.run(debug=True, host='127.0.0.1', port=8050)
