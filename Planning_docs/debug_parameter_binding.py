"""
Advanced debug - Check data types and query parameter matching
"""
import sqlite3
import pandas as pd

SDE_PATH = "../data/sqlite-latest.sqlite"

print("="*70)
print("Data Type & Parameter Binding Debug")
print("="*70)

conn = sqlite3.connect(SDE_PATH)

# Get Pure Blind from mapRegions
print("\n1. Query Pure Blind from mapRegions:")
print("-"*70)
region_query = "SELECT regionID, regionName, typeof(regionID) as regionID_type FROM mapRegions WHERE regionName = 'Pure Blind'"
region_df = pd.read_sql_query(region_query, conn)
print(region_df.to_string(index=False))

region_id = region_df['regionID'].values[0]
print(f"\nPython type of region_id: {type(region_id)}")
print(f"Python value: {region_id}")

# Check actual data in mapSolarSystems
print("\n2. Direct query - no parameters (should work):")
print("-"*70)
direct_query = "SELECT COUNT(*) as count, typeof(regionID) as regionID_type FROM mapSolarSystems WHERE regionID = 10000023"
direct_df = pd.read_sql_query(direct_query, conn)
print(direct_df.to_string(index=False))

# Check with parameter binding (current approach)
print("\n3. Query with parameter binding (current approach):")
print("-"*70)
param_query = "SELECT COUNT(*) as count FROM mapSolarSystems WHERE regionID = ?"
param_df = pd.read_sql_query(param_query, conn, params=(region_id,))
print(f"Count with params=(region_id,): {param_df['count'].values[0]}")

# Try with explicit int conversion
print("\n4. Query with explicit int conversion:")
print("-"*70)
int_df = pd.read_sql_query(param_query, conn, params=(int(region_id),))
print(f"Count with params=(int(region_id),): {int_df['count'].values[0]}")

# Try with string conversion
print("\n5. Query with string conversion:")
print("-"*70)
str_df = pd.read_sql_query(param_query, conn, params=(str(region_id),))
print(f"Count with params=(str(region_id),): {str_df['count'].values[0]}")

# Check sample systems to see their regionID type
print("\n6. Sample systems with their regionID types:")
print("-"*70)
sample_query = """
SELECT
    solarSystemID,
    solarSystemName,
    regionID,
    typeof(regionID) as regionID_type
FROM mapSolarSystems
WHERE regionID = 10000023
LIMIT 5
"""
sample_df = pd.read_sql_query(sample_query, conn)
print(sample_df.to_string(index=False))

# Check if constellation approach works
print("\n7. Query via constellation JOIN (new approach):")
print("-"*70)
join_query = """
SELECT COUNT(*) as count
FROM mapSolarSystems ms
JOIN mapConstellations mc ON ms.constellationID = mc.constellationID
WHERE mc.regionID = ?
"""
join_df = pd.read_sql_query(join_query, conn, params=(region_id,))
print(f"Count via constellation JOIN: {join_df['count'].values[0]}")

# Check constellation regionID types
print("\n8. Constellation regionID types:")
print("-"*70)
const_type_query = """
SELECT
    constellationID,
    constellationName,
    regionID,
    typeof(regionID) as regionID_type
FROM mapConstellations
WHERE regionID = 10000023
LIMIT 3
"""
const_type_df = pd.read_sql_query(const_type_query, conn)
print(const_type_df.to_string(index=False))

conn.close()

print("\n" + "="*70)
print("Debug complete!")
print("="*70)
print("\nSUMMARY:")
print("If direct query works but parameter binding fails, it's a type mismatch.")
print("If constellation JOIN works, we can use that approach instead.")
