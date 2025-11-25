"""
Pure Blind Data Acquisition - Enhanced Version
===============================================

This script extracts ALL available data from Fuzzwork's SDE and creates
a clean data architecture with separated concerns:

1. systems_static.csv - All data from SDE (auto-generated)
2. systems_capacity.csv - Power/workforce (user-maintained)
3. systems_full.csv - Merged data (auto-generated)

Run: python phase1_enhanced.py

Prerequisites:
- sqlite-latest.sqlite (download from https://www.fuzzwork.co.uk/dump/)
- pandas, networkx, openpyxl

Output: pure_blind_data/ directory with CSVs and graph files
"""

import sqlite3
import pandas as pd
import networkx as nx
import json
from pathlib import Path

# Configuration
REGION_ID = 10000023  # Pure Blind
REGION_NAME = "Pure Blind"
SDE_PATH = "../data/sqlite-latest.sqlite"  # Adjust if in different location
OUTPUT_DIR = Path("../data/pure_blind_data")
SPREADSHEET_PATH = "pure_blind_systems.xlsx"  # For extracting capacity data

# Ice Belt type IDs in Eve Online
ICE_BELT_TYPE_IDS = [15, 16]  # Ice Belt and Ice Field

print("="*70)
print("Pure Blind Data Acquisition - Enhanced Version")
print("="*70)

# ============================================================================
# STEP 1: Extract Static Data from SDE
# ============================================================================

print("\nStep 1: Extracting static data from Fuzzwork SDE...")
print("-"*70)

# Check if SDE exists
if not Path(SDE_PATH).exists():
    print(f"ERROR: {SDE_PATH} not found!")
    print("Download from: https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2")
    print("Then run: bunzip2 sqlite-latest.sqlite.bz2")
    exit(1)

conn = sqlite3.connect(SDE_PATH)

# Query 1: Get all Pure Blind systems with basic info
query_systems = """
SELECT 
    ms.solarSystemID as system_id,
    ms.solarSystemName as system_name,
    ms.constellationID as constellation_id,
    mc.constellationName as constellation,
    ms.security,
    ms.x,
    ms.y,
    ms.z
FROM mapSolarSystems ms
JOIN mapConstellations mc ON ms.constellationID = mc.constellationID
WHERE ms.regionID = ?
ORDER BY ms.solarSystemName
"""

systems_df = pd.read_sql_query(query_systems, conn, params=(REGION_ID,))
print(f"✓ Found {len(systems_df)} systems in {REGION_NAME}")

# Query 2: Count moons per system
query_moons = """
SELECT 
    solarSystemID as system_id,
    COUNT(*) as moons
FROM mapDenormalize
WHERE regionID = ?
  AND groupID = 8  -- Moons are groupID 8
GROUP BY solarSystemID
"""

moons_df = pd.read_sql_query(query_moons, conn, params=(REGION_ID,))
systems_df = systems_df.merge(moons_df, on='system_id', how='left')
systems_df['moons'] = systems_df['moons'].fillna(0).astype(int)
print(f"✓ Counted moons for all systems")

# Query 3: Count planets per system
query_planets = """
SELECT 
    solarSystemID as system_id,
    COUNT(*) as planets
FROM mapDenormalize
WHERE regionID = ?
  AND groupID = 7  -- Planets are groupID 7
GROUP BY solarSystemID
"""

planets_df = pd.read_sql_query(query_planets, conn, params=(REGION_ID,))
systems_df = systems_df.merge(planets_df, on='system_id', how='left')
systems_df['planets'] = systems_df['planets'].fillna(0).astype(int)
print(f"✓ Counted planets for all systems")

# Query 4: Count asteroid belts per system
query_belts = """
SELECT 
    solarSystemID as system_id,
    COUNT(*) as belts
FROM mapDenormalize
WHERE regionID = ?
  AND groupID = 9  -- Asteroid belts are groupID 9
GROUP BY solarSystemID
"""

belts_df = pd.read_sql_query(query_belts, conn, params=(REGION_ID,))
systems_df = systems_df.merge(belts_df, on='system_id', how='left')
systems_df['belts'] = systems_df['belts'].fillna(0).astype(int)
print(f"✓ Counted asteroid belts for all systems")

# Query 5: Detect ice belts
query_ice = """
SELECT DISTINCT
    solarSystemID as system_id
FROM mapDenormalize
WHERE regionID = ?
  AND typeID IN (?, ?)
"""

ice_df = pd.read_sql_query(query_ice, conn, params=(REGION_ID, *ICE_BELT_TYPE_IDS))
ice_systems = set(ice_df['system_id'].tolist())
systems_df['has_ice'] = systems_df['system_id'].isin(ice_systems)
print(f"✓ Detected {len(ice_systems)} systems with ice belts")

ice_system_names = systems_df[systems_df['has_ice']]['system_name'].tolist()
print(f"  Ice systems: {', '.join(sorted(ice_system_names))}")

# Query 6: Get internal gates (within Pure Blind)
query_gates_internal = """
SELECT DISTINCT
    msj.fromSolarSystemID as from_system_id,
    ms1.solarSystemName as from_system,
    msj.toSolarSystemID as to_system_id,
    ms2.solarSystemName as to_system
FROM mapSolarSystemJumps msj
JOIN mapSolarSystems ms1 ON msj.fromSolarSystemID = ms1.solarSystemID
JOIN mapSolarSystems ms2 ON msj.toSolarSystemID = ms2.solarSystemID
WHERE ms1.regionID = ? 
  AND ms2.regionID = ?
ORDER BY ms1.solarSystemName, ms2.solarSystemName
"""

gates_internal = pd.read_sql_query(
    query_gates_internal, 
    conn, 
    params=(REGION_ID, REGION_ID)
)
print(f"✓ Found {len(gates_internal)} internal stargate connections")

# Query 7: Get border gates (from Pure Blind to other regions)
query_gates_border = """
SELECT DISTINCT
    msj.fromSolarSystemID as from_system_id,
    ms1.solarSystemName as from_system,
    msj.toSolarSystemID as to_system_id,
    ms2.solarSystemName as to_system,
    mr.regionName as to_region
FROM mapSolarSystemJumps msj
JOIN mapSolarSystems ms1 ON msj.fromSolarSystemID = ms1.solarSystemID
JOIN mapSolarSystems ms2 ON msj.toSolarSystemID = ms2.solarSystemID
JOIN mapRegions mr ON ms2.regionID = mr.regionID
WHERE ms1.regionID = ?
  AND ms2.regionID != ?
ORDER BY ms1.solarSystemName
"""

gates_border = pd.read_sql_query(
    query_gates_border, 
    conn, 
    params=(REGION_ID, REGION_ID)
)
print(f"✓ Found {len(gates_border)} border gate connections")

conn.close()

# ============================================================================
# STEP 2: Extract Capacity Data from Spreadsheet
# ============================================================================

print("\nStep 2: Extracting capacity data from spreadsheet...")
print("-"*70)

if Path(SPREADSHEET_PATH).exists():
    xlsx_df = pd.read_excel(SPREADSHEET_PATH)
    
    # Create capacity dataframe
    capacity_df = xlsx_df[['System Name', 'Power', 'Work Force']].copy()
    capacity_df.columns = ['system_name', 'power_capacity', 'workforce_capacity']
    
    # Fill NaN with 0 (systems without data)
    capacity_df['power_capacity'] = capacity_df['power_capacity'].fillna(0).astype(int)
    capacity_df['workforce_capacity'] = capacity_df['workforce_capacity'].fillna(0).astype(int)
    
    print(f"✓ Extracted capacity data for {len(capacity_df)} systems")
    print(f"  Systems with capacity: {(capacity_df['power_capacity'] > 0).sum()}")
    
else:
    print("⚠ Spreadsheet not found, creating template with default values")
    # Create template with default capacity values
    capacity_df = systems_df[['system_name']].copy()
    capacity_df['power_capacity'] = 2500  # Reasonable default
    capacity_df['workforce_capacity'] = 18000  # Reasonable default
    print("  Using default values: 2500 power, 18000 workforce per system")

# ============================================================================
# STEP 3: Merge and Create Full Dataset
# ============================================================================

print("\nStep 3: Merging static and capacity data...")
print("-"*70)

# Merge systems with capacity
systems_full = systems_df.merge(
    capacity_df, 
    on='system_name', 
    how='left'
)

# Fill any missing capacity with 0
systems_full['power_capacity'] = systems_full['power_capacity'].fillna(0).astype(int)
systems_full['workforce_capacity'] = systems_full['workforce_capacity'].fillna(0).astype(int)

print(f"✓ Created full dataset with {len(systems_full)} systems")

# ============================================================================
# STEP 4: Build NetworkX Graph
# ============================================================================

print("\nStep 4: Building NetworkX graph...")
print("-"*70)

G = nx.Graph()

# Add nodes with all attributes
for _, row in systems_full.iterrows():
    G.add_node(
        row['system_name'],
        system_id=int(row['system_id']),
        constellation=row['constellation'],
        constellation_id=int(row['constellation_id']),
        security=float(row['security']),
        x=float(row['x']),
        y=float(row['y']),
        z=float(row['z']),
        power_capacity=int(row['power_capacity']),
        workforce_capacity=int(row['workforce_capacity']),
        has_ice=bool(row['has_ice']),
        moons=int(row['moons']),
        planets=int(row['planets']),
        belts=int(row['belts']),
    )

# Add edges (stargate connections)
for _, row in gates_internal.iterrows():
    G.add_edge(
        row['from_system'],
        row['to_system'],
        type='stargate'
    )

print(f"✓ Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Validate connectivity
if nx.is_connected(G):
    print("✓ Graph is fully connected")
else:
    print("⚠ WARNING: Graph has disconnected components")
    components = list(nx.connected_components(G))
    print(f"  Number of components: {len(components)}")
    for i, comp in enumerate(components, 1):
        print(f"  Component {i}: {len(comp)} systems")

# ============================================================================
# STEP 5: Generate Analysis
# ============================================================================

print("\nStep 5: Generating network analysis...")
print("-"*70)

analysis = {}

# Chokepoints (articulation points)
chokepoints = list(nx.articulation_points(G))
analysis['chokepoints'] = chokepoints
print(f"✓ Found {len(chokepoints)} chokepoint systems:")
for cp in sorted(chokepoints):
    print(f"  - {cp}")

# High-traffic systems (betweenness centrality)
betweenness = nx.betweenness_centrality(G)
top_traffic = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
analysis['high_traffic_systems'] = [sys for sys, _ in top_traffic]
print(f"✓ Top 10 high-traffic systems:")
for sys, score in top_traffic:
    print(f"  - {sys}: {score:.4f}")

# Network center (closeness centrality)
closeness = nx.closeness_centrality(G)
network_center = max(closeness.items(), key=lambda x: x[1])
analysis['network_center'] = network_center[0]
print(f"✓ Network center: {network_center[0]} (score: {network_center[1]:.4f})")

# Constellation connectivity
constellation_systems = {}
for node in G.nodes():
    const = G.nodes[node]['constellation']
    if const not in constellation_systems:
        constellation_systems[const] = []
    constellation_systems[const].append(node)

analysis['constellations'] = {
    const: len(systems) 
    for const, systems in constellation_systems.items()
}
print(f"✓ Systems per constellation:")
for const, count in sorted(analysis['constellations'].items()):
    print(f"  - {const}: {count} systems")

# ============================================================================
# STEP 6: Save All Data
# ============================================================================

print("\nStep 6: Saving data files...")
print("-"*70)

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# Save static data (from SDE only)
systems_static_path = OUTPUT_DIR / "systems_static.csv"
systems_df.to_csv(systems_static_path, index=False)
print(f"✓ Saved: {systems_static_path}")
print(f"  Columns: {', '.join(systems_df.columns)}")

# Save capacity data (user-maintained)
capacity_path = OUTPUT_DIR / "systems_capacity.csv"
capacity_df.to_csv(capacity_path, index=False)
print(f"✓ Saved: {capacity_path}")
print(f"  Columns: {', '.join(capacity_df.columns)}")

# Save full merged data
systems_full_path = OUTPUT_DIR / "systems_full.csv"
systems_full.to_csv(systems_full_path, index=False)
print(f"✓ Saved: {systems_full_path}")
print(f"  Columns: {', '.join(systems_full.columns)}")

# Save gates
gates_internal_path = OUTPUT_DIR / "gates_internal.csv"
gates_internal.to_csv(gates_internal_path, index=False)
print(f"✓ Saved: {gates_internal_path}")

gates_border_path = OUTPUT_DIR / "gates_border.csv"
gates_border.to_csv(gates_border_path, index=False)
print(f"✓ Saved: {gates_border_path}")

# Save graph (GraphML format)
graph_path = OUTPUT_DIR / "pure_blind_graph.graphml"
nx.write_graphml(G, graph_path)
print(f"✓ Saved: {graph_path}")

# Save graph (JSON format - easier to read)
graph_json_path = OUTPUT_DIR / "pure_blind_graph.json"
graph_data = nx.node_link_data(G)
with open(graph_json_path, 'w') as f:
    json.dump(graph_data, f, indent=2)
print(f"✓ Saved: {graph_json_path}")

# Save analysis summary
summary_path = OUTPUT_DIR / "summary.json"
summary = {
    'region': REGION_NAME,
    'region_id': REGION_ID,
    'total_systems': len(systems_full),
    'total_gates_internal': len(gates_internal),
    'total_gates_border': len(gates_border),
    'ice_systems': ice_system_names,
    'ice_system_count': len(ice_system_names),
    'analysis': {
        'chokepoints': chokepoints,
        'network_center': analysis['network_center'],
        'high_traffic_top5': [sys for sys, _ in top_traffic[:5]],
        'constellations': analysis['constellations'],
    },
    'network_metrics': {
        'diameter': nx.diameter(G) if nx.is_connected(G) else None,
        'average_path_length': nx.average_shortest_path_length(G) if nx.is_connected(G) else None,
        'density': nx.density(G),
    }
}

with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"✓ Saved: {summary_path}")

# ============================================================================
# STEP 7: Create Data Source Documentation
# ============================================================================

readme_path = OUTPUT_DIR / "README.md"
readme_content = f"""# Pure Blind Data - {REGION_NAME}

## Data Files

### Auto-Generated (from Fuzzwork SDE)
- **systems_static.csv** - System data from SDE (name, coords, ice, moons, etc.)
- **gates_internal.csv** - Internal stargate connections
- **gates_border.csv** - Border connections to adjacent regions
- **pure_blind_graph.graphml** - NetworkX graph (XML format)
- **pure_blind_graph.json** - NetworkX graph (JSON format)
- **summary.json** - Network analysis and statistics

### User-Maintained
- **systems_capacity.csv** - Power and workforce capacity per system
  - This file can be edited to update capacity values
  - These values are based on Activity Defense Multiplier (ADM)
  - ADM changes based on in-system activity (mining, ratting)

### Merged Data
- **systems_full.csv** - Complete dataset (static + capacity)
  - This is regenerated when you run phase1_enhanced.py
  - Use this file for the planning tool

## Data Sources

### Fuzzwork SDE
- **Source:** https://www.fuzzwork.co.uk/dump/
- **What it provides:**
  - System names, IDs, coordinates
  - Security status
  - Constellation/region membership
  - Stargate connections
  - Moon/planet/belt counts
  - Ice belt detection
- **What it DOESN'T provide:**
  - Power/workforce capacity (activity-dependent)
  - Current sovereignty holders
  - Existing upgrades

### ESI API (Optional)
- **Source:** https://esi.evetech.net/
- **Useful for:**
  - Current sovereignty status
  - Live structure data
  - Real-time activity metrics
- **Not currently used** (static planning tool)

## How to Update Data

### Update Static Data (from SDE)
```bash
# Download latest SDE
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
bunzip2 sqlite-latest.sqlite.bz2

# Regenerate
python phase1_enhanced.py
```

### Update Capacity Data
```bash
# Edit systems_capacity.csv manually
# Or import from your alliance's data

# Regenerate full dataset
python phase1_enhanced.py
```

## Statistics

- **Total Systems:** {len(systems_full)}
- **Internal Gates:** {len(gates_internal)}
- **Border Gates:** {len(gates_border)}
- **Ice Systems:** {len(ice_system_names)}
- **Constellations:** {len(analysis['constellations'])}

## Network Analysis

- **Chokepoints:** {len(chokepoints)}
- **Network Center:** {analysis['network_center']}
- **Diameter:** {nx.diameter(G) if nx.is_connected(G) else 'N/A (disconnected)'}

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

with open(readme_path, 'w') as f:
    f.write(readme_content)
print(f"✓ Saved: {readme_path}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*70)
print("DATA ACQUISITION COMPLETE")
print("="*70)
print(f"\nOutput directory: {OUTPUT_DIR}/")
print(f"\nGenerated files:")
print(f"  - systems_static.csv (SDE data)")
print(f"  - systems_capacity.csv (user-maintained)")
print(f"  - systems_full.csv (merged)")
print(f"  - gates_internal.csv")
print(f"  - gates_border.csv")
print(f"  - pure_blind_graph.graphml")
print(f"  - pure_blind_graph.json")
print(f"  - summary.json")
print(f"  - README.md")

print(f"\nNext steps:")
print(f"  1. Review systems_capacity.csv and update as needed")
print(f"  2. Run python phase2_visualization.py to visualize")
print(f"  3. Run python dash_app_starter.py to launch the tool")

print("\n" + "="*70)
