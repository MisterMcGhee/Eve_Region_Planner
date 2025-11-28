"""
Pure Blind Region Planner - Graph Visualization Module
=======================================================

Kamada-Kawai Layout with Manual Positioning

This module provides:
1. NetworkX graph construction from CSV data
2. Kamada-Kawai layout (optimizes for hop distance visualization)
3. Interactive Plotly visualization with draggable nodes
4. Save/load custom positions for manual fine-tuning

Usage:
    python graph_visualizer.py                    # Creates interactive HTML
    from graph_visualizer import GraphVisualizer  # Use in Dash app
"""

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional


class GraphVisualizer:
    """
    Handles graph construction and visualization for Pure Blind region
    """

    def __init__(self, data_dir: str = "data/pure_blind_data"):
        """
        Initialize the visualizer with data directory

        Args:
            data_dir: Path to directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.graph = None
        self.systems_df = None
        self.constellation_colors = {}
        self.pos = {}  # 2D positions for nodes

    def load_data(self) -> None:
        """Load all data from CSV files"""
        print("Loading system data...")
        self.systems_df = pd.read_csv(self.data_dir / "systems_full.csv")
        print(f"Loaded {len(self.systems_df)} systems")

        # Load gate connections
        print("Loading gate connections...")
        gates_internal = pd.read_csv(self.data_dir / "gates_internal.csv")
        gates_border = pd.read_csv(self.data_dir / "gates_border.csv")

        # Combine all gates
        self.gates_df = pd.concat([gates_internal, gates_border], ignore_index=True)
        print(f"Loaded {len(self.gates_df)} gate connections")

    def build_graph(self) -> nx.Graph:
        """
        Build NetworkX graph from loaded data

        Returns:
            NetworkX Graph with all system attributes
        """
        print("Building NetworkX graph...")
        self.graph = nx.Graph()

        # Create set of system names we have data for
        known_systems = set(self.systems_df['system_name'])

        # Add nodes with attributes
        for _, system in self.systems_df.iterrows():
            self.graph.add_node(
                system['system_name'],
                system_id=int(system['system_id']),
                constellation=system['constellation'],
                constellation_id=int(system['constellation_id']),
                security=float(system['security']),
                moons=int(system['moons']),
                planets=int(system['planets']),
                belts=int(system['belts']),
                has_ice=bool(system['has_ice']),
                power_capacity=int(system['power_capacity']),
                workforce_capacity=int(system['workforce_capacity']),
            )

        # Add edges from gate connections (only internal Pure Blind connections)
        internal_edges = 0
        border_edges = 0
        for _, gate in self.gates_df.iterrows():
            from_sys = gate['from_system']
            to_sys = gate['to_system']

            if from_sys in known_systems and to_sys in known_systems:
                self.graph.add_edge(from_sys, to_sys)
                internal_edges += 1
            else:
                border_edges += 1

        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {internal_edges} internal edges")
        print(f"Skipped {border_edges} border connections to external regions")

        # Validate connectivity
        if nx.is_connected(self.graph):
            print("✓ Graph is fully connected")
        else:
            print("WARNING: Graph is not fully connected!")

        return self.graph

    def calculate_layout(self, scale: float = 60, positions_file: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
        """
        Calculate 2D layout using Kamada-Kawai algorithm

        Kamada-Kawai optimizes for graph-theoretic distances, meaning systems
        that are N jumps apart will appear approximately N visual units apart.

        Args:
            scale: Scale factor for layout (default 60 for compact view, range 40-100)
                   Lower values = more compact, higher = more spread out
            positions_file: Optional JSON file to load saved manual positions

        Returns:
            Dictionary mapping system names to (x, y) positions
        """
        # Try to load saved positions first
        if positions_file and Path(positions_file).exists():
            print(f"Loading saved positions from {positions_file}...")
            with open(positions_file, 'r') as f:
                saved_data = json.load(f)
                self.pos = {node: tuple(pos) for node, pos in saved_data.items()}
            print(f"✓ Loaded {len(self.pos)} saved positions")
            return self.pos

        # Generate new layout with Kamada-Kawai
        print(f"Calculating layout using Kamada-Kawai (scale={scale})...")
        pos = nx.kamada_kawai_layout(self.graph, scale=scale)
        self.pos = {node: (x, y) for node, (x, y) in pos.items()}

        print(f"✓ Layout calculated for {len(self.pos)} systems")
        crossings = self._count_edge_crossings()
        print(f"  Edge crossings: {crossings}")

        return self.pos

    def save_positions(self, filename: str = "positions_manual.json") -> None:
        """
        Save current node positions to JSON file for manual editing/reloading

        Positions are rounded to nearest integers for easier manual editing.

        Args:
            filename: Output filename
        """
        # Round positions to integers for easier editing
        rounded_positions = {node: [round(x), round(y)] for node, (x, y) in self.pos.items()}

        with open(filename, 'w') as f:
            json.dump(rounded_positions, f, indent=2)
        print(f"✓ Saved positions to {filename}")
        print(f"  Positions rounded to integers for easier editing")
        print(f"  You can manually edit this file and reload with calculate_layout(positions_file='{filename}')")

    def _count_edge_crossings(self) -> int:
        """Count the number of edge crossings in the current layout"""
        edges = list(self.graph.edges())
        crossings = 0

        for i, (a, b) in enumerate(edges):
            for c, d in edges[i+1:]:
                if a == c or a == d or b == c or b == d:
                    continue

                if self._segments_intersect(
                    self.pos[a], self.pos[b],
                    self.pos[c], self.pos[d]
                ):
                    crossings += 1

        return crossings

    def _segments_intersect(self, p1, p2, p3, p4) -> bool:
        """Check if line segments (p1,p2) and (p3,p4) intersect"""
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

        return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

    def assign_constellation_colors(self) -> Dict[str, str]:
        """Assign unique colors to each constellation"""
        constellations = self.systems_df['constellation'].unique()

        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
            '#E63946', '#A8DADC', '#457B9D', '#F4A261', '#E76F51',
        ]

        self.constellation_colors = {
            const: colors[i % len(colors)]
            for i, const in enumerate(sorted(constellations))
        }

        return self.constellation_colors

    def create_plotly_figure(
        self,
        highlight_systems: Optional[List[str]] = None,
        show_labels: bool = True,
        title: str = "Pure Blind Region - Kamada-Kawai Layout",
        editable: bool = True
    ) -> go.Figure:
        """
        Create interactive Plotly visualization

        Args:
            highlight_systems: Optional list of systems to highlight
            show_labels: Whether to show system labels
            title: Title for the graph
            editable: Enable draggable nodes for manual positioning

        Returns:
            Plotly Figure object
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build_graph() first.")
        if not self.pos:
            raise ValueError("Layout not calculated. Call calculate_layout() first.")
        if not self.constellation_colors:
            self.assign_constellation_colors()

        print("Creating interactive Plotly visualization...")

        # Create edge traces
        edge_traces = self._create_edge_traces()

        # Create node traces
        node_traces = self._create_node_traces(highlight_systems, show_labels)

        # Combine all traces
        data = edge_traces + node_traces

        # Create layout
        layout = go.Layout(
            title=dict(
                text=title + (" (Drag nodes to reposition)" if editable else ""),
                font=dict(size=20, color='white'),
                x=0.5,
                xanchor='center'
            ),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=60),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(100, 100, 100, 0.3)',
                dtick=10,  # Grid line every 10 units
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='rgba(150, 150, 150, 0.5)',
                showticklabels=True,
                tickfont=dict(size=10, color='rgba(200, 200, 200, 0.7)'),
                range=[-10, 110]
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(100, 100, 100, 0.3)',
                dtick=10,  # Grid line every 10 units
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='rgba(150, 150, 150, 0.5)',
                showticklabels=True,
                tickfont=dict(size=10, color='rgba(200, 200, 200, 0.7)'),
                range=[-10, 110],
                scaleanchor="x",
                scaleratio=1,
            ),
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(42, 42, 42, 0.8)',
                bordercolor='white',
                borderwidth=1,
            ),
            height=800,
            width=1000,
        )

        fig = go.Figure(data=data, layout=layout)

        # Configure for manual editing if enabled
        if editable:
            fig.update_layout(
                dragmode='pan',  # Allow panning
                modebar_add=['drawline', 'drawopenpath', 'eraseshape']
            )

        print("✓ Plotly figure created")
        return fig

    def _create_edge_traces(self) -> List[go.Scatter]:
        """Create traces for gate connections"""
        edge_x = []
        edge_y = []

        for edge in self.graph.edges():
            x0, y0 = self.pos[edge[0]]
            x1, y1 = self.pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color='#555555'),
            hoverinfo='none',
            mode='lines',
            name='Stargates',
            showlegend=False,
        )

        return [edge_trace]

    def _create_node_traces(
        self,
        highlight_systems: Optional[List[str]] = None,
        show_labels: bool = True
    ) -> List[go.Scatter]:
        """Create traces for system nodes, grouped by constellation"""
        traces = []

        for constellation, color in self.constellation_colors.items():
            systems_in_const = [
                node for node in self.graph.nodes()
                if self.graph.nodes[node]['constellation'] == constellation
            ]

            if not systems_in_const:
                continue

            node_x = [self.pos[node][0] for node in systems_in_const]
            node_y = [self.pos[node][1] for node in systems_in_const]
            node_text = systems_in_const if show_labels else ['' for _ in systems_in_const]

            # Hover info
            hover_text = []
            for node in systems_in_const:
                attrs = self.graph.nodes[node]
                hover_info = (
                    f"<b>{node}</b><br>"
                    f"Constellation: {attrs['constellation']}<br>"
                    f"Security: {attrs['security']:.2f}<br>"
                    f"Moons: {attrs['moons']}<br>"
                    f"Ice: {'Yes' if attrs['has_ice'] else 'No'}<br>"
                    f"Power: {attrs['power_capacity']}<br>"
                    f"Workforce: {attrs['workforce_capacity']}"
                )
                hover_text.append(hover_info)

            # Marker size
            marker_size = 12
            if highlight_systems:
                marker_size = [
                    16 if node in highlight_systems else 12
                    for node in systems_in_const
                ]

            trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text' if show_labels else 'markers',
                text=node_text,
                textposition="top center",
                textfont=dict(size=9, color='white'),
                hovertext=hover_text,
                hoverinfo='text',
                marker=dict(
                    size=marker_size,
                    color=color,
                    line=dict(width=1.5, color='white')
                ),
                name=constellation,
                legendgroup=constellation,
            )

            traces.append(trace)

        return traces

    def export_html(self, filename: str = "pure_blind_map.html", editable: bool = True) -> None:
        """
        Export visualization to standalone HTML file with grid toggle

        Args:
            filename: Output filename
            editable: Enable node dragging for manual positioning
        """
        fig = self.create_plotly_figure(editable=editable)

        # Custom HTML with grid toggle button
        html_template = """
        <html>
        <head>
            <meta charset="utf-8" />
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #1a1a1a;
                    font-family: Arial, sans-serif;
                }}
                #controls {{
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    z-index: 1000;
                    background-color: rgba(42, 42, 42, 0.9);
                    padding: 10px 15px;
                    border-radius: 5px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}
                #gridToggle {{
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    cursor: pointer;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                #gridToggle:hover {{
                    background-color: #45a049;
                }}
                #gridToggle.off {{
                    background-color: #f44336;
                }}
                #gridToggle.off:hover {{
                    background-color: #da190b;
                }}
            </style>
        </head>
        <body>
            <div id="controls">
                <button id="gridToggle" class="on">Grid: ON</button>
            </div>
            <div id="plotDiv"></div>
            <script>
                var plotDiv = document.getElementById('plotDiv');
                var gridOn = true;

                // Plot the figure
                {plot_json}

                // Grid toggle functionality
                document.getElementById('gridToggle').addEventListener('click', function() {{
                    gridOn = !gridOn;
                    var button = this;

                    var update = {{
                        'xaxis.showgrid': gridOn,
                        'xaxis.showticklabels': gridOn,
                        'yaxis.showgrid': gridOn,
                        'yaxis.showticklabels': gridOn
                    }};

                    Plotly.relayout(plotDiv, update);

                    if (gridOn) {{
                        button.textContent = 'Grid: ON';
                        button.className = 'on';
                    }} else {{
                        button.textContent = 'Grid: OFF';
                        button.className = 'off';
                    }}
                }});
            </script>
        </body>
        </html>
        """

        # Generate Plotly JSON
        plot_json = fig.to_html(include_plotlyjs=False, div_id='plotDiv')

        # Write custom HTML
        with open(filename, 'w') as f:
            f.write(html_template.format(plot_json=plot_json))

        print(f"✓ Exported to {filename}")
        print(f"  Grid toggle button added (top-right corner)")

        if editable:
            print(f"  NOTE: Plotly drag-and-drop in HTML is limited.")
            print(f"  For full manual positioning, use save_positions() to export,")
            print(f"  then manually edit the JSON file and reload.")

    # Utility methods
    def get_system_info(self, system_name: str) -> Dict:
        """Get detailed information about a system"""
        if system_name not in self.graph.nodes():
            return None
        return dict(self.graph.nodes[system_name])

    def get_neighbors(self, system_name: str) -> List[str]:
        """Get all neighboring systems (connected by gates)"""
        if system_name not in self.graph.nodes():
            return []
        return list(self.graph.neighbors(system_name))

    def get_constellation_systems(self, constellation: str) -> List[str]:
        """Get all systems in a constellation"""
        return [
            node for node in self.graph.nodes()
            if self.graph.nodes[node]['constellation'] == constellation
        ]

    def calculate_distance(self, system_a: str, system_b: str) -> int:
        """Calculate jump distance between two systems"""
        try:
            return nx.shortest_path_length(self.graph, system_a, system_b)
        except nx.NetworkXNoPath:
            return -1

    def get_route(self, system_a: str, system_b: str) -> List[str]:
        """Get shortest route between two systems"""
        try:
            return nx.shortest_path(self.graph, system_a, system_b)
        except nx.NetworkXNoPath:
            return []


def main():
    """
    Main function for standalone execution
    Creates visualization and exports to HTML
    """
    print("="*70)
    print("Pure Blind Region Planner - Kamada-Kawai Visualization")
    print("="*70)
    print()

    # Create visualizer
    viz = GraphVisualizer()

    # Load data
    viz.load_data()

    # Build graph
    viz.build_graph()

    # Assign constellation colors
    viz.assign_constellation_colors()

    # Calculate layout (compact view with scale=60)
    # If positions file exists, it will be loaded; otherwise Kamada-Kawai generates new positions
    print()
    positions_file = "positions_kamada_kawai.json"
    positions_existed = Path(positions_file).exists()

    if positions_existed:
        print(f"Loading existing positions from {positions_file}...")
    else:
        print("Generating Kamada-Kawai layout...")
    viz.calculate_layout(scale=60, positions_file=positions_file)

    # Export main visualization
    print()
    viz.export_html("pure_blind_map.html", editable=True)

    # Save positions only if they were newly generated (not loaded from file)
    if not positions_existed:
        viz.save_positions(positions_file)

    # Print statistics
    print()
    print("="*70)
    print("Graph Statistics:")
    print("="*70)
    print(f"Total Systems: {viz.graph.number_of_nodes()}")
    print(f"Total Gate Connections: {viz.graph.number_of_edges()}")
    print(f"Constellations: {len(viz.constellation_colors)}")
    print()

    print("Systems per Constellation:")
    for constellation in sorted(viz.constellation_colors.keys()):
        systems = viz.get_constellation_systems(constellation)
        print(f"  {constellation}: {len(systems)} systems")

    print()
    print("="*70)
    print("✓ Visualization Complete!")
    print("="*70)
    print()
    print("Main map: pure_blind_map.html")
    print("  - Open in browser to view")
    print("  - Zoom/pan controls enabled")
    print()
    print("Manual Positioning:")
    print("  1. Edit positions_kamada_kawai.json to manually adjust node positions")
    print("  2. Run: viz.calculate_layout(positions_file='positions_kamada_kawai.json')")
    print("  3. Regenerate visualization with custom positions")
    print("="*70)


if __name__ == "__main__":
    main()
