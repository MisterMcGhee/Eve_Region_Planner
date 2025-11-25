# Pure Blind Planning Tool - Algorithms

This document explains the key algorithms used in the planning tool.

---

## Table of Contents
1. [Distance Calculations](#distance-calculations)
2. [Mining System Clustering](#mining-system-clustering)
3. [Ratting System Distribution](#ratting-system-distribution)
4. [Ansiblex Bridge Optimization](#ansiblex-bridge-optimization)
5. [Network Analysis](#network-analysis)

---

## Distance Calculations

### 3D Euclidean Distance

Calculate the distance between two systems in light-years:

```python
def calculate_distance_ly(system1, system2, G):
    """
    Calculate distance in light-years between two systems.
    
    Args:
        system1: Source system name
        system2: Target system name
        G: NetworkX graph with system coordinates
        
    Returns:
        float: Distance in light-years
    """
    import math
    
    # Get 3D coordinates (in meters)
    x1, y1, z1 = G.nodes[system1]['x'], G.nodes[system1]['y'], G.nodes[system1]['z']
    x2, y2, z2 = G.nodes[system2]['x'], G.nodes[system2]['y'], G.nodes[system2]['z']
    
    # Euclidean distance in meters
    distance_m = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    # Convert to light-years (1 LY ≈ 9.461e15 meters)
    METERS_PER_LY = 9.461e15
    distance_ly = distance_m / METERS_PER_LY
    
    return distance_ly
```

**Complexity:** O(1)

**Usage:** Validating Ansiblex bridge placement (5 LY constraint)

### Graph Distance (Jumps)

Calculate the shortest path distance in jumps:

```python
def calculate_jump_distance(system1, system2, G):
    """
    Calculate shortest path distance in jumps.
    
    Args:
        system1: Source system
        system2: Target system
        G: NetworkX graph
        
    Returns:
        int: Number of jumps, or None if unreachable
    """
    import networkx as nx
    
    try:
        return nx.shortest_path_length(G, system1, system2)
    except nx.NetworkXNoPath:
        return None
```

**Complexity:** O(V + E) using BFS

**Usage:** Calculating distances for strategic planning

### Multi-Target Distances

Calculate distances from one system to many targets:

```python
def calculate_distances_to_targets(source, targets, G):
    """
    Calculate distances from source to all targets efficiently.
    
    Args:
        source: Source system
        targets: List of target systems
        G: NetworkX graph
        
    Returns:
        dict: {target: distance} mapping
    """
    import networkx as nx
    
    # Single-source shortest paths (efficient for multiple targets)
    all_distances = nx.single_source_shortest_path_length(G, source)
    
    return {target: all_distances.get(target, float('inf')) for target in targets}
```

**Complexity:** O(V + E) for all distances at once

**Usage:** Distance heatmaps, reference system calculations

---

## Mining System Clustering

### Objective
Select N systems for mining that maximize:
1. Proximity to industrial hubs
2. Ice belt presence
3. Moon count
4. Constellation clustering

### Algorithm: Weighted Scoring

```python
def optimize_mining_systems(G, industrial_hubs, n_systems, weights=None):
    """
    Select optimal mining systems using weighted scoring.
    
    Args:
        G: NetworkX graph
        industrial_hubs: List of industrial hub systems
        n_systems: Number of mining systems to select
        weights: Dict of score weights (optional)
        
    Returns:
        List of (system, score) tuples
    """
    import networkx as nx
    
    # Default weights
    if weights is None:
        weights = {
            'distance': -10,      # Negative (closer is better)
            'ice': 50,            # Bonus for ice belts
            'moons': 2,           # Per moon bonus
            'clustering': 5,      # Per adjacent mining system
        }
    
    scores = {}
    
    for system in G.nodes():
        score = 0
        
        # 1. Distance to nearest industrial hub (negative weight)
        if industrial_hubs:
            distances = calculate_distances_to_targets(system, industrial_hubs, G)
            min_distance = min(distances.values())
            score += weights['distance'] * min_distance
        
        # 2. Ice belt bonus
        if G.nodes[system].get('has_ice', False):
            score += weights['ice']
        
        # 3. Moon count bonus
        moon_count = G.nodes[system].get('moons', 0)
        score += weights['moons'] * moon_count
        
        scores[system] = score
    
    # Initial selection (top N by score so far)
    candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_systems * 2]
    
    # 4. Iteratively add clustering bonus
    selected = []
    for _ in range(n_systems):
        best_system = None
        best_score = -float('inf')
        
        for system, base_score in candidates:
            if system in selected:
                continue
            
            # Calculate clustering bonus
            constellation = G.nodes[system]['constellation']
            clustering_score = 0
            for neighbor in G.neighbors(system):
                if neighbor in selected and G.nodes[neighbor]['constellation'] == constellation:
                    clustering_score += weights['clustering']
            
            total_score = base_score + clustering_score
            
            if total_score > best_score:
                best_score = total_score
                best_system = system
        
        if best_system:
            selected.append(best_system)
            scores[best_system] = best_score
    
    return [(sys, scores[sys]) for sys in selected]
```

**Complexity:** O(V × E + N × K) where N = systems to select, K = candidates

**Key Features:**
- Considers multiple factors simultaneously
- Clustering bonus increases as systems are selected
- Tunable weights for different priorities

### Example Usage

```python
# Find 10 mining systems near X-7OMU
results = optimize_mining_systems(
    G, 
    industrial_hubs=['X-7OMU'],
    n_systems=10,
    weights={
        'distance': -15,  # Prioritize proximity more
        'ice': 100,       # Strongly prioritize ice
        'moons': 1,       # De-prioritize moons
        'clustering': 5,
    }
)

for system, score in results:
    print(f"{system}: {score:.1f}")
```

---

## Ratting System Distribution

### Objective
Select N systems for ratting that maximize:
1. Spread across the region (avoid clustering)
2. Higher true-sec systems (better anomaly spawns)
3. Balanced constellation coverage
4. Reasonable distance from staging

### Algorithm: Spatial Distribution

```python
def optimize_ratting_systems(G, staging_system, n_systems, strategy='spread'):
    """
    Select optimal ratting systems with spatial distribution.
    
    Args:
        G: NetworkX graph
        staging_system: Staging system for distance reference
        n_systems: Number of ratting systems to select
        strategy: 'spread', 'cluster', or 'constellation'
        
    Returns:
        List of (system, score) tuples
    """
    import networkx as nx
    
    selected = []
    constellation_counts = {}
    
    if strategy == 'spread':
        # Spread evenly - select systems that maximize minimum distance to selected
        candidates = list(G.nodes())
        
        # First system: closest to staging
        distances = nx.single_source_shortest_path_length(G, staging_system)
        first = min(candidates, key=lambda s: distances[s])
        selected.append(first)
        constellation_counts[G.nodes[first]['constellation']] = 1
        
        # Remaining systems: maximize minimum distance to selected
        for _ in range(n_systems - 1):
            best_system = None
            best_min_distance = -1
            
            for system in candidates:
                if system in selected:
                    continue
                
                # Calculate minimum distance to any selected system
                min_dist = min(
                    nx.shortest_path_length(G, system, sel) 
                    for sel in selected
                )
                
                # Bonus for higher true-sec
                sec_bonus = max(0, G.nodes[system]['security']) * 0.5
                
                # Penalty for constellation overload
                constellation = G.nodes[system]['constellation']
                const_count = constellation_counts.get(constellation, 0)
                const_penalty = const_count * 2
                
                score = min_dist + sec_bonus - const_penalty
                
                if score > best_min_distance:
                    best_min_distance = score
                    best_system = system
            
            if best_system:
                selected.append(best_system)
                const = G.nodes[best_system]['constellation']
                constellation_counts[const] = constellation_counts.get(const, 0) + 1
    
    elif strategy == 'cluster':
        # Cluster near staging
        distances = nx.single_source_shortest_path_length(G, staging_system)
        
        # Prefer 3-6 jump range (close but not too close)
        def score_system(sys):
            dist = distances[sys]
            if 3 <= dist <= 6:
                proximity_score = 10 - abs(dist - 4.5)
            else:
                proximity_score = max(0, 5 - abs(dist - 4.5))
            
            sec_score = max(0, G.nodes[sys]['security']) * 2
            return proximity_score + sec_score
        
        candidates = sorted(G.nodes(), key=score_system, reverse=True)
        selected = candidates[:n_systems]
    
    elif strategy == 'constellation':
        # One per constellation, prioritize by true-sec
        constellations = {}
        for system in G.nodes():
            const = G.nodes[system]['constellation']
            if const not in constellations:
                constellations[const] = []
            constellations[const].append(system)
        
        # Pick best system from each constellation
        for const, systems in constellations.items():
            if len(selected) >= n_systems:
                break
            
            # Best = highest true-sec
            best = max(systems, key=lambda s: G.nodes[s]['security'])
            selected.append(best)
    
    # Calculate final scores for display
    scores = {}
    for system in selected:
        sec_score = max(0, G.nodes[system]['security']) * 10
        dist_score = nx.shortest_path_length(G, staging_system, system)
        scores[system] = sec_score + (10 / (1 + dist_score))
    
    return [(sys, scores[sys]) for sys in selected]
```

**Complexity:** O(N × V × E) for spread strategy (most expensive)

**Strategies:**
- **Spread:** Maximizes minimum distance between ratting systems
- **Cluster:** Concentrates systems near staging
- **Constellation:** One system per constellation

---

## Ansiblex Bridge Optimization

### Objective
Place Ansiblex jump bridges to minimize weighted travel time to strategic systems.

### Constraints
1. Maximum 5 light-year range
2. One bridge terminus per system
3. Budget constraints (optional)

### Algorithm 1: Greedy Weighted Reduction

```python
def optimize_bridges_greedy(G, strategic_systems, weights, max_bridges=10):
    """
    Greedy algorithm to place Ansiblex bridges.
    
    Args:
        G: NetworkX graph
        strategic_systems: Dict of {category: [systems]}
        weights: Dict of {category: weight}
        max_bridges: Maximum number of bridges
        
    Returns:
        List of (from, to, improvement) tuples
    """
    import networkx as nx
    
    bridges = []
    used_systems = set()  # Systems that already have a bridge
    
    # Flatten strategic systems with weights
    weighted_targets = []
    for category, systems in strategic_systems.items():
        weight = weights.get(category, 10)
        for system in systems:
            weighted_targets.append((system, weight))
    
    def calculate_weighted_avg_distance(G_current, bridges_current):
        """Calculate current weighted average distance to strategic systems"""
        total_weighted_distance = 0
        total_weight = 0
        
        for target, weight in weighted_targets:
            # Average distance from all systems to this target
            distances = nx.single_source_shortest_path_length(G_current, target)
            avg_dist = sum(distances.values()) / len(distances)
            total_weighted_distance += avg_dist * weight
            total_weight += weight
        
        return total_weighted_distance / total_weight if total_weight > 0 else 0
    
    # Initial distance
    G_working = G.copy()
    baseline_distance = calculate_weighted_avg_distance(G_working, [])
    
    for i in range(max_bridges):
        best_bridge = None
        best_improvement = 0
        
        # Try all possible bridges
        for system1 in G.nodes():
            if system1 in used_systems:
                continue
            
            for system2 in G.nodes():
                if system2 in used_systems or system1 == system2:
                    continue
                
                # Check distance constraint
                distance_ly = calculate_distance_ly(system1, system2, G)
                if distance_ly > 5.0:
                    continue
                
                # Add bridge temporarily
                G_test = G_working.copy()
                G_test.add_edge(system1, system2, type='ansiblex')
                
                # Calculate new weighted distance
                new_distance = calculate_weighted_avg_distance(G_test, bridges + [(system1, system2)])
                
                # Calculate improvement
                improvement = baseline_distance - new_distance
                
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_bridge = (system1, system2, distance_ly)
        
        # Add best bridge
        if best_bridge:
            system1, system2, distance_ly = best_bridge
            bridges.append((system1, system2, best_improvement))
            used_systems.add(system1)
            used_systems.add(system2)
            G_working.add_edge(system1, system2, type='ansiblex')
            baseline_distance -= best_improvement
            
            print(f"Bridge {i+1}: {system1} ↔ {system2} ({distance_ly:.2f} LY) "
                  f"- Improvement: {best_improvement:.3f}")
        else:
            print(f"No valid bridges remaining after {i} bridges")
            break
    
    return bridges
```

**Complexity:** O(M × V² × (V + E)) where M = max_bridges

**Key Features:**
- Considers strategic system weights
- Respects all constraints
- Greedy approach (fast but not optimal)

### Algorithm 2: Integer Linear Programming (Optimal)

For optimal solutions, formulate as ILP:

```python
from scipy.optimize import linprog
import numpy as np

def optimize_bridges_ilp(G, strategic_systems, weights, max_bridges=10):
    """
    Optimal bridge placement using Integer Linear Programming.
    
    This finds the globally optimal solution but is much slower.
    
    Args:
        G: NetworkX graph
        strategic_systems: Dict of strategic systems
        weights: Weights for each category
        max_bridges: Maximum bridges to place
        
    Returns:
        List of optimal bridges
    """
    # Build candidate edges (all valid bridge possibilities)
    candidates = []
    for s1 in G.nodes():
        for s2 in G.nodes():
            if s1 < s2:  # Avoid duplicates
                dist_ly = calculate_distance_ly(s1, s2, G)
                if dist_ly <= 5.0:
                    candidates.append((s1, s2))
    
    n_candidates = len(candidates)
    
    # Decision variables: x[i] = 1 if bridge i is built
    # Objective: minimize weighted average distance
    
    # This requires complex constraint matrices - see scipy.optimize.milp
    # for full implementation details
    
    # Constraints:
    # 1. Sum of bridges <= max_bridges
    # 2. Each system can have at most one bridge terminus
    # 3. If bridge i uses system s, then sum of bridges using s <= 1
    
    # [Full ILP implementation would go here]
    
    pass  # Placeholder
```

**Complexity:** Exponential (NP-hard problem)

**When to use:** Small regions or when optimality is critical

### Bridge Impact Metrics

```python
def calculate_bridge_impact(G, bridges, strategic_systems, weights):
    """
    Calculate impact metrics of bridge network.
    
    Returns:
        dict: Various impact metrics
    """
    import networkx as nx
    
    # Create graph with bridges
    G_with_bridges = G.copy()
    for from_sys, to_sys in bridges:
        G_with_bridges.add_edge(from_sys, to_sys, type='ansiblex')
    
    metrics = {}
    
    # Average jumps to each strategic category
    for category, systems in strategic_systems.items():
        before_distances = []
        after_distances = []
        
        for target in systems:
            dist_before = nx.single_source_shortest_path_length(G, target)
            dist_after = nx.single_source_shortest_path_length(G_with_bridges, target)
            
            before_distances.append(sum(dist_before.values()) / len(dist_before))
            after_distances.append(sum(dist_after.values()) / len(dist_after))
        
        avg_before = sum(before_distances) / len(before_distances) if before_distances else 0
        avg_after = sum(after_distances) / len(after_distances) if after_distances else 0
        
        metrics[f'{category}_before'] = avg_before
        metrics[f'{category}_after'] = avg_after
        metrics[f'{category}_improvement'] = avg_before - avg_after
        metrics[f'{category}_improvement_pct'] = ((avg_before - avg_after) / avg_before * 100) if avg_before > 0 else 0
    
    # Network diameter (max distance between any two systems)
    metrics['diameter_before'] = nx.diameter(G)
    metrics['diameter_after'] = nx.diameter(G_with_bridges)
    
    # Average path length
    metrics['avg_path_before'] = nx.average_shortest_path_length(G)
    metrics['avg_path_after'] = nx.average_shortest_path_length(G_with_bridges)
    
    return metrics
```

---

## Network Analysis

### Chokepoint Detection

Find articulation points (systems whose removal disconnects the graph):

```python
def find_chokepoints(G):
    """
    Find critical chokepoint systems.
    
    Args:
        G: NetworkX graph
        
    Returns:
        List of (system, impact_score) tuples
    """
    import networkx as nx
    
    articulation_points = list(nx.articulation_points(G))
    
    # Calculate impact score for each chokepoint
    chokepoints = []
    for system in articulation_points:
        # Remove system and count components
        G_test = G.copy()
        G_test.remove_node(system)
        n_components = nx.number_connected_components(G_test)
        
        # Calculate size of components
        components = list(nx.connected_components(G_test))
        component_sizes = [len(c) for c in components]
        
        # Impact = how many systems become disconnected
        impact = n_components * max(component_sizes)
        
        chokepoints.append((system, impact))
    
    return sorted(chokepoints, key=lambda x: x[1], reverse=True)
```

**Complexity:** O(V + E) for articulation points

**Usage:** Identifying vulnerable systems that should be defended

### Traffic Analysis

Find high-traffic systems using betweenness centrality:

```python
def analyze_traffic(G, strategic_systems=None):
    """
    Analyze system traffic patterns.
    
    Args:
        G: NetworkX graph
        strategic_systems: Optional list of strategic systems (weights paths through them)
        
    Returns:
        Dict of {system: traffic_score}
    """
    import networkx as nx
    
    if strategic_systems is None:
        # Standard betweenness centrality
        centrality = nx.betweenness_centrality(G)
    else:
        # Weighted betweenness (only paths to/from strategic systems)
        centrality = {}
        for system in G.nodes():
            score = 0
            for target in strategic_systems:
                if system == target:
                    continue
                # Count how many shortest paths go through this system
                paths = list(nx.all_shortest_paths(G, system, target))
                for path in paths:
                    if system in path[1:-1]:  # Exclude source and target
                        score += 1
            centrality[system] = score
    
    return centrality
```

**Complexity:** O(V³) for exact betweenness

**Usage:** Identifying systems that see the most traffic (good candidates for staging/markets)

### System Centrality

Find the "center" of the network:

```python
def find_network_center(G):
    """
    Find the most central system(s) in the network.
    
    Args:
        G: NetworkX graph
        
    Returns:
        List of (system, centrality_score) tuples
    """
    import networkx as nx
    
    # Closeness centrality (inverse of average distance to all other systems)
    closeness = nx.closeness_centrality(G)
    
    # Sort by centrality
    sorted_systems = sorted(closeness.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_systems
```

**Complexity:** O(V × (V + E))

**Usage:** Finding optimal locations for staging or market hubs

---

## Algorithm Complexity Summary

| Algorithm | Complexity | Use Case |
|-----------|-----------|----------|
| Distance (3D) | O(1) | Bridge validation |
| Distance (Graph) | O(V + E) | Jump calculations |
| Mining Clustering | O(V × E + N × K) | Mining optimization |
| Ratting Distribution | O(N × V × E) | Ratting optimization |
| Bridge Greedy | O(M × V² × (V + E)) | Fast bridge placement |
| Bridge ILP | Exponential | Optimal bridge placement |
| Chokepoints | O(V + E) | Vulnerability analysis |
| Traffic Analysis | O(V³) | Strategic placement |
| Centrality | O(V × (V + E)) | Hub identification |

Where:
- V = number of systems (85 for Pure Blind)
- E = number of gates (~150-200 for Pure Blind)
- N = systems to select
- M = maximum bridges

---

**Version:** 1.0  
**Last Updated:** November 25, 2025
