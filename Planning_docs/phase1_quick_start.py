"""
Phase 1 Quick Start: Data Acquisition for Pure Blind
====================================================

This script gets you started immediately with data acquisition.
Run this first, then move on to visualization and planning.
"""

import sqlite3
import pandas as pd
import networkx as nx
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths (adjust as needed)
SDE_DATABASE = "sqlite-latest.sqlite"  # Download from Fuzzwork
SPREADSHEET = "pure_blind_systems.xlsx"  # Your existing spreadsheet
OUTPUT_DIR = Path("../data/pure_blind_data")

# Pure Blind region ID
PURE_BLIND_REGION_ID = 10000023

# ============================================================================
# STEP 1: Load Data from Fuzzwork SDE
# ============================================================================

def load_system_data_from_sde(db_path):
    """
    Extract Pure Blind system data from Fuzzwork SQLite database
    """
    print("Loading system data from SDE...")
    
    conn = sqlite3.connect(db_path)
    
    # Get all Pure Blind systems with 3D coordinates
    query = """
        SELECT 
            solarSystemID,
            solarSystemName,
            constellationID,
            regionID,
            security,
            x, y, z,
            radius
        FROM mapSolarSystems
        WHERE regionID = ?
    """
    
    df_systems = pd.read_sql_query(query, conn, params=(PURE_BLIND_REGION_ID,))
    
    # Get constellation names
    query_const = """
        SELECT constellationID, constellationName
        FROM mapConstellations
        WHERE regionID = ?
    """
    
    df_const = pd.read_sql_query(query_const, conn, params=(PURE_BLIND_REGION_ID,))
    
    # Merge constellation names
    df_systems = df_systems.merge(df_const, on='constellationID', how='left')
    
    conn.close()
    
    print(f"Found {len(df_systems)} systems in Pure Blind")
    return df_systems

def load_gate_connections(db_path):
    """
    Extract stargate connections within Pure Blind
    """
    print("Loading gate connections from SDE...")
    
    conn = sqlite3.connect(db_path)
    
    # Get internal Pure Blind connections
    query = """
        SELECT 
            s1.solarSystemName as fromSystem,
            s2.solarSystemName as toSystem,
            j.fromSolarSystemID,
            j.toSolarSystemID
        FROM mapSolarSystemJumps j
        JOIN mapSolarSystems s1 ON j.fromSolarSystemID = s1.solarSystemID
        JOIN mapSolarSystems s2 ON j.toSolarSystemID = s2.solarSystemID
        WHERE s1.regionID = ? AND s2.regionID = ?
    """
    
    df_gates = pd.read_sql_query(query, conn, 
                                  params=(PURE_BLIND_REGION_ID, PURE_BLIND_REGION_ID))
    
    # Also get cross-region connections (entry/exit points)
    query_border = """
        SELECT 
            s1.solarSystemName as fromSystem,
            s2.solarSystemName as toSystem,
            s2.regionID as toRegionID,
            r2.regionName as toRegionName
        FROM mapSolarSystemJumps j
        JOIN mapSolarSystems s1 ON j.fromSolarSystemID = s1.solarSystemID
        JOIN mapSolarSystems s2 ON j.toSolarSystemID = s2.solarSystemID
        JOIN mapRegions r2 ON s2.regionID = r2.regionID
        WHERE s1.regionID = ? AND s2.regionID != ?
    """
    
    df_border = pd.read_sql_query(query_border, conn,
                                   params=(PURE_BLIND_REGION_ID, PURE_BLIND_REGION_ID))
    
    conn.close()
    
    print(f"Found {len(df_gates)} internal gates")
    print(f"Found {len(df_border)} border gates to neighboring regions")
    
    return df_gates, df_border

# ============================================================================
# STEP 2: Merge with Your Spreadsheet Data
# ============================================================================

def merge_with_spreadsheet(df_sde, spreadsheet_path):
    """
    Merge SDE data with your existing spreadsheet
    """
    print("Merging with spreadsheet data...")
    
    df_sheet = pd.read_excel(spreadsheet_path)
    
    # Merge on system name
    df_merged = df_sde.merge(
        df_sheet,
        left_on='solarSystemName',
        right_on='System Name',
        how='left'
    )
    
    # Check for missing data
    missing = df_merged[df_merged['Power'].isna()]
    if len(missing) > 0:
        print(f"WARNING: {len(missing)} systems missing spreadsheet data:")
        print(missing['solarSystemName'].tolist())
    
    return df_merged

# ============================================================================
# STEP 3: Build NetworkX Graph
# ============================================================================

def build_graph(df_systems, df_gates):
    """
    Create NetworkX graph with all attributes
    """
    print("Building NetworkX graph...")
    
    G = nx.Graph()
    
    # Add nodes with attributes
    for _, row in df_systems.iterrows():
        G.add_node(
            row['solarSystemName'],
            system_id=int(row['solarSystemID']),
            constellation=row['constellationName'],
            constellation_id=int(row['constellationID']),
            security=float(row['security']),
            x=float(row['x']),
            y=float(row['y']),
            z=float(row['z']),
            # From spreadsheet (if available)
            power=int(row.get('Power', 0)) if pd.notna(row.get('Power')) else 0,
            workforce=int(row.get('Work Force', 0)) if pd.notna(row.get('Work Force')) else 0,
            has_ice=bool(row.get('Has Ice Belt') == 'TRUE') if pd.notna(row.get('Has Ice Belt')) else False,
            moons=int(row.get('Moons', 0)) if pd.notna(row.get('Moons')) else 0,
        )
    
    # Add edges (stargate connections)
    for _, row in df_gates.iterrows():
        G.add_edge(row['fromSystem'], row['toSystem'], edge_type='stargate')
    
    print(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Validate connectivity
    if nx.is_connected(G):
        print("✓ Graph is fully connected")
    else:
        print("✗ WARNING: Graph has disconnected components!")
        components = list(nx.connected_components(G))
        print(f"  Number of components: {len(components)}")
        for i, comp in enumerate(components):
            print(f"  Component {i+1}: {len(comp)} systems")
    
    return G

# ============================================================================
# STEP 4: Save Processed Data
# ============================================================================

def save_data(df_systems, df_gates, df_border, G, output_dir):
    """
    Save all data to disk for later use
    """
    print(f"Saving data to {output_dir}...")
    
    output_dir.mkdir(exist_ok=True)
    
    # Save DataFrames as CSV
    df_systems.to_csv(output_dir / "systems.csv", index=False)
    df_gates.to_csv(output_dir / "gates_internal.csv", index=False)
    df_border.to_csv(output_dir / "gates_border.csv", index=False)
    
    # Save graph as GraphML (can be loaded later)
    nx.write_graphml(G, output_dir / "pure_blind_graph.graphml")
    
    # Save graph as JSON (human-readable)
    graph_data = {
        'nodes': [
            {
                'name': node,
                **G.nodes[node]
            }
            for node in G.nodes()
        ],
        'edges': [
            {
                'from': u,
                'to': v,
                **G.edges[u, v]
            }
            for u, v in G.edges()
        ]
    }
    
    with open(output_dir / "pure_blind_graph.json", 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    # Save summary statistics
    stats = {
        'total_systems': G.number_of_nodes(),
        'total_gates': G.number_of_edges(),
        'constellations': df_systems['constellationName'].unique().tolist(),
        'avg_connections_per_system': 2 * G.number_of_edges() / G.number_of_nodes(),
        'network_diameter': nx.diameter(G) if nx.is_connected(G) else None,
        'total_power': int(df_systems['Power'].sum()) if 'Power' in df_systems else 0,
        'total_workforce': int(df_systems['Work Force'].sum()) if 'Work Force' in df_systems else 0,
        'ice_belt_systems': int(df_systems['Has Ice Belt'].sum()) if 'Has Ice Belt' in df_systems else 0,
    }
    
    with open(output_dir / "summary.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("✓ Data saved successfully")
    print(f"\nSummary:")
    print(f"  Systems: {stats['total_systems']}")
    print(f"  Gates: {stats['total_gates']}")
    print(f"  Avg connections/system: {stats['avg_connections_per_system']:.2f}")
    if stats['network_diameter']:
        print(f"  Network diameter: {stats['network_diameter']} jumps")

# ============================================================================
# STEP 5: Generate Initial Analysis
# ============================================================================

def initial_analysis(G):
    """
    Generate some initial network analysis
    """
    print("\n" + "="*70)
    print("INITIAL NETWORK ANALYSIS")
    print("="*70)
    
    # Find strategic chokepoints
    print("\n1. Strategic Chokepoints (Articulation Points)")
    chokepoints = list(nx.articulation_points(G))
    print(f"   Found {len(chokepoints)} critical systems:")
    for system in sorted(chokepoints)[:10]:  # Top 10
        print(f"   - {system}")
    
    # Find high-traffic systems
    print("\n2. High-Traffic Systems (Betweenness Centrality)")
    betweenness = nx.betweenness_centrality(G)
    top_traffic = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
    print("   Top 10 systems by traffic:")
    for system, score in top_traffic:
        print(f"   - {system}: {score:.3f}")
    
    # Find network center
    print("\n3. Network Center (Best Staging System)")
    center = nx.center(G)
    print(f"   Optimal staging systems: {', '.join(center)}")
    
    # Constellation connectivity
    print("\n4. Constellation Connectivity")
    constellations = {}
    for node in G.nodes():
        const = G.nodes[node]['constellation']
        if const not in constellations:
            constellations[const] = []
        constellations[const].append(node)
    
    print(f"   Total constellations: {len(constellations)}")
    for const, systems in sorted(constellations.items()):
        print(f"   - {const}: {len(systems)} systems")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run complete Phase 1 data acquisition
    """
    print("="*70)
    print("PHASE 1: DATA ACQUISITION FOR PURE BLIND")
    print("="*70)
    
    # Check if files exist
    if not Path(SDE_DATABASE).exists():
        print(f"\nERROR: SDE database not found at {SDE_DATABASE}")
        print("Download it from: https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2")
        print("Extract it and place it in this directory.")
        return
    
    if not Path(SPREADSHEET).exists():
        print(f"\nWARNING: Spreadsheet not found at {SPREADSHEET}")
        print("Continuing without power/workforce data...")
        use_spreadsheet = False
    else:
        use_spreadsheet = True
    
    # Step 1: Load from SDE
    df_systems = load_system_data_from_sde(SDE_DATABASE)
    df_gates, df_border = load_gate_connections(SDE_DATABASE)
    
    # Step 2: Merge with spreadsheet (if available)
    if use_spreadsheet:
        df_systems = merge_with_spreadsheet(df_systems, SPREADSHEET)
    
    # Step 3: Build graph
    G = build_graph(df_systems, df_gates)
    
    # Step 4: Save data
    save_data(df_systems, df_gates, df_border, G, OUTPUT_DIR)
    
    # Step 5: Initial analysis
    initial_analysis(G)
    
    print("\n" + "="*70)
    print("PHASE 1 COMPLETE!")
    print("="*70)
    print(f"\nData saved to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("1. Review the data in pure_blind_data/")
    print("2. Check summary.json for statistics")
    print("3. Move on to Phase 2 (Visualization)")
    print("\nTo load the graph later:")
    print("  import networkx as nx")
    print(f"  G = nx.read_graphml('{OUTPUT_DIR}/pure_blind_graph.graphml')")

if __name__ == "__main__":
    main()
