"""
Debug script to check database structure and Pure Blind data
"""
import sqlite3
import pandas as pd

SDE_PATH = "../data/sqlite-latest.sqlite"

print("="*70)
print("EVE SDE Database Debug Tool")
print("="*70)

try:
    conn = sqlite3.connect(SDE_PATH)
    print(f"\n✓ Connected to: {SDE_PATH}")

    # Check if Pure Blind exists in mapRegions
    print("\n1. Checking Pure Blind in mapRegions...")
    print("-"*70)
    query = """
    SELECT regionID, regionName
    FROM mapRegions
    WHERE regionName LIKE '%Pure%' OR regionName LIKE '%Blind%'
    """
    df = pd.read_sql_query(query, conn)
    if len(df) > 0:
        print(df.to_string(index=False))
        pure_blind_id = df[df['regionName'] == 'Pure Blind']['regionID'].values
        if len(pure_blind_id) > 0:
            region_id = pure_blind_id[0]
            print(f"\n✓ Pure Blind found with regionID: {region_id}")
        else:
            print("\n⚠ 'Pure Blind' exact match not found")
            if len(df) > 0:
                region_id = df.iloc[0]['regionID']
                print(f"Using first match: {df.iloc[0]['regionName']} (ID: {region_id})")
    else:
        print("❌ No regions matching 'Pure' or 'Blind' found!")
        conn.close()
        exit(1)

    # Check systems in that region
    print("\n2. Checking systems in Pure Blind...")
    print("-"*70)
    query_systems = """
    SELECT COUNT(*) as count
    FROM mapSolarSystems
    WHERE regionID = ?
    """
    df = pd.read_sql_query(query_systems, conn, params=(region_id,))
    system_count = df['count'].values[0]
    print(f"Systems with regionID {region_id}: {system_count}")

    if system_count == 0:
        print("\n⚠ No systems found! Checking if mapSolarSystems table exists...")

        # List all tables
        query_tables = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables = pd.read_sql_query(query_tables, conn)
        print(f"\nAvailable tables ({len(tables)}):")
        print(tables.to_string(index=False))

        # Check mapSolarSystems structure
        if 'mapSolarSystems' in tables['name'].values:
            print("\n3. Checking mapSolarSystems structure...")
            print("-"*70)
            query_cols = "PRAGMA table_info(mapSolarSystems)"
            cols = pd.read_sql_query(query_cols, conn)
            print(cols[['name', 'type']].to_string(index=False))

            # Check total systems
            query_total = "SELECT COUNT(*) as total FROM mapSolarSystems"
            total = pd.read_sql_query(query_total, conn)
            print(f"\nTotal systems in database: {total['total'].values[0]}")
    else:
        # Show sample systems
        print("\n3. Sample systems from Pure Blind:")
        print("-"*70)
        query_sample = """
        SELECT solarSystemID, solarSystemName, security
        FROM mapSolarSystems
        WHERE regionID = ?
        LIMIT 5
        """
        sample = pd.read_sql_query(query_sample, conn, params=(region_id,))
        print(sample.to_string(index=False))

    # Check mapConstellations
    print("\n4. Checking mapConstellations for Pure Blind...")
    print("-"*70)
    query_const = """
    SELECT COUNT(*) as count
    FROM mapConstellations
    WHERE regionID = ?
    """
    const_df = pd.read_sql_query(query_const, conn, params=(region_id,))
    print(f"Constellations with regionID {region_id}: {const_df['count'].values[0]}")

    conn.close()
    print("\n" + "="*70)
    print("Debug complete!")
    print("="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
