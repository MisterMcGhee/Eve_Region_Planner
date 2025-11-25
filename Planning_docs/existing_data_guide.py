"""
Guide: Using Existing Eve Online Network Data
==============================================

YES - there are excellent existing resources! You don't need to do data entry.
"""

# ============================================================================
# OPTION 1: FUZZWORK'S SDE CONVERSIONS (EASIEST - RECOMMENDED)
# ============================================================================

"""
Steve Ronuken (Fuzzwork) maintains pre-converted versions of CCP's Static 
Data Export (SDE) in multiple formats. This is the EASIEST way to get started.

Download link: https://www.fuzzwork.co.uk/dump/latest/

Available formats:
- SQLite (single file database - easiest to use)
- MySQL
- PostgreSQL  
- CSV files (individual tables)

KEY TABLE FOR JUMP GATES: mapSolarSystemJumps
- Columns: fromRegionID, fromConstellationID, fromSolarSystemID, toSolarSystemID, ...
- This table contains ALL stargate connections in New Eden
"""

# Example: Download and use the SQLite database
import urllib.request
import sqlite3
import networkx as nx

# Download the latest SQLite database (warning: ~130MB compressed)
print("Downloading Eve SDE SQLite database...")
url = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2"

# Note: In practice, download this manually and extract with:
# Linux: bunzip2 sqlite-latest.sqlite.bz2
# Windows: Use 7-Zip to extract

# Once extracted, connect to the database
db_path = "../data/sqlite-latest.sqlite"  # Path to your extracted database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ============================================================================
# BUILDING THE PURE BLIND NETWORK FROM SDE
# ============================================================================

# Get Pure Blind region ID
cursor.execute("SELECT regionID FROM mapRegions WHERE regionName = 'Pure Blind'")
pure_blind_region_id = cursor.fetchone()[0]
print(f"Pure Blind Region ID: {pure_blind_region_id}")

# Get all systems in Pure Blind
cursor.execute("""
    SELECT solarSystemID, solarSystemName, constellationID, security
    FROM mapSolarSystems
    WHERE regionID = ?
""", (pure_blind_region_id,))

systems = {}
for system_id, name, const_id, security in cursor.fetchall():
    systems[system_id] = {
        'name': name,
        'constellation_id': const_id,
        'security': security
    }

print(f"Found {len(systems)} systems in Pure Blind")

# Get all jump gate connections WITHIN Pure Blind
cursor.execute("""
    SELECT fromSolarSystemID, toSolarSystemID
    FROM mapSolarSystemJumps
    WHERE fromRegionID = ? AND toRegionID = ?
""", (pure_blind_region_id, pure_blind_region_id))

connections = cursor.fetchall()
print(f"Found {len(connections)} internal gate connections")

# Build NetworkX graph
G = nx.Graph()

# Add all systems as nodes with attributes
for system_id, data in systems.items():
    G.add_node(data['name'], 
               system_id=system_id,
               constellation_id=data['constellation_id'],
               security=data['security'])

# Add gate connections
for from_id, to_id in connections:
    if from_id in systems and to_id in systems:
        G.add_edge(systems[from_id]['name'], systems[to_id]['name'])

print(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Example: Find route from 5ZXX-K to EC-P8R
if nx.has_path(G, '5ZXX-K', 'EC-P8R'):
    route = nx.shortest_path(G, '5ZXX-K', 'EC-P8R')
    print(f"\nRoute: {' -> '.join(route)} ({len(route)-1} jumps)")

conn.close()

# ============================================================================
# OPTION 2: ESI API (FOR REAL-TIME DATA)
# ============================================================================

"""
Use CCP's official ESI API to get system and connection data.

Advantage: Always up-to-date
Disadvantage: Requires multiple API calls

Key endpoints:
- /universe/regions/10000023/ - Get Pure Blind constellation list
- /universe/constellations/{constellation_id}/ - Get systems in constellation
- /universe/systems/{system_id}/ - Get system details (including stargates)
- /universe/stargates/{stargate_id}/ - Get where stargate leads

API Base: https://esi.evetech.net/latest/
"""

import requests

def build_region_graph_from_esi(region_id):
    """Build graph using ESI API"""
    base_url = "https://esi.evetech.net/latest"
    
    # Get region info
    region = requests.get(f"{base_url}/universe/regions/{region_id}/").json()
    
    G = nx.Graph()
    
    # Get all constellations
    for const_id in region['constellations']:
        const = requests.get(f"{base_url}/universe/constellations/{const_id}/").json()
        
        # Get all systems in constellation
        for system_id in const['systems']:
            system = requests.get(f"{base_url}/universe/systems/{system_id}/").json()
            
            # Add system as node
            G.add_node(system['name'], 
                      system_id=system_id,
                      constellation_id=const_id,
                      security=system['security_status'])
            
            # Add stargate connections
            if 'stargates' in system:
                for stargate_id in system['stargates']:
                    gate = requests.get(f"{base_url}/universe/stargates/{stargate_id}/").json()
                    dest_system_id = gate['destination']['system_id']
                    
                    # Get destination system name
                    dest = requests.get(f"{base_url}/universe/systems/{dest_system_id}/").json()
                    
                    # Add edge (will automatically handle duplicates)
                    G.add_edge(system['name'], dest['name'])
    
    return G

# Example usage (commented out - takes ~5 minutes due to API rate limits):
# G = build_region_graph_from_esi(10000023)  # Pure Blind

# ============================================================================
# OPTION 3: PRE-BUILT PYTHON PACKAGES
# ============================================================================

"""
There are Python packages that wrap the SDE data:

1. eve-online-sde (npm/JavaScript)
   https://github.com/weswigham/eve-online-sde

2. Various community projects on GitHub with pre-processed data
"""

# ============================================================================
# OPTION 4: EXISTING GRAPH PROJECTS
# ============================================================================

"""
GitHub projects that have already done the heavy lifting:

1. eve-online-jump-distance
   https://github.com/li3097/eve-online-jump-distance
   - Has pre-built JSON adjacency maps
   
2. eve-route
   https://github.com/tkhamez/eve-route
   - Full route planning with jump gates and wormholes
   
3. shortcircuit
   https://github.com/secondfry/shortcircuit
   - Desktop app with full pathfinding using mapSolarSystemJumps
"""

# ============================================================================
# RECOMMENDED WORKFLOW FOR YOU
# ============================================================================

"""
For your Pure Blind analysis, I recommend:

1. Download Fuzzwork's SQLite database:
   https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
   
2. Extract it (bunzip2 on Linux, 7-Zip on Windows)

3. Query these key tables:
   - mapSolarSystems: System info (name, security, location)
   - mapSolarSystemJumps: Gate connections
   - mapConstellations: Constellation info
   - mapRegions: Region info
   
4. Build your NetworkX graph as shown above

5. Merge with your existing spreadsheet data using system names as keys

This gives you:
- All 85 Pure Blind systems
- All gate connections (graph edges)
- Ability to analyze routes, chokepoints, strategic importance
- Can merge with your power/workforce/ice belt data from the spreadsheet
"""

# ============================================================================
# QUICK START EXAMPLE
# ============================================================================

def quick_pure_blind_graph():
    """
    Complete example showing how to build Pure Blind graph from SQLite SDE
    """
    import sqlite3
    import networkx as nx
    
    # Connect to database
    conn = sqlite3.connect("../data/sqlite-latest.sqlite")
    cursor = conn.cursor()
    
    # Get Pure Blind systems and connections in one query
    cursor.execute("""
        SELECT 
            s.solarSystemName,
            j.toSolarSystemID,
            s2.solarSystemName as toSystemName
        FROM mapSolarSystems s
        JOIN mapSolarSystemJumps j ON s.solarSystemID = j.fromSolarSystemID
        JOIN mapSolarSystems s2 ON j.toSolarSystemID = s2.solarSystemID
        WHERE s.regionID = 10000023
    """)
    
    # Build graph
    G = nx.Graph()
    for from_sys, to_id, to_sys in cursor.fetchall():
        G.add_edge(from_sys, to_sys)
    
    conn.close()
    return G

# ============================================================================
# MERGING WITH YOUR SPREADSHEET DATA
# ============================================================================

def merge_spreadsheet_and_sde():
    """
    Combine your spreadsheet data with SDE network data
    """
    import pandas as pd
    import sqlite3
    import networkx as nx
    
    # Load your spreadsheet
    df = pd.read_excel('pure_blind_systems.xlsx')
    
    # Connect to SDE
    conn = sqlite3.connect("../data/sqlite-latest.sqlite")
    
    # Build graph with gate connections
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s1.solarSystemName, s2.solarSystemName
        FROM mapSolarSystemJumps j
        JOIN mapSolarSystems s1 ON j.fromSolarSystemID = s1.solarSystemID
        JOIN mapSolarSystems s2 ON j.toSolarSystemID = s2.solarSystemID
        WHERE s1.regionID = 10000023
    """)
    
    G = nx.Graph()
    for from_sys, to_sys in cursor.fetchall():
        G.add_edge(from_sys, to_sys)
    
    # Add your custom attributes from spreadsheet
    for _, row in df.iterrows():
        if row['System Name'] in G.nodes():
            G.nodes[row['System Name']]['power'] = row['Power']
            G.nodes[row['System Name']]['workforce'] = row['Work Force']
            G.nodes[row['System Name']]['has_ice'] = row['Has Ice Belt']
            G.nodes[row['System Name']]['moons'] = row['Moons']
    
    conn.close()
    return G

print("Guide complete! Download the Fuzzwork SQLite database to get started.")
print("URL: https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2")
