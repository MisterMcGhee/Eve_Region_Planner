"""
Enhanced debug to check constellation-based region lookup
"""
import sqlite3
import pandas as pd

SDE_PATH = "../data/sqlite-latest.sqlite"

print("="*70)
print("EVE SDE - Constellation Join Debug")
print("="*70)

conn = sqlite3.connect(SDE_PATH)

# Check Pure Blind region ID
print("\n1. Pure Blind Region ID:")
print("-"*70)
region_query = "SELECT regionID, regionName FROM mapRegions WHERE regionName = 'Pure Blind'"
region_df = pd.read_sql_query(region_query, conn)
print(region_df.to_string(index=False))
region_id = region_df['regionID'].values[0]

# Check constellations directly
print("\n2. Constellations in mapConstellations with regionID 10000023:")
print("-"*70)
const_query = "SELECT constellationID, constellationName, regionID FROM mapConstellations WHERE regionID = ?"
const_df = pd.read_sql_query(const_query, conn, params=(region_id,))
print(f"Found {len(const_df)} constellations")
if len(const_df) > 0:
    print(const_df.head().to_string(index=False))

# Check if systems have NULL regionID
print("\n3. Sample systems with NULL regionID:")
print("-"*70)
null_query = "SELECT solarSystemID, solarSystemName, regionID, constellationID FROM mapSolarSystems WHERE regionID IS NULL LIMIT 5"
null_df = pd.read_sql_query(null_query, conn)
print(f"Systems with NULL regionID: {len(null_df)}")
if len(null_df) > 0:
    print(null_df.to_string(index=False))

# Check regionID values that DO exist
print("\n4. Distinct regionID values in mapSolarSystems:")
print("-"*70)
regions_query = "SELECT DISTINCT regionID FROM mapSolarSystems WHERE regionID IS NOT NULL LIMIT 10"
regions_df = pd.read_sql_query(regions_query, conn)
print(f"Distinct regionIDs found: {len(regions_df)}")
print(regions_df.to_string(index=False))

# Try JOIN approach - systems through constellations
print("\n5. Systems via constellation JOIN (Pure Blind):")
print("-"*70)
join_query = """
SELECT
    ms.solarSystemID,
    ms.solarSystemName,
    ms.constellationID,
    mc.constellationName,
    mc.regionID
FROM mapSolarSystems ms
JOIN mapConstellations mc ON ms.constellationID = mc.constellationID
WHERE mc.regionID = ?
LIMIT 5
"""
join_df = pd.read_sql_query(join_query, conn, params=(region_id,))
print(f"Systems found via JOIN: {len(join_df)}")
if len(join_df) > 0:
    print(join_df.to_string(index=False))

# Count total via JOIN
print("\n6. Total Pure Blind systems via constellation JOIN:")
print("-"*70)
count_query = """
SELECT COUNT(*) as count
FROM mapSolarSystems ms
JOIN mapConstellations mc ON ms.constellationID = mc.constellationID
WHERE mc.regionID = ?
"""
count_df = pd.read_sql_query(count_query, conn, params=(region_id,))
print(f"Total systems: {count_df['count'].values[0]}")

conn.close()

print("\n" + "="*70)
print("Enhanced debug complete!")
print("="*70)
