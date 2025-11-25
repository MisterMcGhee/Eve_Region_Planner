"""
Data Source Investigation for Pure Blind Systems
=================================================

This script investigates what data is available from different sources:
1. Fuzzwork's SDE (Static Data Export)
2. ESI API (Eve Swagger Interface)  
3. Dotlan/third-party sources

Goal: Replace spreadsheet with programmatic data sources
"""

import sqlite3
import pandas as pd
import json

print("="*70)
print("DATA SOURCE INVESTIGATION")
print("="*70)

# ============================================================================
# 1. WHAT CAN WE GET FROM FUZZWORK SDE?
# ============================================================================

print("\n1. FUZZWORK SDE CAPABILITIES")
print("-" * 70)

# Note: This requires sqlite-latest.sqlite to be downloaded
# Download from: https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2

sde_available_tables = """
Available tables in Fuzzwork SDE:

KEY TABLES FOR US:
- mapSolarSystems: System name, ID, security, x/y/z coords, constellationID ✓
- mapSolarSystemJumps: All stargate connections ✓
- mapConstellations: Constellation names and IDs ✓
- mapRegions: Region names and IDs ✓
- mapDenormalize: Celestial objects (planets, moons, belts, stations) ✓

POTENTIALLY USEFUL:
- planetSchematics: Planet info (may help with planet count)
- invTypes: Item/object types
- staStations: NPC stations

NOT IN SDE:
- Power capacity ✗
- Workforce capacity ✗
- Ice belt presence (maybe derivable from belt types)
- Current sovereignty upgrades ✗
- Activity Defense Multiplier (ADM) ✗
"""

print(sde_available_tables)

# ============================================================================
# 2. WHAT CAN WE GET FROM ESI API?
# ============================================================================

print("\n2. ESI API CAPABILITIES")
print("-" * 70)

esi_endpoints = """
Eve Swagger Interface (ESI) - Live game data
Base URL: https://esi.evetech.net/latest/

RELEVANT ENDPOINTS:

/universe/systems/{system_id}/
  - Returns: name, security, constellationID, planets (array) ✓
  - Can get planet count programmatically ✓

/sovereignty/map/
  - Returns: List of all systems with sovereignty info
  - Includes: system_id, alliance_id, faction_id
  - Does NOT include power/workforce ✗

/sovereignty/structures/
  - Returns: Information about sovereignty structures
  - Includes: structure_id, structure_type_id, system_id
  - May include alliance_id but NOT capacity values ✗

/universe/types/{type_id}/
  - Can look up belt types, ice belt types
  - Ice Belt type IDs: 15 (Ice Belt), 16 (Ice Field)
  - This might help identify ice belts! ✓

LIMITATION: ESI does not provide power/workforce capacity values.
These appear to be derived from Activity Defense Multiplier (ADM) which
is calculated based on in-system activity (ratting, mining, etc.)
"""

print(esi_endpoints)

# ============================================================================
# 3. ICE BELT DETECTION
# ============================================================================

print("\n3. ICE BELT DETECTION")
print("-" * 70)

ice_detection = """
OPTIONS FOR DETECTING ICE BELTS:

Option A: Use SDE mapDenormalize table
- Query for celestialID entries where typeID = 15 (Ice Belt)
- Join on solarSystemID
- This should work! ✓

Option B: Use ESI /universe/systems/{system_id}/
- Returns planets array
- May not include belts (unconfirmed)

Option C: Use known list from community sources
- Dotlan shows ice belts (https://evemaps.dotlan.net/map/Pure_Blind)
- Can scrape or use known list as fallback

RECOMMENDATION: Try Option A (SDE), fallback to known list
"""

print(ice_detection)

# ============================================================================
# 4. POWER & WORKFORCE CAPACITY
# ============================================================================

print("\n4. POWER & WORKFORCE CAPACITY - THE PROBLEM")
print("-" * 70)

capacity_problem = """
ISSUE: These values are NOT in SDE or ESI API

WHERE THEY COME FROM:
- Based on Activity Defense Multiplier (ADM)
- ADM increases with system activity (ratting kills, mining, etc.)
- Higher ADM = more capacity
- Changes over time based on alliance activity

CURRENT STATE IN SPREADSHEET:
- Values appear to be manually collected
- Some systems have 0 (no sovereignty or no data collection)
- Values vary widely: 0 to 3200 (power), 0 to 30590 (workforce)

OPTIONS:

Option 1: Use ESI to get CURRENT sovereignty structures
  - Endpoint: /sovereignty/structures/
  - Returns what's currently installed
  - But NOT capacity, just what's being used
  
Option 2: Calculate based on ADM formula
  - ADM levels: 1.0 to 6.0
  - Formula: capacity = base_capacity × ADM_multiplier
  - Problem: Need current ADM values (not in ESI)
  
Option 3: Use reference values
  - Create lookup table of capacity per ADM level
  - Allow manual input/override
  - Most practical for planning tool ✓

Option 4: Assume max capacity (ADM 6.0)
  - For planning purposes, assume best-case scenario
  - Power: ~3000, Workforce: ~30000 (approximate max values)
  - Simple but not accurate for current state

RECOMMENDATION FOR YOUR TOOL:
Since this is a PLANNING tool (not a monitoring tool), use Option 3:
- Create a configuration file with ADM assumptions
- Default to reasonable values (e.g., ADM 4.0-5.0)
- Allow user to override per system
- Don't rely on live data that changes constantly

ALTERNATIVE: Make it user-configurable
- Provide a UI to set these values
- Or import from a CSV that alliance maintains
- This is actually what you're doing now with the spreadsheet!
"""

print(capacity_problem)

# ============================================================================
# 5. RECOMMENDED DATA ARCHITECTURE
# ============================================================================

print("\n5. RECOMMENDED DATA ARCHITECTURE")
print("-" * 70)

recommendation = """
TIERED DATA SOURCES:

TIER 1 - Static Game Data (Fuzzwork SDE)
✓ System names, IDs
✓ Coordinates (x, y, z)
✓ Security status
✓ Constellations, regions
✓ Stargate connections
✓ Moon counts (via mapDenormalize)
✓ Planet counts (via mapDenormalize)
✓ Ice belt detection (via mapDenormalize + typeID)

TIER 2 - Live API Data (ESI) [OPTIONAL]
✓ Current sovereignty holder (alliance)
✓ Installed structures
✓ System activity (kill stats)
- Real-time updates

TIER 3 - Alliance-Specific Data (Configuration File)
! Power capacity (per system)
! Workforce capacity (per system)
! Strategic classifications (staging, industrial, etc.)
! Existing Ansiblex bridges
! Current upgrade configurations
! Budget constraints

RECOMMENDED STRUCTURE:

pure_blind_data/
├── systems_static.csv        # From SDE (auto-generated)
│   ├── system_name
│   ├── system_id
│   ├── constellation
│   ├── security
│   ├── x, y, z
│   ├── moons (count)
│   ├── planets (count)
│   ├── belts (count)
│   └── has_ice (boolean)
│
├── systems_capacity.csv       # User-maintained or from ESI
│   ├── system_name
│   ├── power_capacity
│   └── workforce_capacity
│
└── systems_full.csv           # Merged (auto-generated)
    └── (all columns from above)

THIS APPROACH:
1. Auto-generates what CAN be automated (SDE data)
2. Keeps user-maintained data separate and updateable
3. Merges them for the tool to use
4. Clear separation of concerns
"""

print(recommendation)

# ============================================================================
# 6. EXAMPLE: Detecting Ice Belts from SDE
# ============================================================================

print("\n6. CODE EXAMPLE: Detecting Ice Belts from SDE")
print("-" * 70)

example_code = """
# Connect to Fuzzwork SDE
import sqlite3
conn = sqlite3.connect('sqlite-latest.sqlite')

# Query for ice belts in Pure Blind
query = \"\"\"
SELECT 
    ms.solarSystemName,
    ms.solarSystemID,
    COUNT(md.itemID) as ice_belt_count
FROM mapSolarSystems ms
LEFT JOIN mapDenormalize md ON ms.solarSystemID = md.solarSystemID
WHERE ms.regionID = 10000023  -- Pure Blind
  AND md.typeID = 15  -- Ice Belt type
GROUP BY ms.solarSystemName, ms.solarSystemID
HAVING ice_belt_count > 0
ORDER BY ms.solarSystemName
\"\"\"

ice_systems = pd.read_sql_query(query, conn)
print(f"Found {len(ice_systems)} systems with ice belts")

# This should match your spreadsheet's 12 ice systems:
# BDV3-T, D2-HOS, DK-FXK, KLY-C0, KQK1-2, KU5R-W, 
# MI6O-6, O-BY0Y, O-N8XZ, OE-9UF, R6XN-9, Y-C3EQ
"""

print(example_code)

# ============================================================================
# 7. ACTION ITEMS
# ============================================================================

print("\n7. ACTION ITEMS FOR YOU")
print("-" * 70)

action_items = """
TO MOVE AWAY FROM SPREADSHEET:

IMMEDIATE (Phase 1 Enhancement):
[ ] 1. Download Fuzzwork SDE if not already done
[ ] 2. Enhance phase1_quick_start.py to extract:
      - Ice belt detection from mapDenormalize
      - Moon counts from mapDenormalize  
      - Planet/belt counts from mapDenormalize
[ ] 3. Create systems_static.csv with all SDE data
[ ] 4. Create systems_capacity.csv for power/workforce
      - Copy from current spreadsheet
      - Document that this is user-maintained
[ ] 5. Merge into systems_full.csv

SHORT TERM (Phase 2):
[ ] 6. Add UI for editing capacity values
[ ] 7. Add import/export for capacity CSV
[ ] 8. Document data sources in README

OPTIONAL (Phase 5):
[ ] 9. Add ESI integration for live sovereignty data
[ ] 10. Add ADM-based capacity calculation
[ ] 11. Add automatic updates from ESI

CURRENT ANSWER TO YOUR QUESTION:
"Can we use only Fuzzwork data drops?"
- PARTIALLY: Yes for system info, coordinates, ice belts, moons
- NO: Not for power/workforce capacity (not in game data)
- SOLUTION: Keep capacity in separate CSV, merge at runtime
"""

print(action_items)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

summary = """
✓ Use Fuzzwork SDE for: systems, coords, ice, moons, planets, gates
✗ Cannot get from ANY source: power/workforce capacity
! Keep capacity data separate (user-maintained CSV)
! Merge at runtime for tool usage

This is actually BETTER for a planning tool because capacity changes
over time based on activity. A static config file is more appropriate
than trying to pull live data.
"""

print(summary)
