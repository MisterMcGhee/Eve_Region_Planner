"""
Pure Blind Region Planner - Graph Visualization Module
=======================================================

Phase 2: Graph Construction & Visualization

This module provides:
1. NetworkX graph construction from CSV data
2. 2D layout using actual 3D coordinates (x,y projection)
3. Interactive Plotly visualization with constellation color-coding
4. Hover tooltips and system information
5. Export capabilities

Usage:
    python graph_visualizer.py                    # Creates standalone HTML
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
                x=float(system['x']),
                y=float(system['y']),
                z=float(system['z']),
                moons=int(system['moons']),
                planets=int(system['planets']),
                belts=int(system['belts']),
                has_ice=bool(system['has_ice']),
                power_capacity=int(system['power_capacity']),
                workforce_capacity=int(system['workforce_capacity']),
            )

        # Add edges from gate connections
        # Only add edges if both systems are in Pure Blind (have coordinate data)
        internal_edges = 0
        border_edges = 0
        for _, gate in self.gates_df.iterrows():
            from_sys = gate['from_system']
            to_sys = gate['to_system']

            # Only add edge if both systems are in our dataset
            if from_sys in known_systems and to_sys in known_systems:
                self.graph.add_edge(from_sys, to_sys)
                internal_edges += 1
            else:
                border_edges += 1

        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {internal_edges} internal edges")
        print(f"Skipped {border_edges} border connections to external regions")

        # Validate connectivity
        if not nx.is_connected(self.graph):
            print("WARNING: Graph is not fully connected!")
            components = list(nx.connected_components(self.graph))
            print(f"Number of components: {len(components)}")
        else:
            print("✓ Graph is fully connected")

        return self.graph

    def calculate_layout(self, method: str = "planar") -> Dict[str, Tuple[float, float]]:
        """
        Calculate 2D layout from 3D coordinates

        Args:
            method: Layout method to use
                - "3d_projection": Direct x,y projection from 3D coordinates
                - "planar": Force-directed layout minimizing edge crossings (default)
                - "hybrid": Start with 3D projection, refine with force-directed

        Returns:
            Dictionary mapping system names to (x, y) positions
        """
        print(f"Calculating 2D layout using '{method}' method...")

        if method == "3d_projection":
            self.pos = self._layout_3d_projection()
        elif method == "planar":
            self.pos = self._layout_force_directed()
        elif method == "hybrid":
            self.pos = self._layout_hybrid()
        else:
            raise ValueError(f"Unknown layout method: {method}")

        print(f"✓ Layout calculated for {len(self.pos)} systems")

        # Count edge crossings for diagnostics
        crossings = self._count_edge_crossings()
        print(f"  Edge crossings: {crossings}")

        return self.pos

    def _layout_3d_projection(self) -> Dict[str, Tuple[float, float]]:
        """Direct projection from 3D coordinates (original method)"""
        pos = {}

        for node in self.graph.nodes():
            # Get 3D coordinates
            x = self.graph.nodes[node]['x']
            y = self.graph.nodes[node]['y']
            # z is ignored for 2D projection
            pos[node] = (x, y)

        # Normalize to 0-100 range
        return self._normalize_positions(pos)

    def _layout_force_directed(self) -> Dict[str, Tuple[float, float]]:
        """
        Force-directed layout to minimize edge crossings
        Uses NetworkX spring layout (Fruchterman-Reingold algorithm)
        """
        # Use spring layout with parameters tuned for readability
        pos = nx.spring_layout(
            self.graph,
            k=2.0,  # Optimal distance between nodes
            iterations=100,  # More iterations = better layout
            seed=42,  # Reproducible layout
            scale=100,  # Scale to 0-100 range
        )

        # Convert to our format
        return {node: (x, y) for node, (x, y) in pos.items()}

    def _layout_hybrid(self) -> Dict[str, Tuple[float, float]]:
        """
        Hybrid approach: Start with 3D projection, refine with force-directed
        Preserves general spatial relationships while reducing crossings
        """
        # Start with 3D projection
        initial_pos = self._layout_3d_projection()

        # Convert to format needed by spring_layout
        initial_pos_array = {node: np.array([x, y]) for node, (x, y) in initial_pos.items()}

        # Refine with force-directed, using initial positions
        pos = nx.spring_layout(
            self.graph,
            pos=initial_pos_array,
            k=1.5,
            iterations=50,  # Fewer iterations to preserve initial structure
            seed=42,
            scale=100,
        )

        # Convert back to our format
        return {node: (x, y) for node, (x, y) in pos.items()}

    def _normalize_positions(self, pos: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Normalize positions to 0-100 range"""
        all_x = [x for x, y in pos.values()]
        all_y = [y for x, y in pos.values()]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        normalized = {}
        for node, (x, y) in pos.items():
            norm_x = (x - min_x) / (max_x - min_x) * 100 if max_x != min_x else 50
            norm_y = (y - min_y) / (max_y - min_y) * 100 if max_y != min_y else 50
            normalized[node] = (norm_x, norm_y)

        return normalized

    def _count_edge_crossings(self) -> int:
        """
        Count the number of edge crossings in the current layout
        This is a simple geometric check
        """
        edges = list(self.graph.edges())
        crossings = 0

        for i, (a, b) in enumerate(edges):
            for c, d in edges[i+1:]:
                # Skip if edges share a vertex
                if a == c or a == d or b == c or b == d:
                    continue

                # Check if line segments intersect
                if self._segments_intersect(
                    self.pos[a], self.pos[b],
                    self.pos[c], self.pos[d]
                ):
                    crossings += 1

        return crossings

    def _segments_intersect(self, p1, p2, p3, p4) -> bool:
        """
        Check if line segments (p1,p2) and (p3,p4) intersect
        Uses the orientation method
        """
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

        return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

    def assign_constellation_colors(self) -> Dict[str, str]:
        """
        Assign unique colors to each constellation

        Returns:
            Dictionary mapping constellation names to hex colors
        """
        constellations = self.systems_df['constellation'].unique()

        # Use a color palette with good contrast
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
            '#E63946', '#A8DADC', '#457B9D', '#F4A261', '#E76F51',
        ]

        self.constellation_colors = {
            const: colors[i % len(colors)]
            for i, const in enumerate(sorted(constellations))
        }

        print(f"✓ Assigned colors to {len(self.constellation_colors)} constellations")
        return self.constellation_colors

    def create_plotly_figure(
        self,
        highlight_systems: Optional[List[str]] = None,
        show_labels: bool = True,
        title: str = "Pure Blind Region - System Map"
    ) -> go.Figure:
        """
        Create interactive Plotly visualization

        Args:
            highlight_systems: Optional list of systems to highlight
            show_labels: Whether to show system labels
            title: Title for the graph

        Returns:
            Plotly Figure object
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build_graph() first.")
        if not self.pos:
            raise ValueError("Layout not calculated. Call calculate_layout() first.")
        if not self.constellation_colors:
            self.assign_constellation_colors()

        print("Creating Plotly visualization...")

        # Create edge traces (gate connections)
        edge_traces = self._create_edge_traces()

        # Create node traces (systems, grouped by constellation)
        node_traces = self._create_node_traces(highlight_systems, show_labels)

        # Combine all traces
        data = edge_traces + node_traces

        # Create layout
        layout = go.Layout(
            title=dict(
                text=title,
                font=dict(size=24, color='white'),
                x=0.5,
                xanchor='center'
            ),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=60),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-5, 105]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-5, 105]
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
        )

        fig = go.Figure(data=data, layout=layout)
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
            line=dict(width=0.5, color='#444444'),
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

        # Group systems by constellation
        for constellation, color in self.constellation_colors.items():
            # Filter systems in this constellation
            systems_in_const = [
                node for node in self.graph.nodes()
                if self.graph.nodes[node]['constellation'] == constellation
            ]

            if not systems_in_const:
                continue

            # Positions
            node_x = [self.pos[node][0] for node in systems_in_const]
            node_y = [self.pos[node][1] for node in systems_in_const]

            # Labels
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

            # Determine marker size (highlight if specified)
            marker_size = 10
            if highlight_systems:
                marker_size = [
                    15 if node in highlight_systems else 10
                    for node in systems_in_const
                ]

            trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text' if show_labels else 'markers',
                text=node_text,
                textposition="top center",
                textfont=dict(size=8, color='white'),
                hovertext=hover_text,
                hoverinfo='text',
                marker=dict(
                    size=marker_size,
                    color=color,
                    line=dict(width=1, color='white')
                ),
                name=constellation,
                legendgroup=constellation,
            )

            traces.append(trace)

        return traces

    def export_html(self, filename: str = "pure_blind_map.html") -> None:
        """
        Export visualization to standalone HTML file

        Args:
            filename: Output filename
        """
        fig = self.create_plotly_figure()
        fig.write_html(filename)
        print(f"✓ Exported to {filename}")

    def export_graph_data(self, filename: str = "graph_data.json") -> None:
        """
        Export graph data to JSON for use in other applications

        Args:
            filename: Output filename
        """
        data = {
            'nodes': [],
            'edges': [],
            'constellations': self.constellation_colors,
        }

        for node in self.graph.nodes():
            attrs = self.graph.nodes[node]
            x, y = self.pos[node]
            data['nodes'].append({
                'id': node,
                'x': x,
                'y': y,
                **{k: v for k, v in attrs.items() if k not in ['x', 'y', 'z']}
            })

        for edge in self.graph.edges():
            data['edges'].append({
                'from': edge[0],
                'to': edge[1],
            })

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Exported graph data to {filename}")

    def get_system_info(self, system_name: str) -> Dict:
        """
        Get detailed information about a system

        Args:
            system_name: Name of the system

        Returns:
            Dictionary with system attributes
        """
        if system_name not in self.graph.nodes():
            return None

        return dict(self.graph.nodes[system_name])

    def get_neighbors(self, system_name: str) -> List[str]:
        """
        Get all neighboring systems (connected by gates)

        Args:
            system_name: Name of the system

        Returns:
            List of neighboring system names
        """
        if system_name not in self.graph.nodes():
            return []

        return list(self.graph.neighbors(system_name))

    def get_constellation_systems(self, constellation: str) -> List[str]:
        """
        Get all systems in a constellation

        Args:
            constellation: Constellation name

        Returns:
            List of system names
        """
        return [
            node for node in self.graph.nodes()
            if self.graph.nodes[node]['constellation'] == constellation
        ]

    def calculate_distance(self, system_a: str, system_b: str) -> int:
        """
        Calculate jump distance between two systems

        Args:
            system_a: First system name
            system_b: Second system name

        Returns:
            Number of jumps, or -1 if not connected
        """
        try:
            return nx.shortest_path_length(self.graph, system_a, system_b)
        except nx.NetworkXNoPath:
            return -1

    def get_route(self, system_a: str, system_b: str) -> List[str]:
        """
        Get shortest route between two systems

        Args:
            system_a: First system name
            system_b: Second system name

        Returns:
            List of systems in route, or empty list if no path
        """
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
    print("Pure Blind Region Planner - Phase 2: Graph Visualization")
    print("="*70)
    print()

    # Create visualizer
    viz = GraphVisualizer()

    # Load data
    viz.load_data()

    # Build graph
    viz.build_graph()

    # Assign colors (before layout)
    viz.assign_constellation_colors()

    print()
    print("="*70)
    print("Testing Different Layout Methods")
    print("="*70)
    print()

    # Test all three layout methods and compare
    layouts = {
        "3d_projection": "Pure Blind Map - 3D Projection",
        "planar": "Pure Blind Map - Force-Directed (Minimal Crossings)",
        "hybrid": "Pure Blind Map - Hybrid Layout"
    }

    crossing_results = {}

    for method, title in layouts.items():
        print(f"Generating {method} layout...")
        viz.calculate_layout(method=method)

        # Store crossing count
        crossing_results[method] = viz._count_edge_crossings()

        # Export visualization
        filename = f"pure_blind_map_{method}.html"
        fig = viz.create_plotly_figure(title=title)
        fig.write_html(filename)
        print(f"  Exported to {filename}")
        print()

    # Use the best layout for the main export
    best_method = min(crossing_results, key=crossing_results.get)
    print(f"Best layout method: {best_method} ({crossing_results[best_method]} crossings)")
    print(f"Creating main visualization with {best_method} layout...")

    viz.calculate_layout(method=best_method)
    viz.export_html("pure_blind_map.html")

    # Export graph data
    viz.export_graph_data("pure_blind_graph_data.json")

    # Print statistics
    print()
    print("="*70)
    print("Graph Statistics:")
    print("="*70)
    print(f"Total Systems: {viz.graph.number_of_nodes()}")
    print(f"Total Gate Connections: {viz.graph.number_of_edges()}")
    print(f"Constellations: {len(viz.constellation_colors)}")
    print()

    # Constellation breakdown
    print("Systems per Constellation:")
    for constellation in sorted(viz.constellation_colors.keys()):
        systems = viz.get_constellation_systems(constellation)
        print(f"  {constellation}: {len(systems)} systems")

    print()
    print("="*70)
    print("Layout Comparison:")
    print("="*70)
    for method, crossings in sorted(crossing_results.items(), key=lambda x: x[1]):
        print(f"  {method:20s}: {crossings:4d} edge crossings")

    print()
    print("="*70)
    print("✓ Phase 2 Complete!")
    print(f"Main map: pure_blind_map.html (using {best_method} layout)")
    print("Comparison maps:")
    for method in layouts.keys():
        print(f"  - pure_blind_map_{method}.html")
    print("="*70)


if __name__ == "__main__":
    main()
