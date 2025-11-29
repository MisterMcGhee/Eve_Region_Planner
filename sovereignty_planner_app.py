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
from bridge_manager import BridgeManager
import networkx as nx
import json

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Add custom CSS for dropdown styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom dropdown styling for better contrast */
            .custom-dropdown .Select-control {
                background-color: #2a2a2a !important;
            }
            .custom-dropdown .Select-menu-outer {
                background-color: #2a2a2a !important;
            }
            .custom-dropdown .Select-option {
                background-color: #2a2a2a !important;
                color: #ffffff !important;
            }
            .custom-dropdown .Select-option:hover {
                background-color: #00D9FF !important;
                color: #000000 !important;
            }
            .custom-dropdown .Select-value-label {
                color: #ffffff !important;
            }
            .custom-dropdown .Select-placeholder {
                color: #aaaaaa !important;
            }
            .custom-dropdown .Select-input > input {
                color: #ffffff !important;
            }
            /* For newer Dash versions using different dropdown classes */
            .custom-dropdown div[class*="singleValue"] {
                color: #ffffff !important;
            }
            .custom-dropdown div[class*="placeholder"] {
                color: #aaaaaa !important;
            }
            .custom-dropdown div[class*="menu"] {
                background-color: #2a2a2a !important;
            }
            .custom-dropdown div[class*="option"] {
                background-color: #2a2a2a !important;
                color: #ffffff !important;
            }
            .custom-dropdown div[class*="option"]:hover {
                background-color: #00D9FF !important;
                color: #000000 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Initialize our calculators
calc = UpgradeCalculator()
calc.load_data()
calc.load_system_upgrades("system_upgrades.json")

viz = GraphVisualizer()
viz.load_data()
viz.build_graph()
viz.assign_constellation_colors()
viz.calculate_layout(scale=60, positions_file="positions_kamada_kawai.json")

# Initialize bridge manager
bridge_mgr = BridgeManager(viz.graph)
bridge_mgr.load_bridges("ansiblex_bridges.json")

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
                    style={
                        'backgroundColor': '#2a2a2a',
                        'color': '#ffffff'
                    },
                    className='custom-dropdown'
                ),
            ], style={'marginBottom': '20px'}),

            # System Info Display
            html.Div(id='system-info', style={'marginBottom': '20px'}),

            # Capacity Gauges
            html.Div([
                html.H4("Capacity Usage", style={'color': '#00D9FF'}),
                dcc.Graph(id='power-gauge', config={'displayModeBar': False},
                         style={'height': '150px'}),
                dcc.Graph(id='workforce-gauge', config={'displayModeBar': False},
                         style={'height': '150px'}),
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
                    style={
                        'backgroundColor': '#2a2a2a',
                        'color': '#ffffff',
                        'marginBottom': '10px'
                    },
                    className='custom-dropdown'
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
            ], style={'marginBottom': '20px'}),

            # Ansiblex Bridges Section
            html.Hr(style={'borderColor': '#00D9FF', 'margin': '20px 0'}),
            html.Div([
                html.H3("Ansiblex Jump Bridges", style={'color': '#00D9FF'}),

                # Staging System Configuration
                html.Div([
                    html.H4("Staging System", style={'color': '#00D9FF', 'fontSize': '18px'}),
                    dcc.Dropdown(
                        id='staging-selector',
                        options=[{'label': sys, 'value': sys} for sys in all_systems],
                        value=bridge_mgr.get_staging_system(),
                        placeholder="Select staging system...",
                        style={'backgroundColor': '#2a2a2a', 'color': '#ffffff'},
                        className='custom-dropdown'
                    ),
                ], style={'marginBottom': '15px'}),

                # Bridge Statistics
                html.Div(id='bridge-stats', style={'marginBottom': '15px'}),

                # Optimization Controls
                html.Div([
                    html.H4("Optimize Bridges", style={'color': '#00D9FF', 'fontSize': '18px'}),
                    html.Label("Algorithm:", style={'color': '#ffffff'}),
                    dcc.Dropdown(
                        id='bridge-algorithm',
                        options=[
                            {'label': 'Farthest Systems (Recommended)', 'value': 'farthest_systems'},
                            {'label': 'Total Jump Reduction', 'value': 'staging_system'},
                            {'label': 'Max Distance Reduction', 'value': 'max_distance'}
                        ],
                        value='farthest_systems',
                        style={'backgroundColor': '#2a2a2a', 'color': '#ffffff', 'marginBottom': '10px'},
                        className='custom-dropdown'
                    ),
                    html.Label("Number of Bridges:", style={'color': '#ffffff'}),
                    dcc.Slider(
                        id='bridge-count-slider',
                        min=1,
                        max=20,
                        step=1,
                        value=10,
                        marks={i: str(i) for i in range(0, 21, 5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Button('Optimize Bridges', id='optimize-bridges-btn', n_clicks=0,
                               style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer', 'marginTop': '10px'}),
                    html.Button('Clear All Bridges', id='clear-bridges-btn', n_clicks=0,
                               style={'width': '100%', 'padding': '10px', 'backgroundColor': '#f44336',
                                      'color': 'white', 'border': 'none', 'cursor': 'pointer', 'marginTop': '10px'}),
                    html.Div(id='bridge-message', style={'marginTop': '10px'}),
                ]),
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

    # Calculate remaining capacities
    power_remaining = usage['total_power_capacity'] - usage['power_used']
    workforce_remaining = usage['total_workforce_capacity'] - usage['workforce_used']

    # Power horizontal bar
    power_fig = go.Figure()

    # Add used capacity bar
    power_fig.add_trace(go.Bar(
        y=['Power'],
        x=[usage['power_used']],
        orientation='h',
        name='Used',
        marker=dict(color='#00D9FF'),
        hovertemplate='Used: %{x:,}<extra></extra>'
    ))

    # Add remaining capacity bar
    power_fig.add_trace(go.Bar(
        y=['Power'],
        x=[power_remaining],
        orientation='h',
        name='Remaining',
        marker=dict(color='#2a2a2a'),
        hovertemplate='Remaining: %{x:,}<extra></extra>'
    ))

    power_fig.update_layout(
        barmode='stack',
        title=dict(
            text=f"Power: {power_remaining:,} / {usage['total_power_capacity']:,}",
            font=dict(color='#ffffff', size=16),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        margin=dict(l=20, r=20, t=60, b=20),
        height=150,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        )
    )

    # Workforce horizontal bar
    workforce_fig = go.Figure()

    # Add used capacity bar
    workforce_fig.add_trace(go.Bar(
        y=['Workforce'],
        x=[usage['workforce_used']],
        orientation='h',
        name='Used',
        marker=dict(color='#00D9FF'),
        hovertemplate='Used: %{x:,}<extra></extra>'
    ))

    # Add remaining capacity bar
    workforce_fig.add_trace(go.Bar(
        y=['Workforce'],
        x=[workforce_remaining],
        orientation='h',
        name='Remaining',
        marker=dict(color='#2a2a2a'),
        hovertemplate='Remaining: %{x:,}<extra></extra>'
    ))

    workforce_fig.update_layout(
        barmode='stack',
        title=dict(
            text=f"Workforce: {workforce_remaining:,} / {usage['total_workforce_capacity']:,}",
            font=dict(color='#ffffff', size=16),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        margin=dict(l=20, r=20, t=60, b=20),
        height=150,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        )
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
    triggered_value = ctx.triggered[0]['value']

    # Only process if button was actually clicked (not None, not 0)
    # When buttons are first added to DOM, n_clicks is None which triggers this callback
    # We need to ignore those false triggers
    if not triggered_value or triggered_value == 0:
        return ""

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

    # Create the figure with bridges
    fig = viz.create_plotly_figure(
        highlight_systems=highlight_systems,
        show_labels=True,
        title=f"Pure Blind Region - Selected: {selected_system}" if selected_system else "Pure Blind Region",
        editable=False,
        bridges=bridge_mgr.bridges
    )

    return fig


# Callback for click-to-select system on the map
@app.callback(
    Output('system-selector', 'value', allow_duplicate=True),
    Input('region-map', 'clickData'),
    prevent_initial_call=True
)
def select_system_from_map(clickData):
    """
    Update the system selector when a system is clicked on the map
    """
    if clickData is None:
        return dash.no_update

    # Extract the clicked point data
    try:
        # The clicked point will have the system name in the 'text' field or 'hovertext'
        point = clickData['points'][0]

        # Try to extract system name from hovertext (formatted as HTML)
        if 'hovertext' in point:
            hovertext = point['hovertext']
            # Extract system name from the first line of hover text
            # Format is: "<b>SystemName</b><br>..."
            system_name = hovertext.split('<br>')[0].replace('<b>', '').replace('</b>', '')
            return system_name

        # Fallback: try to get from 'text' field
        if 'text' in point and point['text']:
            return point['text']

        # If we can't determine the system name, don't update
        return dash.no_update

    except (KeyError, IndexError, AttributeError):
        # If there's any error extracting the system name, don't update
        return dash.no_update


# Bridge Management Callbacks

@app.callback(
    Output('bridge-stats', 'children'),
    Input('staging-selector', 'value')
)
def update_bridge_stats(staging_system):
    """Update bridge statistics display"""
    if not staging_system:
        return html.Div("No staging system selected", style={'color': '#ff6b6b'})

    bridge_mgr.set_staging_system(staging_system)

    # Calculate statistics
    total_bridges = len(bridge_mgr.bridges)
    active_bridges = sum(1 for b in bridge_mgr.bridges if b.get('active', True))

    if total_bridges == 0:
        return html.Div([
            html.P([html.Strong("No bridges configured")], style={'color': '#ffd93d'}),
            html.P(f"Staging: {staging_system}", style={'fontSize': '14px'}),
        ])

    # Calculate metrics
    distances = nx.single_source_shortest_path_length(viz.graph, staging_system)
    avg_distance = sum(distances.values()) / len(distances)
    max_distance = max(distances.values())

    return html.Div([
        html.P([html.Strong("Bridges: "), f"{active_bridges} active / {total_bridges} total"]),
        html.P([html.Strong("Staging: "), staging_system], style={'fontSize': '14px'}),
        html.P([html.Strong("Avg Jumps: "), f"{avg_distance:.2f}"]),
        html.P([html.Strong("Max Jumps: "), f"{max_distance}"]),
    ])


@app.callback(
    [Output('bridge-message', 'children'),
     Output('region-map', 'figure', allow_duplicate=True)],
    [Input('optimize-bridges-btn', 'n_clicks'),
     Input('clear-bridges-btn', 'n_clicks')],
    [State('staging-selector', 'value'),
     State('bridge-algorithm', 'value'),
     State('bridge-count-slider', 'value'),
     State('system-selector', 'value')],
    prevent_initial_call=True
)
def handle_bridge_operations(optimize_clicks, clear_clicks, staging_system, algorithm, max_bridges, selected_system):
    """Handle bridge optimization and clearing"""
    ctx = callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'clear-bridges-btn':
        bridge_mgr.clear_bridges()
        bridge_mgr.save_bridges()

        # Update map
        fig = viz.create_plotly_figure(
            highlight_systems=[selected_system] if selected_system else [],
            show_labels=True,
            title=f"Pure Blind Region - Selected: {selected_system}" if selected_system else "Pure Blind Region",
            editable=False,
            bridges=bridge_mgr.bridges
        )

        return html.Div("✓ All bridges cleared", style={'color': '#4CAF50'}), fig

    elif button_id == 'optimize-bridges-btn':
        if not staging_system:
            return html.Div("⚠ Please select a staging system", style={'color': '#ff6b6b'}), dash.no_update

        try:
            # Run optimization
            if algorithm == 'farthest_systems':
                bridges = bridge_mgr.optimize_for_farthest_systems(
                    staging_system=staging_system,
                    max_bridges=max_bridges,
                    target_percentile=0.80
                )
            elif algorithm == 'staging_system':
                regional_gates = bridge_mgr.config.get('regional_gates', [])
                bridges = bridge_mgr.optimize_for_staging_system(
                    staging_system=staging_system,
                    max_bridges=max_bridges,
                    regional_gates=regional_gates
                )
            else:  # max_distance
                bridges = bridge_mgr.optimize_for_max_distance_reduction(
                    staging_system=staging_system,
                    max_bridges=max_bridges
                )

            # Apply bridges
            bridge_mgr.clear_bridges()
            for bridge in bridges:
                bridge_mgr.add_bridge(bridge['from'], bridge['to'], validate=False)

            bridge_mgr.save_bridges()

            # Calculate improvement
            distances = nx.single_source_shortest_path_length(viz.graph, staging_system)
            avg_dist = sum(distances.values()) / len(distances)
            max_dist = max(distances.values())

            # Update map
            fig = viz.create_plotly_figure(
                highlight_systems=[selected_system] if selected_system else [],
                show_labels=True,
                title=f"Pure Blind Region - Selected: {selected_system}" if selected_system else "Pure Blind Region",
                editable=False,
                bridges=bridge_mgr.bridges
            )

            message = html.Div([
                html.P(f"✓ Optimized {len(bridges)} bridges", style={'color': '#4CAF50'}),
                html.P(f"Avg: {avg_dist:.2f} jumps | Max: {max_dist} jumps", style={'fontSize': '12px'})
            ])

            return message, fig

        except Exception as e:
            return html.Div(f"Error: {str(e)}", style={'color': '#ff6b6b'}), dash.no_update

    return dash.no_update, dash.no_update


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
