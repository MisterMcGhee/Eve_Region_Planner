"""
Ansiblex Jump Bridge Management Module

Handles all functionality related to Ansiblex jump bridges including:
- Distance calculations (light-years)
- Valid connection detection (5 LY constraint)
- Bridge configuration management
- Placement metrics and optimization
"""

import json
import math
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path


class BridgeManager:
    """Manages Ansiblex jump bridge calculations and configurations."""

    # Constants
    METERS_PER_LY = 9.461e15  # Meters per light-year
    MAX_BRIDGE_RANGE_LY = 5.0  # Maximum jump bridge range in light-years
    ANSIBLEX_UPGRADE_NAME = "Advanced Logistics (Ansi)"

    def __init__(self, graph: nx.Graph = None):
        """
        Initialize the bridge manager.

        Args:
            graph: NetworkX graph with system data (x, y, z coordinates)
        """
        self.graph = graph
        self.bridges: List[Dict] = []
        self._valid_connections_cache: Dict[str, List[Tuple[str, float]]] = {}

    def set_graph(self, graph: nx.Graph):
        """Set the graph after initialization."""
        self.graph = graph
        self._valid_connections_cache.clear()

    def calculate_distance_ly(self, system1: str, system2: str) -> float:
        """
        Calculate the distance in light-years between two systems.

        Uses 3D Euclidean distance from in-game coordinates.

        Args:
            system1: Name of first system
            system2: Name of second system

        Returns:
            Distance in light-years

        Raises:
            KeyError: If system not found in graph
            ValueError: If coordinates missing
        """
        if self.graph is None:
            raise ValueError("Graph not set. Use set_graph() first.")

        # Get coordinates
        node1 = self.graph.nodes[system1]
        node2 = self.graph.nodes[system2]

        x1, y1, z1 = node1['x'], node1['y'], node1['z']
        x2, y2, z2 = node2['x'], node2['y'], node2['z']

        # Calculate Euclidean distance in meters
        distance_m = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

        # Convert to light-years
        distance_ly = distance_m / self.METERS_PER_LY

        return distance_ly

    def can_bridge_connect(self, system1: str, system2: str) -> Tuple[bool, float]:
        """
        Check if two systems can be connected by an Ansiblex jump bridge.

        Args:
            system1: Name of first system
            system2: Name of second system

        Returns:
            Tuple of (can_connect: bool, distance_ly: float)
        """
        distance = self.calculate_distance_ly(system1, system2)
        can_connect = distance <= self.MAX_BRIDGE_RANGE_LY
        return can_connect, distance

    def get_valid_connections(self, system: str,
                             exclude_systems: Set[str] = None) -> List[Tuple[str, float]]:
        """
        Get all systems within bridge range of the given system.

        Args:
            system: System name to find connections for
            exclude_systems: Set of systems to exclude from results

        Returns:
            List of tuples (system_name, distance_ly) sorted by distance
        """
        if exclude_systems is None:
            exclude_systems = set()

        # Check cache
        cache_key = f"{system}:{','.join(sorted(exclude_systems))}"
        if cache_key in self._valid_connections_cache:
            return self._valid_connections_cache[cache_key]

        valid_connections = []

        for other_system in self.graph.nodes():
            # Skip self and excluded systems
            if other_system == system or other_system in exclude_systems:
                continue

            can_connect, distance = self.can_bridge_connect(system, other_system)

            if can_connect:
                valid_connections.append((other_system, distance))

        # Sort by distance (closest first)
        valid_connections.sort(key=lambda x: x[1])

        # Cache result
        self._valid_connections_cache[cache_key] = valid_connections

        return valid_connections

    def get_bridge_summary(self, system: str) -> Dict:
        """
        Get a summary of bridge connection possibilities for a system.

        Args:
            system: System name

        Returns:
            Dictionary with connection statistics
        """
        connections = self.get_valid_connections(system)

        if not connections:
            return {
                'system': system,
                'total_connections': 0,
                'closest_system': None,
                'closest_distance': None,
                'farthest_system': None,
                'farthest_distance': None,
                'average_distance': None
            }

        distances = [dist for _, dist in connections]

        return {
            'system': system,
            'total_connections': len(connections),
            'closest_system': connections[0][0],
            'closest_distance': connections[0][1],
            'farthest_system': connections[-1][0],
            'farthest_distance': connections[-1][1],
            'average_distance': sum(distances) / len(distances)
        }

    def load_bridges(self, filename: str = "ansiblex_bridges.json") -> bool:
        """
        Load bridge configuration from JSON file.

        Args:
            filename: Path to bridge configuration file

        Returns:
            True if successful, False if file doesn't exist
        """
        filepath = Path(filename)

        if not filepath.exists():
            self.bridges = []
            return False

        with open(filepath, 'r') as f:
            data = json.load(f)
            self.bridges = data.get('bridges', [])

        return True

    def save_bridges(self, filename: str = "ansiblex_bridges.json"):
        """
        Save bridge configuration to JSON file.

        Args:
            filename: Path to bridge configuration file
        """
        data = {
            'bridges': self.bridges,
            'metadata': {
                'total_bridges': len(self.bridges),
                'active_bridges': sum(1 for b in self.bridges if b.get('active', True))
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def add_bridge(self, system1: str, system2: str,
                   active: bool = True,
                   validate: bool = True) -> Tuple[bool, str]:
        """
        Add a bridge between two systems.

        Args:
            system1: First system name
            system2: Second system name
            active: Whether bridge is active
            validate: Whether to validate distance constraint

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check if bridge already exists
        if self.has_bridge(system1, system2):
            return False, f"Bridge already exists between {system1} and {system2}"

        # Check if either system is already used
        used_systems = self.get_used_systems()
        if system1 in used_systems:
            return False, f"System {system1} already has a bridge"
        if system2 in used_systems:
            return False, f"System {system2} already has a bridge"

        # Validate distance if requested
        if validate:
            can_connect, distance = self.can_bridge_connect(system1, system2)
            if not can_connect:
                return False, f"Systems too far apart: {distance:.2f} LY (max {self.MAX_BRIDGE_RANGE_LY} LY)"
        else:
            distance = self.calculate_distance_ly(system1, system2)

        # Add bridge
        bridge = {
            'from': system1,
            'to': system2,
            'distance_ly': round(distance, 2),
            'active': active
        }

        self.bridges.append(bridge)

        return True, f"Bridge added: {system1} <-> {system2} ({distance:.2f} LY)"

    def remove_bridge(self, system1: str, system2: str) -> Tuple[bool, str]:
        """
        Remove a bridge between two systems.

        Args:
            system1: First system name
            system2: Second system name

        Returns:
            Tuple of (success: bool, message: str)
        """
        initial_count = len(self.bridges)

        # Remove bridge (bidirectional)
        self.bridges = [
            b for b in self.bridges
            if not ((b['from'] == system1 and b['to'] == system2) or
                   (b['from'] == system2 and b['to'] == system1))
        ]

        if len(self.bridges) < initial_count:
            return True, f"Bridge removed: {system1} <-> {system2}"
        else:
            return False, f"No bridge found between {system1} and {system2}"

    def has_bridge(self, system1: str, system2: str) -> bool:
        """Check if a bridge exists between two systems."""
        for bridge in self.bridges:
            if ((bridge['from'] == system1 and bridge['to'] == system2) or
                (bridge['from'] == system2 and bridge['to'] == system1)):
                return True
        return False

    def get_used_systems(self) -> Set[str]:
        """Get set of all systems that have bridges."""
        used = set()
        for bridge in self.bridges:
            used.add(bridge['from'])
            used.add(bridge['to'])
        return used

    def get_bridges_for_system(self, system: str) -> List[Dict]:
        """Get all bridges connected to a system."""
        return [
            b for b in self.bridges
            if b['from'] == system or b['to'] == system
        ]

    def clear_bridges(self):
        """Remove all bridges."""
        self.bridges = []

    def calculate_jump_savings(self, graph_with_bridges: nx.Graph) -> Dict:
        """
        Calculate jump distance savings with bridges vs without.

        Args:
            graph_with_bridges: NetworkX graph with bridge edges added

        Returns:
            Dictionary with statistics about jump savings
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        systems = list(self.graph.nodes())
        total_original = 0
        total_with_bridges = 0
        improvements = []

        # Calculate all-pairs shortest paths
        for i, sys1 in enumerate(systems):
            for sys2 in systems[i+1:]:
                try:
                    # Original distance
                    original_dist = nx.shortest_path_length(self.graph, sys1, sys2)

                    # Distance with bridges
                    bridge_dist = nx.shortest_path_length(graph_with_bridges, sys1, sys2)

                    total_original += original_dist
                    total_with_bridges += bridge_dist

                    if bridge_dist < original_dist:
                        improvements.append({
                            'from': sys1,
                            'to': sys2,
                            'original': original_dist,
                            'with_bridges': bridge_dist,
                            'saved': original_dist - bridge_dist
                        })

                except nx.NetworkXNoPath:
                    continue

        avg_original = total_original / len(systems) / (len(systems) - 1) * 2
        avg_with_bridges = total_with_bridges / len(systems) / (len(systems) - 1) * 2

        return {
            'average_jumps_original': avg_original,
            'average_jumps_with_bridges': avg_with_bridges,
            'average_savings': avg_original - avg_with_bridges,
            'total_improvements': len(improvements),
            'top_improvements': sorted(improvements, key=lambda x: x['saved'], reverse=True)[:10]
        }

    def get_region_statistics(self) -> Dict:
        """
        Get statistics about bridge connectivity across the region.

        Returns:
            Dictionary with regional statistics
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        systems = list(self.graph.nodes())
        total_connections = 0
        connection_counts = []

        for system in systems:
            connections = self.get_valid_connections(system)
            total_connections += len(connections)
            connection_counts.append(len(connections))

        # Avoid double counting (each connection counted twice)
        total_unique_pairs = total_connections // 2

        return {
            'total_systems': len(systems),
            'total_possible_connections': total_unique_pairs,
            'average_connections_per_system': sum(connection_counts) / len(connection_counts),
            'max_connections': max(connection_counts) if connection_counts else 0,
            'min_connections': min(connection_counts) if connection_counts else 0,
            'systems_with_no_connections': sum(1 for c in connection_counts if c == 0)
        }

    def calculate_system_metrics(self, system: str) -> Dict:
        """
        Calculate various metrics for a system to evaluate bridge placement value.

        Metrics include:
        - Centrality (closeness to all other systems)
        - Betweenness (how often system is on shortest paths)
        - Degree (number of stargate connections)
        - Bridge connections (number of systems in 5 LY range)
        - Constellation connectivity (number of other constellations reachable)

        Args:
            system: System name

        Returns:
            Dictionary with all metrics
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        # Calculate centrality metrics
        closeness = nx.closeness_centrality(self.graph, system)
        betweenness_dict = nx.betweenness_centrality(self.graph, k=10)  # Sample for speed
        betweenness = betweenness_dict.get(system, 0.0)

        # Degree (stargate connections)
        degree = self.graph.degree(system)

        # Bridge connections
        valid_connections = self.get_valid_connections(system)
        bridge_connections = len(valid_connections)

        # Constellation connectivity
        system_constellation = self.graph.nodes[system]['constellation']
        reachable_constellations = set()

        for other_system, _ in valid_connections:
            other_constellation = self.graph.nodes[other_system]['constellation']
            if other_constellation != system_constellation:
                reachable_constellations.add(other_constellation)

        return {
            'system': system,
            'closeness_centrality': closeness,
            'betweenness_centrality': betweenness,
            'stargate_degree': degree,
            'bridge_connections': bridge_connections,
            'cross_constellation_bridges': len(reachable_constellations),
            'constellation': system_constellation
        }

    def rank_systems_for_bridges(self, metric: str = 'composite',
                                 top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Rank systems by their value for bridge placement.

        Args:
            metric: Metric to use for ranking:
                - 'centrality': Closeness centrality
                - 'betweenness': Betweenness centrality
                - 'connections': Number of valid bridge connections
                - 'cross_constellation': Cross-constellation connectivity
                - 'composite': Weighted combination of all metrics
            top_n: Number of top systems to return

        Returns:
            List of (system_name, score) tuples sorted by score
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        systems = list(self.graph.nodes())
        scores = []

        if metric == 'composite':
            # Calculate all metrics for normalization
            all_metrics = [self.calculate_system_metrics(sys) for sys in systems]

            # Normalize each metric to 0-1 range
            max_closeness = max(m['closeness_centrality'] for m in all_metrics)
            max_betweenness = max(m['betweenness_centrality'] for m in all_metrics)
            max_connections = max(m['bridge_connections'] for m in all_metrics)
            max_cross_const = max(m['cross_constellation_bridges'] for m in all_metrics)

            for metrics in all_metrics:
                # Weighted composite score
                score = (
                    0.25 * (metrics['closeness_centrality'] / max_closeness if max_closeness > 0 else 0) +
                    0.25 * (metrics['betweenness_centrality'] / max_betweenness if max_betweenness > 0 else 0) +
                    0.30 * (metrics['bridge_connections'] / max_connections if max_connections > 0 else 0) +
                    0.20 * (metrics['cross_constellation_bridges'] / max_cross_const if max_cross_const > 0 else 0)
                )
                scores.append((metrics['system'], score))
        else:
            # Single metric
            metric_map = {
                'centrality': 'closeness_centrality',
                'betweenness': 'betweenness_centrality',
                'connections': 'bridge_connections',
                'cross_constellation': 'cross_constellation_bridges'
            }

            if metric not in metric_map:
                raise ValueError(f"Unknown metric: {metric}")

            metric_key = metric_map[metric]

            for system in systems:
                metrics = self.calculate_system_metrics(system)
                scores.append((system, metrics[metric_key]))

        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_n]

    def calculate_bridge_value(self, system1: str, system2: str) -> Dict:
        """
        Calculate the strategic value of a potential bridge between two systems.

        Args:
            system1: First system name
            system2: Second system name

        Returns:
            Dictionary with value metrics
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        # Check if bridge is valid
        can_connect, distance = self.can_bridge_connect(system1, system2)

        if not can_connect:
            return {
                'valid': False,
                'distance_ly': distance,
                'reason': 'Distance exceeds 5 LY limit'
            }

        # Calculate current distance via stargates
        try:
            current_jumps = nx.shortest_path_length(self.graph, system1, system2)
        except nx.NetworkXNoPath:
            current_jumps = float('inf')

        # Jump savings (if bridge reduces jumps from X to 1)
        jump_savings = max(0, current_jumps - 1)

        # Check if bridge connects different constellations
        const1 = self.graph.nodes[system1]['constellation']
        const2 = self.graph.nodes[system2]['constellation']
        cross_constellation = const1 != const2

        # Calculate how many system pairs benefit from this bridge
        # (Sample analysis for performance)
        sample_systems = list(self.graph.nodes())[:20]  # Sample for speed
        improved_paths = 0

        for sys_a in sample_systems:
            for sys_b in sample_systems:
                if sys_a >= sys_b:
                    continue

                try:
                    # Current distance
                    current_dist = nx.shortest_path_length(self.graph, sys_a, sys_b)

                    # Distance if going through bridge
                    dist_via_s1 = nx.shortest_path_length(self.graph, sys_a, system1)
                    dist_via_s2 = nx.shortest_path_length(self.graph, sys_b, system2)
                    dist_with_bridge = dist_via_s1 + 1 + dist_via_s2

                    # Also check reverse
                    dist_via_s1_rev = nx.shortest_path_length(self.graph, sys_a, system2)
                    dist_via_s2_rev = nx.shortest_path_length(self.graph, sys_b, system1)
                    dist_with_bridge_rev = dist_via_s1_rev + 1 + dist_via_s2_rev

                    best_with_bridge = min(dist_with_bridge, dist_with_bridge_rev)

                    if best_with_bridge < current_dist:
                        improved_paths += 1

                except nx.NetworkXNoPath:
                    pass

        return {
            'valid': True,
            'distance_ly': distance,
            'current_jumps': current_jumps,
            'jump_savings': jump_savings,
            'cross_constellation': cross_constellation,
            'improved_paths': improved_paths,
            'from_constellation': const1,
            'to_constellation': const2
        }

    def optimize_bridge_placement_greedy(self, max_bridges: int = 10,
                                        prioritize: str = 'jump_savings') -> List[Dict]:
        """
        Use greedy algorithm to find optimal bridge placements.

        Args:
            max_bridges: Maximum number of bridges to place
            prioritize: What to optimize for:
                - 'jump_savings': Maximize direct jump savings
                - 'coverage': Maximize number of improved paths
                - 'cross_constellation': Prioritize connecting constellations
                - 'balanced': Balance multiple objectives

        Returns:
            List of bridge dictionaries with placement information
        """
        if self.graph is None:
            raise ValueError("Graph not set")

        placed_bridges = []
        used_systems = set()

        for _ in range(max_bridges):
            best_bridge = None
            best_score = -1

            # Evaluate all possible bridges
            systems = list(self.graph.nodes())

            for i, sys1 in enumerate(systems):
                if sys1 in used_systems:
                    continue

                # Get valid connections for this system
                connections = self.get_valid_connections(sys1, exclude_systems=used_systems)

                for sys2, distance in connections:
                    if sys2 in used_systems:
                        continue

                    # Calculate bridge value
                    value = self.calculate_bridge_value(sys1, sys2)

                    if not value['valid']:
                        continue

                    # Calculate score based on priority
                    if prioritize == 'jump_savings':
                        score = value['jump_savings']
                    elif prioritize == 'coverage':
                        score = value['improved_paths']
                    elif prioritize == 'cross_constellation':
                        score = value['improved_paths'] * (2 if value['cross_constellation'] else 1)
                    else:  # balanced
                        score = (
                            value['jump_savings'] * 0.4 +
                            value['improved_paths'] * 0.4 +
                            (10 if value['cross_constellation'] else 0) * 0.2
                        )

                    if score > best_score:
                        best_score = score
                        best_bridge = {
                            'from': sys1,
                            'to': sys2,
                            'distance_ly': distance,
                            'score': score,
                            'value': value
                        }

            # Add best bridge if found
            if best_bridge:
                placed_bridges.append(best_bridge)
                used_systems.add(best_bridge['from'])
                used_systems.add(best_bridge['to'])
            else:
                # No more valid bridges
                break

        return placed_bridges


def main():
    """Example usage and testing."""
    from graph_visualizer import GraphVisualizer

    # Load graph
    print("Loading Pure Blind region data...")
    viz = GraphVisualizer()
    viz.load_data()
    viz.build_graph()

    # Create bridge manager
    manager = BridgeManager(viz.graph)

    # Get region statistics
    print("\n=== Region Bridge Statistics ===")
    stats = manager.get_region_statistics()
    print(f"Total systems: {stats['total_systems']}")
    print(f"Possible bridge connections: {stats['total_possible_connections']}")
    print(f"Average connections per system: {stats['average_connections_per_system']:.1f}")
    print(f"Max connections for a system: {stats['max_connections']}")
    print(f"Min connections for a system: {stats['min_connections']}")
    print(f"Systems with no valid connections: {stats['systems_with_no_connections']}")

    # Test specific system
    test_system = "5ZXX-K"
    print(f"\n=== Bridge Analysis for {test_system} ===")
    summary = manager.get_bridge_summary(test_system)
    print(f"Total systems in range: {summary['total_connections']}")
    if summary['closest_system']:
        print(f"Closest: {summary['closest_system']} ({summary['closest_distance']:.2f} LY)")
        print(f"Farthest: {summary['farthest_system']} ({summary['farthest_distance']:.2f} LY)")
        print(f"Average distance: {summary['average_distance']:.2f} LY")

    # Show first 10 valid connections
    connections = manager.get_valid_connections(test_system)
    print(f"\nFirst 10 systems in bridge range:")
    for system, distance in connections[:10]:
        print(f"  {system}: {distance:.2f} LY")

    # Test system metrics
    print(f"\n=== System Metrics for {test_system} ===")
    metrics = manager.calculate_system_metrics(test_system)
    print(f"Closeness centrality: {metrics['closeness_centrality']:.4f}")
    print(f"Betweenness centrality: {metrics['betweenness_centrality']:.4f}")
    print(f"Stargate connections: {metrics['stargate_degree']}")
    print(f"Valid bridge connections: {metrics['bridge_connections']}")
    print(f"Cross-constellation bridges: {metrics['cross_constellation_bridges']}")

    # Rank systems by composite score
    print("\n=== Top 10 Systems for Bridge Placement (Composite Score) ===")
    top_systems = manager.rank_systems_for_bridges(metric='composite', top_n=10)
    for i, (system, score) in enumerate(top_systems, 1):
        const = viz.graph.nodes[system]['constellation']
        print(f"{i:2d}. {system:10s} (Score: {score:.3f}, Constellation: {const})")

    # Test bridge value calculation
    if len(connections) > 1:
        bridge_from = test_system
        bridge_to = connections[1][0]  # Second closest
        print(f"\n=== Bridge Value Analysis: {bridge_from} <-> {bridge_to} ===")
        value = manager.calculate_bridge_value(bridge_from, bridge_to)
        print(f"Valid: {value['valid']}")
        print(f"Distance: {value['distance_ly']:.2f} LY")
        print(f"Current jumps via stargates: {value['current_jumps']}")
        print(f"Jump savings: {value['jump_savings']}")
        print(f"Cross-constellation: {value['cross_constellation']}")
        print(f"Improved paths (sample): {value['improved_paths']}")

    # Test optimization algorithms
    print("\n=== Optimized Bridge Placement (5 bridges, balanced strategy) ===")
    manager.clear_bridges()  # Start fresh
    optimal_bridges = manager.optimize_bridge_placement_greedy(
        max_bridges=5,
        prioritize='balanced'
    )

    for i, bridge in enumerate(optimal_bridges, 1):
        print(f"\n{i}. {bridge['from']} <-> {bridge['to']}")
        print(f"   Distance: {bridge['distance_ly']:.2f} LY")
        print(f"   Score: {bridge['score']:.2f}")
        print(f"   Jump savings: {bridge['value']['jump_savings']}")
        print(f"   Cross-constellation: {bridge['value']['cross_constellation']}")
        print(f"   Improved paths: {bridge['value']['improved_paths']}")

    # Save optimal bridges
    for bridge in optimal_bridges:
        manager.add_bridge(
            bridge['from'],
            bridge['to'],
            validate=False  # Already validated
        )

    manager.save_bridges()
    print("\n✓ Optimal bridge configuration saved to ansiblex_bridges.json")


if __name__ == "__main__":
    main()
