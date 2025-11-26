"""
Region Data Extractor
=====================

This script extracts ALL available data from Fuzzwork's SDE and creates
a clean data architecture with separated concerns:

1. systems_static.csv - All data from SDE (auto-generated)
2. systems_capacity.csv - Power/workforce (user-maintained)
3. systems_full.csv - Merged data (auto-generated)

Run: python region_data_extractor.py

Prerequisites:
- sqlite-latest.sqlite in ../data/ (download from https://www.fuzzwork.co.uk/dump/)
- pandas, networkx, openpyxl

Output: ../data/[region_name]_data/ directory with CSVs and graph files
"""

import sqlite3
import pandas as pd
import networkx as nx
import json
import re
from pathlib import Path

# Configuration
SDE_PATH = "../data/sqlite-latest.sqlite"


def get_available_regions(conn):
    """Query all available regions from the SDE database."""
    query = """
    SELECT
        regionID,
        regionName
    FROM mapRegions
    WHERE regionID < 11000000  -- Filter out wormhole regions
    ORDER BY regionName
    """
    df = pd.read_sql_query(query, conn)
    return df


def sanitize_folder_name(region_name):
    """Convert region name to a safe folder name."""
    # Convert to lowercase and replace spaces/special chars with underscores
    safe_name = re.sub(r'[^\w\s-]', '', region_name.lower())
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    return safe_name + "_data"


def extract_region_data(region_id, region_name, conn, base_output_dir):
    """Extract all data for a single region."""

    # Create output directory
    folder_name = sanitize_folder_name(region_name)
    OUTPUT_DIR = Path(base_output_dir) / folder_name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print(f"Extracting: {region_name}")
    print("="*70)

    # ========================================================================
    # STEP 1: Extract Static Data from SDE
    # ========================================================================

    print("\nStep 1: Extracting static data from Fuzzwork SDE...")
    print("-"*70)

    # Query 1: Get all systems with basic info
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
    WHERE mc.regionID = ?
    ORDER BY ms.solarSystemName
    """

    systems_df = pd.read_sql_query(query_systems, conn, params=(region_id,))

    if len(systems_df) == 0:
        print(f"⚠ No systems found in {region_name}, skipping...")
        return False

    print(f"✓ Found {len(systems_df)} systems in {region_name}")

    # Get system IDs for filtering celestial queries
    system_ids = tuple(systems_df['system_id'].tolist())

    # Query 2: Count moons per system
    query_moons = f"""
    SELECT
        solarSystemID as system_id,
        COUNT(*) as moons
    FROM mapDenormalize
    WHERE solarSystemID IN ({','.join('?' * len(system_ids))})
      AND groupID = 8  -- Moons are groupID 8
    GROUP BY solarSystemID
    """

    moons_df = pd.read_sql_query(query_moons, conn, params=system_ids)
    systems_df = systems_df.merge(moons_df, on='system_id', how='left')
    systems_df['moons'] = systems_df['moons'].fillna(0).astype(int)
    print(f"✓ Counted moons for all systems")

    # Query 3: Count planets per system
    query_planets = f"""
    SELECT
        solarSystemID as system_id,
        COUNT(*) as planets
    FROM mapDenormalize
    WHERE solarSystemID IN ({','.join('?' * len(system_ids))})
      AND groupID = 7  -- Planets are groupID 7
    GROUP BY solarSystemID
    """

    planets_df = pd.read_sql_query(query_planets, conn, params=system_ids)
    systems_df = systems_df.merge(planets_df, on='system_id', how='left')
    systems_df['planets'] = systems_df['planets'].fillna(0).astype(int)
    print(f"✓ Counted planets for all systems")

    # Query 4: Count asteroid belts per system
    query_belts = f"""
    SELECT
        solarSystemID as system_id,
        COUNT(*) as belts
    FROM mapDenormalize
    WHERE solarSystemID IN ({','.join('?' * len(system_ids))})
      AND groupID = 9  -- Asteroid belts are groupID 9
    GROUP BY solarSystemID
    """

    belts_df = pd.read_sql_query(query_belts, conn, params=system_ids)
    systems_df = systems_df.merge(belts_df, on='system_id', how='left')
    systems_df['belts'] = systems_df['belts'].fillna(0).astype(int)
    print(f"✓ Counted asteroid belts for all systems")

    # NOTE: Ice belt detection removed - now user-maintained in systems_capacity.csv
    # Ice belts are dynamic Cosmic Anomalies and cannot be reliably detected from SDE

    # Query 5: Get internal gates (within region)
    query_gates_internal = """
    SELECT DISTINCT
        msj.fromSolarSystemID as from_system_id,
        ms1.solarSystemName as from_system,
        msj.toSolarSystemID as to_system_id,
        ms2.solarSystemName as to_system
    FROM mapSolarSystemJumps msj
    JOIN mapSolarSystems ms1 ON msj.fromSolarSystemID = ms1.solarSystemID
    JOIN mapConstellations mc1 ON ms1.constellationID = mc1.constellationID
    JOIN mapSolarSystems ms2 ON msj.toSolarSystemID = ms2.solarSystemID
    JOIN mapConstellations mc2 ON ms2.constellationID = mc2.constellationID
    WHERE mc1.regionID = ?
      AND mc2.regionID = ?
    ORDER BY ms1.solarSystemName, ms2.solarSystemName
    """

    gates_internal = pd.read_sql_query(
        query_gates_internal,
        conn,
        params=(region_id, region_id)
    )
    print(f"✓ Found {len(gates_internal)} internal stargate connections")

    # Query 7: Get border gates (from region to other regions)
    query_gates_border = """
    SELECT DISTINCT
        msj.fromSolarSystemID as from_system_id,
        ms1.solarSystemName as from_system,
        msj.toSolarSystemID as to_system_id,
        ms2.solarSystemName as to_system,
        mr.regionName as to_region
    FROM mapSolarSystemJumps msj
    JOIN mapSolarSystems ms1 ON msj.fromSolarSystemID = ms1.solarSystemID
    JOIN mapConstellations mc1 ON ms1.constellationID = mc1.constellationID
    JOIN mapSolarSystems ms2 ON msj.toSolarSystemID = ms2.solarSystemID
    JOIN mapConstellations mc2 ON ms2.constellationID = mc2.constellationID
    JOIN mapRegions mr ON mc2.regionID = mr.regionID
    WHERE mc1.regionID = ?
      AND mc2.regionID != ?
    ORDER BY ms1.solarSystemName
    """

    gates_border = pd.read_sql_query(
        query_gates_border,
        conn,
        params=(region_id, region_id)
    )
    print(f"✓ Found {len(gates_border)} border gate connections")

    # ========================================================================
    # STEP 2: Create Capacity Data Template
    # ========================================================================

    print("\nStep 2: Creating capacity data template...")
    print("-"*70)

    # Create template with default capacity values
    capacity_df = systems_df[['system_name']].copy()
    capacity_df['power_capacity'] = 0  # User needs to fill this
    capacity_df['workforce_capacity'] = 0  # User needs to fill this
    capacity_df['has_ice'] = False  # User needs to fill this (ice belts are dynamic)
    print(f"✓ Created capacity template with {len(capacity_df)} systems")
    print("  ⚠ Power, workforce, and ice status set to default - edit systems_capacity.csv")

    # ========================================================================
    # STEP 3: Merge and Create Full Dataset
    # ========================================================================

    print("\nStep 3: Merging static and capacity data...")
    print("-"*70)

    # Merge systems with capacity
    systems_full = systems_df.merge(
        capacity_df,
        on='system_name',
        how='left'
    )

    # Fill any missing capacity with 0, has_ice with False
    systems_full['power_capacity'] = systems_full['power_capacity'].fillna(0).astype(int)
    systems_full['workforce_capacity'] = systems_full['workforce_capacity'].fillna(0).astype(int)
    systems_full['has_ice'] = systems_full['has_ice'].fillna(False).astype(bool)

    print(f"✓ Created full dataset with {len(systems_full)} systems")

    # ========================================================================
    # STEP 4: Build NetworkX Graph
    # ========================================================================

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
            if i <= 3:  # Only show first 3 components
                print(f"  Component {i}: {len(comp)} systems")

    # ========================================================================
    # STEP 5: Generate Analysis
    # ========================================================================

    print("\nStep 5: Generating network analysis...")
    print("-"*70)

    analysis = {}

    # Chokepoints (articulation points)
    chokepoints = list(nx.articulation_points(G))
    analysis['chokepoints'] = chokepoints
    print(f"✓ Found {len(chokepoints)} chokepoint systems")

    # High-traffic systems (betweenness centrality)
    betweenness = nx.betweenness_centrality(G)
    top_traffic = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
    analysis['high_traffic_systems'] = [sys for sys, _ in top_traffic]
    print(f"✓ Identified top 10 high-traffic systems")

    # Network center (closeness centrality)
    closeness = nx.closeness_centrality(G)
    network_center = max(closeness.items(), key=lambda x: x[1])
    analysis['network_center'] = network_center[0]
    print(f"✓ Network center: {network_center[0]}")

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
    print(f"✓ Analyzed {len(analysis['constellations'])} constellations")

    # ========================================================================
    # STEP 6: Save All Data
    # ========================================================================

    print("\nStep 6: Saving data files...")
    print("-"*70)

    # Save static data (from SDE only)
    systems_static_path = OUTPUT_DIR / "systems_static.csv"
    systems_df.to_csv(systems_static_path, index=False)
    print(f"✓ Saved: {systems_static_path}")

    # Save capacity data (user-maintained)
    capacity_path = OUTPUT_DIR / "systems_capacity.csv"
    capacity_df.to_csv(capacity_path, index=False)
    print(f"✓ Saved: {capacity_path}")

    # Save full merged data
    systems_full_path = OUTPUT_DIR / "systems_full.csv"
    systems_full.to_csv(systems_full_path, index=False)
    print(f"✓ Saved: {systems_full_path}")

    # Save gates
    gates_internal_path = OUTPUT_DIR / "gates_internal.csv"
    gates_internal.to_csv(gates_internal_path, index=False)
    print(f"✓ Saved: {gates_internal_path}")

    gates_border_path = OUTPUT_DIR / "gates_border.csv"
    gates_border.to_csv(gates_border_path, index=False)
    print(f"✓ Saved: {gates_border_path}")

    # Save graph (GraphML format)
    graph_name = sanitize_folder_name(region_name).replace('_data', '_graph')
    graph_path = OUTPUT_DIR / f"{graph_name}.graphml"
    nx.write_graphml(G, graph_path)
    print(f"✓ Saved: {graph_path}")

    # Save graph (JSON format - easier to read)
    graph_json_path = OUTPUT_DIR / f"{graph_name}.json"
    graph_data = nx.node_link_data(G)
    with open(graph_json_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
    print(f"✓ Saved: {graph_json_path}")

    # Save analysis summary
    summary_path = OUTPUT_DIR / "summary.json"

    # Get ice systems from user-maintained data
    ice_system_names = systems_full[systems_full['has_ice']]['system_name'].tolist()

    summary = {
        'region': region_name,
        'region_id': region_id,
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

    # ========================================================================
    # STEP 7: Create Data Source Documentation
    # ========================================================================

    readme_path = OUTPUT_DIR / "README.md"
    readme_content = f"""# {region_name} Region Data

## Data Files

### Auto-Generated (from Fuzzwork SDE)
- **systems_static.csv** - System data from SDE (name, coords, moons, planets, belts, etc.)
- **gates_internal.csv** - Internal stargate connections
- **gates_border.csv** - Border connections to adjacent regions
- **{graph_name}.graphml** - NetworkX graph (XML format)
- **{graph_name}.json** - NetworkX graph (JSON format)
- **summary.json** - Network analysis and statistics

### User-Maintained
- **systems_capacity.csv** - Power, workforce, and ice status per system
  - Power/workforce capacity based on Activity Defense Multiplier (ADM)
  - ADM changes based on in-system activity (mining, ratting)
  - Ice status (has_ice) - mark True for systems with ice belts
  - Ice belts are dynamic Cosmic Anomalies and cannot be auto-detected

### Merged Data
- **systems_full.csv** - Complete dataset (static + capacity)
  - This is regenerated when you run region_data_extractor.py
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
- **What it DOESN'T provide:**
  - Power/workforce capacity (activity-dependent)
  - Ice belt locations (now dynamic Cosmic Anomalies)
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
mv sqlite-latest.sqlite ../

# Regenerate (from Planning_docs directory)
cd ../../Planning_docs
python region_data_extractor.py
```

### Update Capacity and Ice Data
```bash
# Edit systems_capacity.csv manually
# Update power_capacity, workforce_capacity, and has_ice columns
# Or import from your alliance's data

# Regenerate full dataset (from Planning_docs directory)
cd ../../Planning_docs
python region_data_extractor.py
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

    print("\n✓ Extraction complete for " + region_name)
    return True


def main():
    """Main function with interactive region selection."""

    print("="*70)
    print("EVE Online - Region Data Extractor")
    print("="*70)

    # Check if SDE exists
    if not Path(SDE_PATH).exists():
        print(f"\n❌ ERROR: {SDE_PATH} not found!")
        print("\nDownload from: https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2")
        print("\nSteps:")
        print("  1. wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2")
        print("  2. bunzip2 sqlite-latest.sqlite.bz2")
        print("  3. mv sqlite-latest.sqlite ../data/")
        exit(1)

    # Connect to database
    print(f"\n✓ Found SDE database: {SDE_PATH}")
    conn = sqlite3.connect(SDE_PATH)

    # Get available regions
    print("\nQuerying available regions...")
    regions_df = get_available_regions(conn)

    print(f"\n✓ Found {len(regions_df)} regions in the database")

    # Display menu
    print("\n" + "="*70)
    print("SELECT REGION(S) TO EXTRACT")
    print("="*70)

    print("\n0. Extract ALL regions")
    print("-" * 70)

    # Display regions in columns
    for idx, row in regions_df.iterrows():
        print(f"{idx + 1:3d}. {row['regionName']}")

    print("="*70)

    # Get user input
    while True:
        try:
            choice = input("\nEnter your choice (0 for all, or region number): ").strip()

            if choice == '0':
                # Extract all regions
                print(f"\n✓ Extracting data for ALL {len(regions_df)} regions...")
                extracted_count = 0
                failed_regions = []

                for idx, row in regions_df.iterrows():
                    result = extract_region_data(
                        row['regionID'],
                        row['regionName'],
                        conn,
                        "../data"
                    )
                    if result:
                        extracted_count += 1
                    else:
                        failed_regions.append(row['regionName'])

                print("\n" + "="*70)
                print("BATCH EXTRACTION COMPLETE")
                print("="*70)
                print(f"\n✓ Successfully extracted: {extracted_count}/{len(regions_df)} regions")
                if failed_regions:
                    print(f"⚠ Skipped regions (no systems): {', '.join(failed_regions)}")
                break

            else:
                choice_num = int(choice)
                if 1 <= choice_num <= len(regions_df):
                    # Extract single region
                    region_row = regions_df.iloc[choice_num - 1]
                    extract_region_data(
                        region_row['regionID'],
                        region_row['regionName'],
                        conn,
                        "../data"
                    )

                    # Ask if user wants to extract another
                    another = input("\nExtract another region? (y/n): ").strip().lower()
                    if another != 'y':
                        break
                else:
                    print("❌ Invalid choice. Please enter a number from the list.")

        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n✓ Extraction cancelled by user.")
            break

    conn.close()

    print("\n" + "="*70)
    print("EXTRACTION SESSION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review systems_capacity.csv in each region folder")
    print("  2. Update power and workforce values based on your data")
    print("  3. Re-run this script to regenerate systems_full.csv")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
