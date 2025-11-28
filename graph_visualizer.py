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

    def calculate_layout(self, method: str = "kamada_kawai", scale: float = 80) -> Dict[str, Tuple[float, float]]:
        """
        Calculate 2D layout using Kamada-Kawai algorithm

        Kamada-Kawai optimizes for graph-theoretic distances, meaning systems
        that are N jumps apart will appear approximately N visual units apart.

        Args:
            method: Layout method (currently only "kamada_kawai" supported)
            scale: Scale factor for layout (default 80, range 50-100)
                   Lower values = more compact, higher = more spread out

        Returns:
            Dictionary mapping system names to (x, y) positions
        """
        print(f"Calculating layout using Kamada-Kawai (scale={scale})...")

        if method != "kamada_kawai":
            print(f"Warning: Only 'kamada_kawai' method supported. Using Kamada-Kawai.")

        # Use Kamada-Kawai layout - optimizes for graph-theoretic distances
        pos = nx.kamada_kawai_layout(self.graph, scale=scale)
        self.pos = {node: (x, y) for node, (x, y) in pos.items()}

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

    def _layout_planar(self) -> Dict[str, Tuple[float, float]]:
        """
        Pure topological planar layout - ignores coordinates completely
        Uses planar layout if graph is planar, otherwise best alternative
        """
        # Check if graph is actually planar
        is_planar, embedding = nx.check_planarity(self.graph)

        if is_planar:
            print("  Graph IS planar! Using planar_layout for zero crossings")
            # Use the planar layout algorithm
            pos = nx.planar_layout(self.graph, scale=100)
            return {node: (x, y) for node, (x, y) in pos.items()}
        else:
            print("  Graph is NOT planar - using Kamada-Kawai for minimal crossings")
            # Fall back to Kamada-Kawai which generally works well for non-planar graphs
            return self._layout_kamada_kawai()

    def _layout_kamada_kawai(self) -> Dict[str, Tuple[float, float]]:
        """
        Kamada-Kawai layout - optimizes for graph-theoretic distances
        Often produces better results than spring layout for path clarity
        """
        pos = nx.kamada_kawai_layout(self.graph, scale=100)
        return {node: (x, y) for node, (x, y) in pos.items()}

    def _layout_spectral(self) -> Dict[str, Tuple[float, float]]:
        """
        Spectral layout - uses eigenvectors of graph Laplacian
        Very fast and often produces good results for visualization
        """
        pos = nx.spectral_layout(self.graph, scale=100)
        return {node: (x, y) for node, (x, y) in pos.items()}

    def _layout_constellation_clustered(self) -> Dict[str, Tuple[float, float]]:
        """
        Constellation-clustered layout using Kamada-Kawai

        Strategy:
        1. Layout each constellation separately using Kamada-Kawai
        2. Create meta-graph of constellations (edges between constellations)
        3. Layout the meta-graph using Kamada-Kawai
        4. Position constellation sub-layouts within their meta-positions

        This should reduce crossings within constellations while maintaining
        overall graph structure.
        """
        print("  Clustering by constellation...")

        # Get all constellations
        constellations = {}
        for node in self.graph.nodes():
            const = self.graph.nodes[node]['constellation']
            if const not in constellations:
                constellations[const] = []
            constellations[const].append(node)

        # Layout each constellation separately
        constellation_layouts = {}
        for const, systems in constellations.items():
            # Create subgraph for this constellation
            subgraph = self.graph.subgraph(systems)

            # Layout the subgraph (scale smaller for individual constellations)
            if len(systems) > 1:
                sub_pos = nx.kamada_kawai_layout(subgraph, scale=15)
            else:
                # Single node - place at origin
                sub_pos = {systems[0]: (0, 0)}

            constellation_layouts[const] = sub_pos

        # Create meta-graph of constellations
        # Edge exists if any system in const_a connects to any system in const_b
        meta_graph = nx.Graph()
        meta_graph.add_nodes_from(constellations.keys())

        for const_a in constellations:
            for const_b in constellations:
                if const_a >= const_b:  # Avoid duplicates and self-loops
                    continue

                # Check if there's an edge between these constellations
                for sys_a in constellations[const_a]:
                    for sys_b in constellations[const_b]:
                        if self.graph.has_edge(sys_a, sys_b):
                            meta_graph.add_edge(const_a, const_b)
                            break
                    if meta_graph.has_edge(const_a, const_b):
                        break

        # Layout the meta-graph
        if len(meta_graph.nodes()) > 1:
            meta_pos = nx.kamada_kawai_layout(meta_graph, scale=100)
        else:
            meta_pos = {list(meta_graph.nodes())[0]: (50, 50)}

        # Combine: place each constellation's layout at its meta-position
        final_pos = {}
        for const, systems in constellations.items():
            meta_x, meta_y = meta_pos[const]

            for system in systems:
                sub_x, sub_y = constellation_layouts[const][system]
                # Offset by meta position
                final_pos[system] = (meta_x + sub_x, meta_y + sub_y)

        return final_pos

    def _layout_dotlan(self) -> Dict[str, Tuple[float, float]]:
        """
        Dotlan-style layout - matches Dotlan EVE map appearance

        Strategy:
        1. Layout each constellation individually (planar if possible, else kamada-kawai)
        2. Create meta-graph of constellation connections
        3. Position constellations with generous spacing for visual clarity
        4. Ensure 0 or minimal crossings

        This mimics Dotlan's hand-tuned appearance with strong constellation clustering.
        """
        print("  Creating Dotlan-style layout with constellation clustering...")

        # Get all constellations and their systems
        constellations = {}
        for node in self.graph.nodes():
            const = self.graph.nodes[node]['constellation']
            if const not in constellations:
                constellations[const] = []
            constellations[const].append(node)

        print(f"  Laying out {len(constellations)} constellations...")

        # Layout each constellation separately
        constellation_layouts = {}
        constellation_sizes = {}

        for const, systems in constellations.items():
            # Create subgraph for this constellation
            subgraph = self.graph.subgraph(systems)

            if len(systems) == 1:
                # Single node - place at origin
                constellation_layouts[const] = {systems[0]: (0, 0)}
                constellation_sizes[const] = (0, 0, 0, 0)  # min_x, max_x, min_y, max_y
            else:
                # Try planar layout first for this constellation
                is_planar, _ = nx.check_planarity(subgraph)

                if is_planar and len(systems) > 2:
                    # Use planar layout for 0 crossings within constellation
                    sub_pos = nx.planar_layout(subgraph, scale=20)
                else:
                    # Use kamada-kawai for small or non-planar constellations
                    sub_pos = nx.kamada_kawai_layout(subgraph, scale=20)

                constellation_layouts[const] = {node: (x, y) for node, (x, y) in sub_pos.items()}

                # Calculate bounding box
                xs = [x for x, y in sub_pos.values()]
                ys = [y for x, y in sub_pos.values()]
                constellation_sizes[const] = (min(xs), max(xs), min(ys), max(ys))

        # Create meta-graph of constellations (similar to earlier method)
        meta_graph = nx.Graph()
        meta_graph.add_nodes_from(constellations.keys())

        # Add edges between constellations that have inter-constellation connections
        for const_a in constellations:
            for const_b in constellations:
                if const_a >= const_b:
                    continue

                # Check if there's an edge between these constellations
                for sys_a in constellations[const_a]:
                    for sys_b in constellations[const_b]:
                        if self.graph.has_edge(sys_a, sys_b):
                            meta_graph.add_edge(const_a, const_b)
                            break
                    if meta_graph.has_edge(const_a, const_b):
                        break

        # Layout the meta-graph with generous spacing
        if len(meta_graph.nodes()) > 1:
            # Use kamada-kawai for meta-graph for good separation
            meta_pos = nx.kamada_kawai_layout(meta_graph, scale=150)  # Larger scale for spacing
        else:
            meta_pos = {list(meta_graph.nodes())[0]: (50, 50)}

        # Combine: place each constellation's layout at its meta-position
        # Add padding between constellations for Dotlan-style visual separation
        final_pos = {}
        padding = 30  # Extra space between constellations

        for const, systems in constellations.items():
            meta_x, meta_y = meta_pos[const]

            for system in systems:
                sub_x, sub_y = constellation_layouts[const][system]
                # Offset by meta position
                final_pos[system] = (meta_x + sub_x, meta_y + sub_y)

        print(f"  Dotlan-style layout complete with visual constellation separation")
        return final_pos

    def _layout_grid(self) -> Dict[str, Tuple[float, float]]:
        """
        Grid-snapped layout

        Strategy:
        1. Use Kamada-Kawai to get initial positions
        2. Snap positions to a grid (reduces visual clutter)
        3. Use grid cells that are large enough to avoid overlaps

        This creates a more "organized" looking graph while maintaining
        topological relationships.
        """
        print("  Snapping to grid...")

        # Start with Kamada-Kawai layout
        initial_pos = self._layout_kamada_kawai()

        # Determine grid size based on number of nodes
        # We want enough grid cells to avoid too many collisions
        num_nodes = len(initial_pos)
        grid_size = int(np.ceil(np.sqrt(num_nodes * 2)))  # 2x oversampling
        cell_size = 100.0 / grid_size

        print(f"  Using {grid_size}x{grid_size} grid (cell size: {cell_size:.1f})")

        # Snap each position to nearest grid point
        grid_pos = {}
        occupied = set()

        # Sort nodes by their initial position to process consistently
        sorted_nodes = sorted(initial_pos.keys(),
                            key=lambda n: (initial_pos[n][0], initial_pos[n][1]))

        for node in sorted_nodes:
            x, y = initial_pos[node]

            # Find nearest grid point
            grid_x = round(x / cell_size) * cell_size
            grid_y = round(y / cell_size) * cell_size

            # If occupied, find nearest unoccupied grid point
            if (grid_x, grid_y) in occupied:
                # Search in expanding square around the desired position
                for radius in range(1, grid_size):
                    found = False
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            if abs(dx) != radius and abs(dy) != radius:
                                continue  # Only check perimeter

                            test_x = grid_x + dx * cell_size
                            test_y = grid_y + dy * cell_size

                            if (test_x, test_y) not in occupied:
                                grid_x, grid_y = test_x, test_y
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break

            grid_pos[node] = (grid_x, grid_y)
            occupied.add((grid_x, grid_y))

        # Normalize to 0-100 range
        return self._normalize_positions(grid_pos)

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

    def analyze_layout_preservation(self) -> Dict:
        """
        Analyze what information is preserved in the current layout

        Returns:
            Dictionary with analysis metrics
        """
        if not self.pos:
            raise ValueError("No layout calculated. Call calculate_layout() first.")

        analysis = {
            'graph_distance_correlation': 0.0,
            'euclidean_distance_correlation': 0.0,
            'constellation_cohesion': 0.0,
        }

        # 1. Graph-theoretic distance vs Euclidean distance correlation
        # This tells us how well the layout preserves hop distances
        graph_distances = []
        euclidean_distances = []

        nodes = list(self.graph.nodes())
        for i, node_a in enumerate(nodes):
            for node_b in nodes[i+1:]:
                # Graph distance (hop count)
                graph_dist = nx.shortest_path_length(self.graph, node_a, node_b)
                graph_distances.append(graph_dist)

                # Euclidean distance in layout
                x1, y1 = self.pos[node_a]
                x2, y2 = self.pos[node_b]
                euclidean_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                euclidean_distances.append(euclidean_dist)

        # Calculate Pearson correlation
        if len(graph_distances) > 1:
            correlation = np.corrcoef(graph_distances, euclidean_distances)[0, 1]
            analysis['graph_distance_correlation'] = correlation

        # 2. Constellation cohesion - how well are constellations clustered?
        # Measure average distance within constellation vs between constellations
        within_const_distances = []
        between_const_distances = []

        for node_a in nodes:
            for node_b in nodes:
                if node_a >= node_b:
                    continue

                const_a = self.graph.nodes[node_a]['constellation']
                const_b = self.graph.nodes[node_b]['constellation']

                x1, y1 = self.pos[node_a]
                x2, y2 = self.pos[node_b]
                euclidean_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                if const_a == const_b:
                    within_const_distances.append(euclidean_dist)
                else:
                    between_const_distances.append(euclidean_dist)

        if within_const_distances and between_const_distances:
            avg_within = np.mean(within_const_distances)
            avg_between = np.mean(between_const_distances)
            # Cohesion score: ratio of between/within (higher = better clustering)
            analysis['constellation_cohesion'] = avg_between / avg_within if avg_within > 0 else 0

        return analysis


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
    print("Testing Layout Methods")
    print("="*70)
    print()

    # Test layout methods
    layouts = {
        # Dotlan-style (primary focus)
        "dotlan": "Pure Blind - Dotlan Style (Constellation Clustered)",

        # Topological (ignore coordinates, optimize for path clarity)
        "kamada_kawai": "Pure Blind - Kamada-Kawai",
        "planar": "Pure Blind - Planar (0 crossings if planar)",

        # For comparison
        "constellation_clustered": "Pure Blind - Constellation Clustered (old)",
        "grid": "Pure Blind - Grid Layout",
        "spectral": "Pure Blind - Spectral",
        "3d_projection": "Pure Blind - 3D Projection (Coordinate-based)",
        "hybrid": "Pure Blind - Hybrid (Coord + Force-directed)",
    }

    crossing_results = {}
    analysis_results = {}

    for method, title in layouts.items():
        print(f"Generating {method} layout...")
        viz.calculate_layout(method=method)

        # Store crossing count
        crossing_results[method] = viz._count_edge_crossings()

        # Analyze what's preserved
        analysis = viz.analyze_layout_preservation()
        analysis_results[method] = analysis
        print(f"  Distance correlation: {analysis['graph_distance_correlation']:.3f}")
        print(f"  Constellation cohesion: {analysis['constellation_cohesion']:.2f}")

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
    print("Layout Comparison Summary:")
    print("="*70)

    # Separate layout types
    dotlan_style = ["dotlan"]
    topological = ["kamada_kawai", "planar", "spectral"]
    clustered = ["constellation_clustered", "grid"]
    coord_based = ["3d_projection", "hybrid"]

    print("\nDOTLAN-STYLE LAYOUT (matches Dotlan EVE maps):")
    print("-" * 70)
    print(f"{'Method':<25} {'Crossings':>10} {'Dist.Corr':>12} {'Const.Cohesion':>15}")
    print("-" * 70)
    for method in dotlan_style:
        if method in crossing_results:
            analysis = analysis_results[method]
            print(f"{method:<25} {crossing_results[method]:>10} "
                  f"{analysis['graph_distance_correlation']:>12.3f} "
                  f"{analysis['constellation_cohesion']:>15.2f}")

    print("\nTOPOLOGICAL LAYOUTS (ignore coordinates, optimize for clarity):")
    print("-" * 70)
    print(f"{'Method':<25} {'Crossings':>10} {'Dist.Corr':>12} {'Const.Cohesion':>15}")
    print("-" * 70)
    for method in topological:
        if method in crossing_results:
            analysis = analysis_results[method]
            print(f"{method:<25} {crossing_results[method]:>10} "
                  f"{analysis['graph_distance_correlation']:>12.3f} "
                  f"{analysis['constellation_cohesion']:>15.2f}")

    print("\nCLUSTERED LAYOUTS (experimental constellation grouping):")
    print("-" * 70)
    print(f"{'Method':<25} {'Crossings':>10} {'Dist.Corr':>12} {'Const.Cohesion':>15}")
    print("-" * 70)
    for method in clustered:
        if method in crossing_results:
            analysis = analysis_results[method]
            print(f"{method:<25} {crossing_results[method]:>10} "
                  f"{analysis['graph_distance_correlation']:>12.3f} "
                  f"{analysis['constellation_cohesion']:>15.2f}")

    print("\nCOORDINATE-BASED LAYOUTS (use Eve spatial data):")
    print("-" * 70)
    print(f"{'Method':<25} {'Crossings':>10} {'Dist.Corr':>12} {'Const.Cohesion':>15}")
    print("-" * 70)
    for method in coord_based:
        if method in crossing_results:
            analysis = analysis_results[method]
            print(f"{method:<25} {crossing_results[method]:>10} "
                  f"{analysis['graph_distance_correlation']:>12.3f} "
                  f"{analysis['constellation_cohesion']:>15.2f}")

    print()
    print("="*70)
    print("WHAT INFORMATION IS PRESERVED?")
    print("="*70)
    print()
    print("Distance Correlation:")
    print("  Measures how well graph distances (hop count) correlate with")
    print("  visual distances on screen. Higher = better distance preservation.")
    print("  Kamada-Kawai optimizes for this metric!")
    print()
    print("Constellation Cohesion:")
    print("  Ratio of between-constellation to within-constellation distances.")
    print("  Higher = constellations are more visually clustered.")
    print("  Constellation-clustered layout optimizes for this!")
    print()
    print(f"Best for minimal crossings: {min(crossing_results, key=crossing_results.get)} "
          f"({crossing_results[min(crossing_results, key=crossing_results.get)]} crossings)")

    # Find best for distance correlation
    best_corr = max(analysis_results, key=lambda m: analysis_results[m]['graph_distance_correlation'])
    print(f"Best for distance preservation: {best_corr} "
          f"(correlation: {analysis_results[best_corr]['graph_distance_correlation']:.3f})")

    # Find best for constellation cohesion
    best_cohesion = max(analysis_results, key=lambda m: analysis_results[m]['constellation_cohesion'])
    print(f"Best for constellation clustering: {best_cohesion} "
          f"(cohesion: {analysis_results[best_cohesion]['constellation_cohesion']:.2f})")

    print()
    print("="*70)
    print("✓ Phase 2 Complete!")
    print(f"Main map: pure_blind_map.html (using {best_method} layout)")
    print()
    print("All comparison maps generated:")
    for method in layouts.keys():
        print(f"  - pure_blind_map_{method}.html")
    print("="*70)


if __name__ == "__main__":
    main()
