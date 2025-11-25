"""
Pure Blind Planning Tool - Dash Application Starter
===================================================

This is a working starter template showing the split-screen architecture.
Demonstrates how tools switch and update the visualization.

Install: pip install dash plotly networkx
Run: python dash_app_starter.py
Open: http://127.0.0.1:8050/
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path

# ============================================================================
# LOAD DATA (from Phase 1)
# ============================================================================

def load_graph():
    """Load the Pure Blind graph from Phase 1 output"""
    graph_path = Path("../data/pure_blind_data") / "pure_blind_graph.graphml"
    
    if not graph_path.exists():
        # Create a simple demo graph if Phase 1 hasn't run yet
        G = nx.Graph()
        demo_systems = {
            '5ZXX-K': {'x': 0, 'y': 0, 'power': 2500, 'workforce': 18000, 'constellation': 'U-7RBK'},
            'X-7OMU': {'x': 1, 'y': 1, 'power': 2000, 'workforce': 15000, 'constellation': '38G6-L'},
            'EC-P8R': {'x': 2, 'y': 0, 'power': 1600, 'workforce': 30000, 'constellation': 'YS-GOP'},
            'KQK1-2': {'x': 0, 'y': 2, 'power': 2000, 'workforce': 11000, 'constellation': 'MDM8-J'},
        }
        for sys, attrs in demo_systems.items():
            G.add_node(sys, **attrs)
        G.add_edges_from([('5ZXX-K', 'X-7OMU'), ('X-7OMU', 'EC-P8R'), ('5ZXX-K', 'KQK1-2')])
        return G
    
    G = nx.read_graphml(graph_path)
    # Convert string attributes back to proper types
    for node in G.nodes():
        G.nodes[node]['x'] = float(G.nodes[node]['x'])
        G.nodes[node]['y'] = float(G.nodes[node]['y'])
    return G

# ============================================================================
# APP STATE
# ============================================================================

G = load_graph()
system_list = sorted(G.nodes())

# Initial state
app_state = {
    'bridges': [],  # [(from, to), ...]
    'system_upgrades': {},  # {system: [{type, level, power, workforce}, ...]}
    'reference_system': system_list[0] if system_list else None,
}

# ============================================================================
# DASH APP SETUP
# ============================================================================

app = dash.Dash(__name__)
app.title = "Pure Blind Planning Tool"

# ============================================================================
# STYLES
# ============================================================================

STYLE_LEFT_PANEL = {
    'width': '30%',
    'display': 'inline-block',
    'vertical-align': 'top',
    'padding': '20px',
    'background-color': '#2a2a2a',
    'height': '100vh',
    'overflow-y': 'auto',
}

STYLE_RIGHT_PANEL = {
    'width': '70%',
    'display': 'inline-block',
    'vertical-align': 'top',
    'padding': '20px',
    'background-color': '#1a1a1a',
    'height': '100vh',
}

STYLE_SECTION = {
    'margin-bottom': '20px',
    'padding': '15px',
    'background-color': '#3a3a3a',
    'border-radius': '5px',
}

STYLE_BUTTON = {
    'background-color': '#4ECDC4',
    'color': 'white',
    'border': 'none',
    'padding': '10px 20px',
    'border-radius': '5px',
    'cursor': 'pointer',
    'margin': '5px',
}

STYLE_DROPDOWN = {
    'background-color': '#3a3a3a',
    'color': 'white',
}

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Pure Blind Sovereignty Planning Tool", 
                style={'color': 'white', 'margin': '20px', 'text-align': 'center'}),
    ], style={'background-color': '#0a0a0a'}),
    
    # Main Content
    html.Div([
        # LEFT PANEL - CONTROLS
        html.Div([
            html.H3("Control Panel", style={'color': 'white'}),
            
            # Tool Selector
            html.Div([
                html.Label("Select Tool:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='tool-selector',
                    options=[
                        {'label': '🌉 Ansiblex Bridge Builder', 'value': 'ansiblex'},
                        {'label': '⚙️ System Upgrade Planner', 'value': 'upgrades'},
                        {'label': '⛏️ Mining System Optimizer', 'value': 'mining'},
                        {'label': '📊 Strategic Network Analysis', 'value': 'strategic'},
                    ],
                    value='ansiblex',
                    style={'margin-top': '10px'},
                ),
            ], style=STYLE_SECTION),
            
            # Dynamic tool controls (changes based on selected tool)
            html.Div(id='tool-controls', style={'margin-top': '20px'}),
            
            # Status/Feedback
            html.Div(id='status-message', style={
                'margin-top': '20px',
                'padding': '10px',
                'border-radius': '5px',
                'color': 'white',
            }),
            
        ], style=STYLE_LEFT_PANEL),
        
        # RIGHT PANEL - VISUALIZATION
        html.Div([
            html.H3("Visualization Dashboard", style={'color': 'white'}),
            
            # Main visualization area (changes based on tool)
            dcc.Graph(
                id='main-visualization',
                style={'height': '70vh'},
                config={'displayModeBar': True}
            ),
            
            # Metrics display (below graph)
            html.Div(id='metrics-display', style={'color': 'white', 'margin-top': '20px'}),
            
        ], style=STYLE_RIGHT_PANEL),
    ]),
    
    # Hidden stores for state management
    dcc.Store(id='app-state', data=app_state),
    
], style={'background-color': '#0a0a0a', 'min-height': '100vh'})

# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('tool-controls', 'children'),
    Input('tool-selector', 'value'),
)
def update_tool_controls(tool):
    """Generate different controls based on selected tool"""
    
    if tool == 'ansiblex':
        return html.Div([
            html.H4("Ansiblex Bridge Builder", style={'color': 'white'}),
            
            html.Div([
                html.Label("Reference System:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='reference-system',
                    options=[{'label': s, 'value': s} for s in system_list],
                    value=system_list[0] if system_list else None,
                    style={'margin-top': '5px'},
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Hr(style={'border-color': '#555'}),
            
            html.Div([
                html.Label("Add New Bridge:", style={'color': 'white'}),
                html.Div([
                    html.Label("From:", style={'color': 'white', 'margin-right': '10px'}),
                    dcc.Dropdown(
                        id='bridge-from',
                        options=[{'label': s, 'value': s} for s in system_list],
                        value=system_list[0] if system_list else None,
                        style={'width': '200px', 'display': 'inline-block'},
                    ),
                ], style={'margin-bottom': '10px'}),
                
                html.Div([
                    html.Label("To:", style={'color': 'white', 'margin-right': '10px'}),
                    dcc.Dropdown(
                        id='bridge-to',
                        options=[{'label': s, 'value': s} for s in system_list],
                        value=system_list[1] if len(system_list) > 1 else None,
                        style={'width': '200px', 'display': 'inline-block'},
                    ),
                ], style={'margin-bottom': '10px'}),
                
                html.Button("Add Bridge", id='add-bridge-btn', n_clicks=0, style=STYLE_BUTTON),
            ]),
            
            html.Hr(style={'border-color': '#555'}),
            
            html.Div([
                html.H5("Current Bridges:", style={'color': 'white'}),
                html.Div(id='bridge-list', style={'color': 'white'}),
            ]),
        ])
    
    elif tool == 'upgrades':
        return html.Div([
            html.H4("System Upgrade Planner", style={'color': 'white'}),
            
            html.Div([
                html.Label("Select System:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='selected-system',
                    options=[{'label': s, 'value': s} for s in system_list],
                    value=system_list[0] if system_list else None,
                    style={'margin-top': '5px'},
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Div(id='system-info', style={'color': 'white', 'margin-bottom': '15px'}),
            
            html.Hr(style={'border-color': '#555'}),
            
            html.Div([
                html.Label("Add Upgrade:", style={'color': 'white'}),
                html.Div([
                    dcc.Dropdown(
                        id='upgrade-type',
                        options=[
                            {'label': 'Mining Upgrade', 'value': 'mining'},
                            {'label': 'Ratting Upgrade', 'value': 'ratting'},
                            {'label': 'Belt Upgrade', 'value': 'belt'},
                        ],
                        value='mining',
                        style={'width': '200px', 'margin-bottom': '10px'},
                    ),
                    dcc.Dropdown(
                        id='upgrade-level',
                        options=[
                            {'label': 'Level 1', 'value': 1},
                            {'label': 'Level 2', 'value': 2},
                            {'label': 'Level 3', 'value': 3},
                        ],
                        value=1,
                        style={'width': '200px', 'margin-bottom': '10px'},
                    ),
                    html.Button("Add Upgrade", id='add-upgrade-btn', n_clicks=0, style=STYLE_BUTTON),
                ]),
            ]),
            
            html.Hr(style={'border-color': '#555'}),
            
            html.Div([
                html.H5("Quick Presets:", style={'color': 'white'}),
                html.Button("Max Mining", id='preset-mining-btn', n_clicks=0, style=STYLE_BUTTON),
                html.Button("Max Ratting", id='preset-ratting-btn', n_clicks=0, style=STYLE_BUTTON),
            ]),
        ])
    
    elif tool == 'mining':
        return html.Div([
            html.H4("Mining System Optimizer", style={'color': 'white'}),
            
            html.Div([
                html.Label("Industrial Hub:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='industrial-hub',
                    options=[{'label': s, 'value': s} for s in system_list],
                    value=system_list[0] if system_list else None,
                    style={'margin-top': '5px'},
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Div([
                html.Label("Number of Mining Systems:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='num-mining-systems',
                    options=[{'label': str(i), 'value': i} for i in range(5, 21, 5)],
                    value=10,
                    style={'margin-top': '5px'},
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Button("Run Optimization", id='run-mining-opt-btn', n_clicks=0, style=STYLE_BUTTON),
            
            html.Div(id='mining-results', style={'color': 'white', 'margin-top': '20px'}),
        ])
    
    elif tool == 'strategic':
        return html.Div([
            html.H4("Strategic Network Analysis", style={'color': 'white'}),
            
            html.Div([
                html.Label("Analysis Type:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='analysis-type',
                    options=[
                        {'label': 'Chokepoints', 'value': 'chokepoints'},
                        {'label': 'Traffic (Betweenness)', 'value': 'traffic'},
                        {'label': 'System Centrality', 'value': 'centrality'},
                        {'label': 'Distance Heatmap', 'value': 'distance'},
                    ],
                    value='chokepoints',
                    style={'margin-top': '5px'},
                ),
            ], style={'margin-bottom': '15px'}),
            
            html.Button("Run Analysis", id='run-analysis-btn', n_clicks=0, style=STYLE_BUTTON),
            
            html.Div(id='analysis-results', style={'color': 'white', 'margin-top': '20px'}),
        ])
    
    return html.Div([html.P("Select a tool to begin", style={'color': 'white'})])

@callback(
    Output('main-visualization', 'figure'),
    Output('metrics-display', 'children'),
    Input('tool-selector', 'value'),
    Input('reference-system', 'value'),
    Input('add-bridge-btn', 'n_clicks'),
    Input('selected-system', 'value'),
    State('bridge-from', 'value'),
    State('bridge-to', 'value'),
    State('app-state', 'data'),
)
def update_visualization(tool, reference_system, add_bridge_clicks, 
                        selected_system, bridge_from, bridge_to, state):
    """Update the right panel based on tool and actions"""
    
    # Determine which input triggered the callback
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if tool == 'ansiblex':
        # Create graph visualization with bridges
        fig = create_bridge_graph(G, state['bridges'], reference_system)
        
        # Calculate metrics
        if reference_system:
            distances = nx.single_source_shortest_path_length(G, reference_system)
            avg_distance = sum(distances.values()) / len(distances)
            metrics = html.Div([
                html.H4("Network Metrics"),
                html.P(f"Average jumps from {reference_system}: {avg_distance:.2f}"),
                html.P(f"Number of bridges: {len(state['bridges'])}"),
            ])
        else:
            metrics = html.Div([html.P("Select a reference system")])
        
        return fig, metrics
    
    elif tool == 'upgrades':
        # Create capacity gauges
        if selected_system and selected_system in G.nodes():
            power_capacity = G.nodes[selected_system].get('power', 2500)
            workforce_capacity = G.nodes[selected_system].get('workforce', 18000)
            
            # Calculate used capacity (from state)
            upgrades = state['system_upgrades'].get(selected_system, [])
            power_used = sum(u['power'] for u in upgrades)
            workforce_used = sum(u['workforce'] for u in upgrades)
            
            fig = create_capacity_gauges(power_capacity, power_used, 
                                        workforce_capacity, workforce_used)
            
            # Show upgrade list
            metrics = html.Div([
                html.H4(f"Upgrades for {selected_system}"),
                html.P(f"Power: {power_used} / {power_capacity} ({power_used/power_capacity*100:.1f}%)"),
                html.P(f"Workforce: {workforce_used} / {workforce_capacity} ({workforce_used/workforce_capacity*100:.1f}%)"),
            ])
        else:
            fig = go.Figure()
            metrics = html.Div([html.P("Select a system")])
        
        return fig, metrics
    
    elif tool == 'mining':
        # Show graph with highlighted mining systems
        fig = create_mining_graph(G, reference_system)
        metrics = html.Div([html.P("Mining optimization visualization")])
        return fig, metrics
    
    elif tool == 'strategic':
        # Show strategic analysis
        fig = create_strategic_graph(G)
        metrics = html.Div([html.P("Strategic network analysis")])
        return fig, metrics
    
    # Default
    fig = create_basic_graph(G)
    return fig, html.Div([html.P("Select a tool")])

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_basic_graph(G):
    """Create basic network visualization"""
    pos = nx.spring_layout(G, k=2)
    
    # Edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Nodes
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_text = list(G.nodes())
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(size=10, color='#4ECDC4'),
        textfont=dict(color='white', size=8),
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
    )
    
    return fig

def create_bridge_graph(G, bridges, reference_system):
    """Create graph with Ansiblex bridges highlighted"""
    # Similar to basic graph, but with bridges shown in different color
    return create_basic_graph(G)  # Simplified for now

def create_capacity_gauges(power_cap, power_used, workforce_cap, workforce_used):
    """Create capacity gauge visualization"""
    fig = go.Figure()
    
    # Power gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=power_used,
        title={'text': "Power Capacity"},
        domain={'x': [0, 0.45], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, power_cap]},
            'bar': {'color': "#4ECDC4"},
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': power_cap * 0.9
            }
        }
    ))
    
    # Workforce gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=workforce_used,
        title={'text': "Workforce Capacity"},
        domain={'x': [0.55, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, workforce_cap]},
            'bar': {'color': "#4ECDC4"},
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': workforce_cap * 0.9
            }
        }
    ))
    
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font={'color': 'white'},
    )
    
    return fig

def create_mining_graph(G, industrial_hub):
    """Create graph highlighting mining systems"""
    return create_basic_graph(G)  # Simplified for now

def create_strategic_graph(G):
    """Create strategic analysis visualization"""
    return create_basic_graph(G)  # Simplified for now

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("Pure Blind Planning Tool - Dash Application")
    print("="*70)
    print("\nStarting server...")
    print("Open your browser to: http://127.0.0.1:8050/")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    app.run_server(debug=True, host='127.0.0.1', port=8050)
