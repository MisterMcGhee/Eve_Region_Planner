"""
QUICK REFERENCE: Common Graph Operations for Eve Online
========================================================

Installation:
  pip install networkx matplotlib

Quick Start Template:
"""

import networkx as nx

# Create the graph
G = nx.Graph()

# Add systems with attributes
G.add_node("5ZXX-K", constellation="U-7RBK", has_ice=False, power=0, workforce=0)
G.add_edge("5ZXX-K", "X-7OMU")  # Add gate connection

# ============================================================================
# MOST COMMON OPERATIONS
# ============================================================================

"""
1. ROUTE PLANNING - Find shortest path between systems
"""
path = nx.shortest_path(G, "Start-System", "End-System")
jumps = nx.shortest_path_length(G, "Start-System", "End-System")
print(f"Route: {' -> '.join(path)} ({jumps} jumps)")

"""
2. FIND NEAREST RESOURCE - Find closest system with specific attribute
"""
def find_nearest_with_attribute(graph, start, attribute, value=True):
    """Find nearest system where attribute equals value"""
    targets = [n for n, data in graph.nodes(data=True) 
               if data.get(attribute) == value]
    
    closest = None
    min_dist = float('inf')
    
    for target in targets:
        try:
            dist = nx.shortest_path_length(graph, start, target)
            if dist < min_dist:
                min_dist = dist
                closest = target
        except nx.NetworkXNoPath:
            continue
    
    if closest:
        path = nx.shortest_path(graph, start, closest)
        return closest, path, min_dist
    return None, None, None

# Example: Find nearest ice belt
ice_system, route, distance = find_nearest_with_attribute(G, "5ZXX-K", "has_ice", True)

"""
3. DISTANCE FROM ONE SYSTEM TO ALL OTHERS
"""
distances = nx.single_source_shortest_path_length(G, "5ZXX-K")
# Returns: {'5ZXX-K': 0, 'X-7OMU': 1, 'EC-P8R': 2, ...}

# Get all systems within N jumps
nearby = [sys for sys, dist in distances.items() if dist <= 3]

"""
4. FIND CHOKEPOINTS - Critical systems for control
"""
chokepoints = list(nx.articulation_points(G))
# These systems split the network if removed - strategic targets!

"""
5. FIND HIGH-TRAFFIC SYSTEMS - Best for interdiction/camping
"""
traffic = nx.betweenness_centrality(G)
# Returns dict: {'System': importance_score, ...}

# Get top 5 highest-traffic systems
top_traffic = sorted(traffic.items(), key=lambda x: x[1], reverse=True)[:5]

"""
6. CHECK CONNECTIVITY - Can I reach that system?
"""
can_reach = nx.has_path(G, "System-A", "System-B")

"""
7. GET ADJACENT SYSTEMS - Systems 1 jump away
"""
neighbors = list(G.neighbors("5ZXX-K"))

"""
8. FIND ALL PATHS - Multiple routes to same destination
"""
all_routes = list(nx.all_shortest_paths(G, "Start", "End"))
# Returns list of paths, all with same length

"""
9. NETWORK CENTER - Best staging system
"""
center = nx.center(G)  # System(s) with minimum maximum distance to others

"""
10. FILTER SYSTEMS BY ATTRIBUTE
"""
# Find all systems with ice belts
ice_systems = [node for node, data in G.nodes(data=True) 
               if data.get('has_ice', False)]

# Find all systems in a constellation
constellation_systems = [node for node, data in G.nodes(data=True)
                        if data.get('constellation') == 'U-7RBK']

# Find systems with high power
high_power = [node for node, data in G.nodes(data=True)
              if data.get('power', 0) > 2000]

# ============================================================================
# BUILDING THE FULL PURE BLIND NETWORK
# ============================================================================

"""
Template for building from your spreadsheet data:
"""

def build_pure_blind_network(systems_data, connections_data):
    """
    Build graph from spreadsheet data
    
    systems_data: list of dicts with keys: name, constellation, power, workforce, has_ice, moons
    connections_data: list of tuples: [(system1, system2), ...]
    """
    G = nx.Graph()
    
    # Add all systems with attributes
    for system in systems_data:
        G.add_node(
            system['name'],
            constellation=system['constellation'],
            power=system['power'],
            workforce=system['workforce'],
            has_ice=system['has_ice'],
            moons=system['moons']
        )
    
    # Add all gate connections
    G.add_edges_from(connections_data)
    
    return G

# Example usage:
systems = [
    {'name': '5ZXX-K', 'constellation': 'U-7RBK', 'power': 0, 'workforce': 0, 
     'has_ice': False, 'moons': 82},
    {'name': 'EC-P8R', 'constellation': 'YS-GOP', 'power': 1660, 'workforce': 30590,
     'has_ice': True, 'moons': 64},
]

connections = [
    ('5ZXX-K', 'X-7OMU'),
    ('X-7OMU', 'EC-P8R'),
]

G = build_pure_blind_network(systems, connections)

# ============================================================================
# ADVANCED: CUSTOM PATHFINDING
# ============================================================================

"""
Find safest route (avoiding high-traffic systems)
"""
def find_safest_path(graph, start, end, traffic_weights):
    """
    Find path avoiding high-traffic systems
    traffic_weights: dict of {system: traffic_score}
    """
    # Create edge weights based on node traffic
    for u, v in graph.edges():
        # Weight is sum of endpoint traffic scores
        weight = traffic_weights.get(u, 0) + traffic_weights.get(v, 0)
        graph[u][v]['danger'] = weight
    
    # Find path minimizing danger
    path = nx.shortest_path(graph, start, end, weight='danger')
    return path

"""
Find route avoiding specific systems (gatecamps, hostile territory)
"""
def find_path_avoiding(graph, start, end, avoid_systems):
    """Find path that avoids specific systems"""
    # Create subgraph without avoided systems
    nodes_to_keep = [n for n in graph.nodes() if n not in avoid_systems]
    subgraph = graph.subgraph(nodes_to_keep)
    
    try:
        return nx.shortest_path(subgraph, start, end)
    except nx.NetworkXNoPath:
        return None  # No path exists avoiding those systems

# Example:
gatecamps = ['EC-P8R', 'X-7OMU']  # Known dangerous systems
safe_route = find_path_avoiding(G, '5ZXX-K', 'CL6-ZG', gatecamps)

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
For large networks (all of New Eden):
1. Use nx.DiGraph() if you have one-way connections (wormholes)
2. Pre-compute distances if you'll query them multiple times:
   all_distances = dict(nx.all_pairs_shortest_path_length(G))
3. For repeated pathfinding, use nx.dijkstra_path() directly
4. Consider using igraph library for very large graphs (faster)
"""

# ============================================================================
# VISUALIZATION QUICK REFERENCE
# ============================================================================

"""
Basic visualization:
"""
import matplotlib.pyplot as plt

pos = nx.spring_layout(G)  # Position nodes
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=500, font_size=8, font_weight='bold')
plt.savefig('network.png')

"""
Color nodes by attribute:
"""
colors = ['red' if G.nodes[n].get('has_ice') else 'gray' for n in G.nodes()]
nx.draw(G, pos, node_color=colors, with_labels=True)

"""
Highlight a path:
"""
path = nx.shortest_path(G, 'Start', 'End')
path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=3)

# ============================================================================
# COMMON ERRORS AND SOLUTIONS
# ============================================================================

"""
ERROR: NetworkXNoPath
SOLUTION: Systems aren't connected. Check with nx.has_path(G, start, end)

ERROR: KeyError when accessing node attributes
SOLUTION: Use .get() method: G.nodes[node].get('attribute', default_value)

ERROR: Graph visualization is messy
SOLUTION: Try different layouts:
  - nx.spring_layout(G, k=2)  # Increase k for more spacing
  - nx.kamada_kawai_layout(G)
  - nx.circular_layout(G)
  - nx.shell_layout(G)
"""

print("Quick reference guide loaded!")
print("\nMost useful functions:")
print("  nx.shortest_path(G, start, end)")
print("  nx.single_source_shortest_path_length(G, start)")
print("  list(G.neighbors(node))")
print("  nx.articulation_points(G)")
print("  nx.betweenness_centrality(G)")
